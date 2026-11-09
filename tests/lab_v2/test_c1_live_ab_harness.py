"""Slice C1: freno de presupuesto, payload Gemini y tombstones de parches rechazados."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from ddi_fw.lab_v2.context_compiler import compile_session_context
from ddi_fw.lab_v2.live_ab_harness import (
    BudgetGuard,
    GeminiLiveClient,
    load_live_config,
    messages_to_gemini_payload,
)

_TOMBSTONE = "[DDI-TOMBSTONE: parche rechazado en revisión previa; ver Memoria Negativa]"


def _ok(prompt_tokens: int = 12, output_tokens: int = 1, text: str = "ok") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "candidates": [{"content": {"parts": [{"text": text}]}}],
            "usageMetadata": {
                "promptTokenCount": prompt_tokens,
                "candidatesTokenCount": output_tokens,
            },
        },
    )


def test_call_21_raises_before_the_network_after_twenty_successes() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _ok()

    guard = BudgetGuard()
    client = GeminiLiveClient(
        "test-key",
        "gemini-2.5-flash",
        guard,
        transport=httpx.MockTransport(handler),
        sleep_fn=lambda _seconds: None,
    )
    messages = [{"role": "user", "content": "hola"}]
    try:
        for _ in range(20):
            client.generate(messages, estimated_tokens=12)
        with pytest.raises(RuntimeError, match="HARD_BUDGET_EXCEEDED"):
            client.generate(messages, estimated_tokens=12)
    finally:
        client.close()
    assert len(seen) == 20
    assert guard.successful_calls == 20


def test_token_budget_blocks_before_any_request() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _ok()

    client = GeminiLiveClient(
        "test-key",
        "gemini-2.5-flash",
        BudgetGuard(),
        transport=httpx.MockTransport(handler),
        sleep_fn=lambda _seconds: None,
    )
    try:
        with pytest.raises(RuntimeError, match="HARD_BUDGET_EXCEEDED"):
            client.generate([{"role": "user", "content": "hola"}], estimated_tokens=3_500_001)
    finally:
        client.close()
    assert seen == []


def test_payload_merges_roles_keeps_final_user_and_disables_flash_thinking() -> None:
    messages = [
        {"role": "system", "content": "sistema uno"},
        {"role": "user", "content": "u1"},
        {"role": "user", "content": "u2"},
        {"role": "assistant", "content": "a1"},
        {"role": "assistant", "content": "a2"},
        {"role": "system", "content": "[DDI-CONTEXT-GOVERNOR]\nfirmas vivas"},
        {"role": "user", "content": "consigna final exacta"},
    ]
    payload = messages_to_gemini_payload(messages, "gemini-2.5-flash")
    instruction = payload["systemInstruction"]
    assert isinstance(instruction, dict)
    assert instruction["parts"] == [{"text": "sistema uno\n\n[DDI-CONTEXT-GOVERNOR]\nfirmas vivas"}]
    contents = payload["contents"]
    assert isinstance(contents, list)
    roles = [item["role"] for item in contents]
    assert roles == ["user", "model", "user"]
    assert all(roles[index] != roles[index + 1] for index in range(len(roles) - 1))
    assert contents[0]["parts"] == [{"text": "u1\n\nu2"}]
    assert contents[-1]["parts"] == [{"text": "consigna final exacta"}]
    generation = payload["generationConfig"]
    assert isinstance(generation, dict)
    assert generation["temperature"] == 0.0
    assert generation["maxOutputTokens"] == 2048
    assert generation["thinkingConfig"] == {"thinkingBudget": 0}
    plain = messages_to_gemini_payload(messages, "gemini-2.5-pro")
    plain_gen = plain["generationConfig"]
    assert isinstance(plain_gen, dict)
    assert "thinkingConfig" not in plain_gen


def test_leading_model_turn_gets_a_user_preamble() -> None:
    payload = messages_to_gemini_payload(
        [
            {"role": "assistant", "content": "arranque"},
            {"role": "user", "content": "cierre"},
        ],
        "gemini-2.5-flash",
    )
    contents = payload["contents"]
    assert isinstance(contents, list)
    assert contents[0]["parts"] == [{"text": "[Inicio de registro de sesión]"}]
    assert contents[-1]["role"] == "user"


def test_http_429_then_200_sleeps_without_counting_the_failure() -> None:
    sleeps: list[float] = []
    seen: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        del request
        seen.append(1)
        if len(seen) == 1:
            return httpx.Response(429, json={"error": {"message": "rate limit"}})
        return _ok(prompt_tokens=40, output_tokens=3, text="respuesta")

    guard = BudgetGuard()
    client = GeminiLiveClient(
        "test-key",
        "gemini-2.5-flash",
        guard,
        transport=httpx.MockTransport(handler),
        sleep_fn=sleeps.append,
    )
    try:
        result = client.generate([{"role": "user", "content": "hola"}], estimated_tokens=40)
    finally:
        client.close()
    assert sleeps == [35.0]
    assert result.text == "respuesta"
    assert result.prompt_tokens == 40
    assert result.output_tokens == 3
    assert guard.successful_calls == 1
    assert guard.http_attempts == 2
    assert guard.accumulated_input_tokens == 40


def test_http_400_error_never_echoes_the_api_key() -> None:
    secret = "super-secret-key"

    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(400, json={"error": {"message": f"bad {secret}"}})

    client = GeminiLiveClient(
        secret,
        "gemini-2.5-flash",
        BudgetGuard(),
        transport=httpx.MockTransport(handler),
        sleep_fn=lambda _seconds: None,
    )
    try:
        with pytest.raises(RuntimeError, match="HTTP 400") as caught:
            client.generate([{"role": "user", "content": "hola"}], estimated_tokens=8)
    finally:
        client.close()
    assert secret not in str(caught.value)
    assert "[REDACTED]" in str(caught.value)


def test_heavy_call_paces_the_following_request() -> None:
    sleeps: list[float] = []
    seen: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        del request
        seen.append(1)
        tokens = 100_000 if len(seen) == 1 else 20
        return _ok(prompt_tokens=tokens)

    client = GeminiLiveClient(
        "test-key",
        "gemini-2.5-flash",
        BudgetGuard(),
        transport=httpx.MockTransport(handler),
        sleep_fn=sleeps.append,
        heavy_call_pacing_s=18.0,
    )
    messages = [{"role": "user", "content": "hola"}]
    try:
        client.generate(messages, estimated_tokens=100_000)
        client.generate(messages, estimated_tokens=20)
    finally:
        client.close()
    assert sleeps == [18.0]


def test_rejected_late_patch_is_tombstoned_and_does_not_bury_the_accepted_def() -> None:
    accepted = "def calcular_total(centavos, tasa_bps):\n    return centavos\n"
    rejected = "def calcular_total(centavos, tasa_bps, extra):\n    return centavos + extra\n"
    messages = [
        {"role": "system", "content": "INVARIANTE: enteros"},
        {"role": "user", "content": "mantener calcular_total aceptada"},
        {"role": "assistant", "content": f"```python\n{accepted}```\n"},
        {"role": "assistant", "content": f"```python\n{rejected}```\n"},
        {"role": "user", "content": "rechazo el parche"},
    ]
    result = compile_session_context(
        messages,
        rejected_turn_indices={3},
        max_budget_tokens=36000,
        fresh_tail_turns=1,
        force_hygiene=True,
    )
    joined = "\n".join(message["content"] for message in result.messages)
    assert _TOMBSTONE in joined
    assert "def calcular_total(centavos, tasa_bps):" in joined
    assert "return centavos + extra" not in joined
    assert result.superseded_blocks_pruned == 1


def test_load_live_config_prefers_env_and_does_not_require_the_real_secret(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    for name in ("DDI_LIVE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "DDI_LIVE_MODEL"):
        monkeypatch.delenv(name, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# comentario",
                "GOOGLE_API_KEY='desde-archivo'",
                "DDI_LIVE_MODEL=\"modelo-de-prueba\"",
                "",
            ]
        ),
        encoding="utf-8",
    )
    from_file = load_live_config(env_file)
    assert from_file.api_key == "desde-archivo"
    assert from_file.key_name == "GOOGLE_API_KEY"
    assert from_file.model == "modelo-de-prueba"
    assert "desde-archivo" not in repr(from_file)
    monkeypatch.setenv("DDI_LIVE_API_KEY", "desde-entorno")
    from_env = load_live_config(env_file)
    assert from_env.api_key == "desde-entorno"
    assert from_env.key_name == "DDI_LIVE_API_KEY"
    monkeypatch.delenv("DDI_LIVE_API_KEY", raising=False)
    empty = tmp_path / "empty.env"
    empty.write_text("OTRA=1\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="MISSING_LIVE_API_KEY"):
        load_live_config(empty)

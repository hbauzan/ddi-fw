"""Cliente Gemini con freno de presupuesto para el duelo A/B vivo."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import httpx

_KEY_NAMES = ("DDI_LIVE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY")
_DEFAULT_MODEL = "gemini-2.5-flash"
_RETRY_DELAYS_S = (35.0, 65.0)
_HEAVY_INPUT_TOKENS = 100_000


@dataclass
class LiveApiConfig:
    api_key: str
    model: str
    key_name: str

    def __repr__(self) -> str:
        return f"LiveApiConfig(model={self.model!r}, key_name={self.key_name!r})"


@dataclass
class BudgetGuard:
    max_successful_calls: int = 20
    max_total_http_attempts: int = 35
    max_input_tokens: int = 3_500_000
    successful_calls: int = 0
    http_attempts: int = 0
    accumulated_input_tokens: int = 0

    def check_before_call(self, estimated_tokens: int) -> None:
        if estimated_tokens < 0:
            raise ValueError("estimated_tokens negativo")
        exceeded = (
            self.successful_calls >= self.max_successful_calls
            or self.http_attempts >= self.max_total_http_attempts
            or self.accumulated_input_tokens + estimated_tokens > self.max_input_tokens
        )
        if exceeded:
            raise RuntimeError("HARD_BUDGET_EXCEEDED")


@dataclass(frozen=True)
class LiveCompletion:
    text: str
    prompt_tokens: int
    output_tokens: int
    latency_ms: float


def load_live_config(env_path: Path | None = None) -> LiveApiConfig:
    """Lee la clave sin pisar variables ya presentes y sin incluirla en ``repr``."""
    path = _repo_root() / ".env" if env_path is None else env_path
    merged: dict[str, str] = _parse_env_file(path) if path.is_file() else {}
    for name, value in os.environ.items():
        if value.strip():
            merged[name] = value.strip()
    api_key = ""
    key_name = ""
    for name in _KEY_NAMES:
        candidate = merged.get(name, "").strip()
        if candidate:
            api_key = candidate
            key_name = name
            break
    if not api_key:
        raise RuntimeError("MISSING_LIVE_API_KEY")
    model = merged.get("DDI_LIVE_MODEL", "").strip() or _DEFAULT_MODEL
    return LiveApiConfig(api_key=api_key, model=model, key_name=key_name)


def messages_to_gemini_payload(
    messages: list[dict[str, str]],
    model: str,
) -> dict[str, object]:
    systems = [message.get("content", "") for message in messages if message.get("role") == "system"]
    contents: list[dict[str, object]] = []
    for message in messages:
        if message.get("role") == "system":
            continue
        role = "model" if message.get("role") == "assistant" else "user"
        text = message.get("content", "")
        if contents and contents[-1]["role"] == role:
            part = contents[-1]["parts"]
            if isinstance(part, list) and part and isinstance(part[0], dict):
                part[0]["text"] = str(part[0].get("text", "")) + "\n\n" + text
            continue
        contents.append({"role": role, "parts": [{"text": text}]})
    if contents and contents[0]["role"] == "model":
        contents.insert(0, {"role": "user", "parts": [{"text": "[Inicio de registro de sesión]"}]})
    if not contents or contents[-1]["role"] != "user":
        raise ValueError("el ultimo contenido debe tener rol user")
    gen_cfg: dict[str, object] = {
        "temperature": 0.0,
        "maxOutputTokens": 2048,
    }
    if "flash" in model.lower():
        gen_cfg["thinkingConfig"] = {"thinkingBudget": 0}
    payload: dict[str, object] = {"contents": contents, "generationConfig": gen_cfg}
    if systems:
        payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(systems)}]}
    return payload


class GeminiLiveClient:
    """Cliente sincrónico. El freno corre antes de cada intento HTTP."""

    def __init__(
        self,
        api_key: str,
        model: str,
        guard: BudgetGuard,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
        heavy_call_pacing_s: float = 18.0,
        timeout_s: float = 180.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._guard = guard
        self._sleep_fn = sleep_fn
        self._heavy_call_pacing_s = heavy_call_pacing_s
        self._previous_input_tokens = 0
        self._url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )
        self._client = httpx.Client(transport=transport, timeout=timeout_s)

    def close(self) -> None:
        self._client.close()

    def generate(
        self,
        messages: list[dict[str, str]],
        estimated_tokens: int,
    ) -> LiveCompletion:
        self._guard.check_before_call(estimated_tokens)
        if self._previous_input_tokens >= _HEAVY_INPUT_TOKENS:
            self._sleep_fn(self._heavy_call_pacing_s)
        payload = messages_to_gemini_payload(messages, self._model)
        headers = {"x-goog-api-key": self._api_key}
        retry_index = 0
        while True:
            self._guard.check_before_call(estimated_tokens)
            self._guard.http_attempts += 1
            started = time.perf_counter()
            try:
                response = self._client.post(self._url, headers=headers, json=payload)
            except httpx.HTTPError as exc:
                raise RuntimeError(f"HTTP transport error: {type(exc).__name__}") from None
            if response.status_code in (429, 503):
                if retry_index >= len(_RETRY_DELAYS_S):
                    raise RuntimeError(_sanitize_error(response, self._api_key))
                self._sleep_fn(_RETRY_DELAYS_S[retry_index])
                retry_index += 1
                continue
            if response.status_code != 200:
                raise RuntimeError(_sanitize_error(response, self._api_key))
            latency_ms = (time.perf_counter() - started) * 1000.0
            return self._consume_success(response, estimated_tokens, latency_ms)

    def _consume_success(
        self,
        response: httpx.Response,
        estimated_tokens: int,
        latency_ms: float,
    ) -> LiveCompletion:
        try:
            data = response.json()
        except ValueError:
            raise RuntimeError("HTTP 200: cuerpo JSON invalido") from None
        if not isinstance(data, dict):
            raise RuntimeError("HTTP 200: cuerpo JSON invalido")
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates or not isinstance(candidates[0], dict):
            raise RuntimeError("HTTP 200: sin candidates")
        content = candidates[0].get("content")
        parts = content.get("parts") if isinstance(content, dict) else None
        texts: list[str] = []
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    texts.append(str(part.get("text", "")))
        usage = data.get("usageMetadata")
        if isinstance(usage, dict) and "promptTokenCount" in usage:
            prompt_tokens = int(usage["promptTokenCount"])
        else:
            prompt_tokens = int(estimated_tokens)
        if isinstance(usage, dict) and "candidatesTokenCount" in usage:
            output_tokens = int(usage["candidatesTokenCount"])
        else:
            output_tokens = 0
        self._guard.successful_calls += 1
        self._guard.accumulated_input_tokens += prompt_tokens
        self._previous_input_tokens = prompt_tokens
        return LiveCompletion(
            text="".join(texts),
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            latency_ms=float(latency_ms),
        )


def _sanitize_error(response: httpx.Response, api_key: str) -> str:
    try:
        body = response.text
    except httpx.HTTPError:
        body = ""
    if api_key:
        body = body.replace(api_key, "[REDACTED]")
    collapsed = " ".join(body.split())
    return f"HTTP {response.status_code}: {collapsed[:300]}"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _parse_env_file(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip().removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if name:
            parsed[name] = value
    return parsed


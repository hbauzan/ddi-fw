"""Slice B3: una sesión de 260k tokens cabe en el presupuesto y conserva el contrato."""

from __future__ import annotations

import time

from ddi_fw.lab_v2.ast_symbol_index import LiveSymbolIndex, extract_python_blocks
from ddi_fw.lab_v2.context_compiler import compile_session_context, estimate_tokens

_INVARIANT = "INVARIANTE-LIQUIDACION-CENTAVOS: el modulo no puede perder centavos."
_OLD = "def liquidar_orden(monto, tasa):\n    return monto * tasa\n"
_MID = "def liquidar_orden(monto, tasa, moneda):\n    return int(monto * tasa)\n"
_LIVE = (
    "def liquidar_orden(centavos: int, bps_impuesto: int, moneda: str) -> int:\n"
    "    return centavos + (centavos * bps_impuesto) // 10000\n"
)


def _trace(index: int) -> str:
    lines = ["Traceback (most recent call last):"]
    for frame in range(8):
        lines.append(f'  File "old_{index}.py", line {frame}, in liquidar')
        lines.append("    liquidar_orden(monto, tasa)")
    lines.append("ValueError: firma vieja")
    return "\n".join(lines)


def _session() -> list[dict[str, str]]:
    filler_unit = "FAILED tests/test_liquidacion.py::test_centavos - AssertionError: esperado 1050 obtenido 1049\n"
    messages: list[dict[str, str]] = [
        {"role": "system", "content": _INVARIANT},
        {"role": "user", "content": "Implementa liquidar_orden en centavos enteros y no cambies el objetivo."},
        {"role": "assistant", "content": f"```python\n{_OLD}```\n"},
        {"role": "assistant", "content": f"```python\n{_MID}```\n"},
    ]
    target_chars = 260_000 * 4
    messages.append({"role": "user", "content": filler_unit * ((target_chars // len(filler_unit)) + 1)})
    for index in range(40):
        messages.append({"role": "user", "content": _trace(index)})
    messages.append({"role": "assistant", "content": f"```python\n{_LIVE}```\n"})
    for index in range(5):
        messages.append({"role": "user", "content": f"consulta final {index}: conservar la firma viva de centavos"})
    return messages


def test_large_session_compiles_under_budget_and_keeps_the_contract() -> None:
    messages = _session()
    index = LiveSymbolIndex()
    for turn_id, message in enumerate(messages):
        blocks = extract_python_blocks(message["content"])
        if blocks and message["role"] == "assistant":
            index.ingest_accepted_turn(turn_id, blocks)
    started = time.perf_counter()
    result = compile_session_context(messages, symbol_index=index, max_budget_tokens=36000, fresh_tail_turns=6)
    elapsed = time.perf_counter() - started
    joined = "\n".join(message["content"] for message in result.messages)
    assert result.original_tokens >= 260_000
    assert result.compiled_tokens <= 36000
    assert 1.0 - (result.compiled_tokens / result.original_tokens) > 0.85
    assert _INVARIANT in joined
    assert "liquidar_orden(centavos, bps_impuesto, moneda)" in joined
    assert "def liquidar_orden(monto, tasa):" not in joined
    assert "DDI-TOMBSTONE" in joined
    assert 'File "old_0.py"' not in joined
    assert "ValueError: firma vieja" in joined
    assert elapsed < 0.250
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") == 1


def _text_with_token_count(seed: str, tokens: int) -> str:
    desired = tokens * 4 - 3
    unit = seed.strip() + ".\n"
    parts: list[str] = []
    used = 0
    while used + len(unit) <= desired:
        parts.append(unit)
        used += len(unit)
    parts.append("a" * (desired - used))
    text = "".join(parts)
    if estimate_tokens(text) != tokens:
        raise RuntimeError(f"no pude construir {tokens} tokens")
    return text


def _turn_with_live_def(definition: str, tokens: int) -> str:
    block = f"```python\n{definition}```\n"
    desired = tokens * 4 - 3
    if len(block) >= desired:
        raise RuntimeError("la definicion no entra en el turno")
    padding = _text_with_token_count("oscilador termico del sensor radial", tokens)
    # El presupuesto se mide sobre el texto final, no sobre el relleno suelto.
    body = block + padding
    if len(body) > desired:
        body = block + padding[: desired - len(block)]
    else:
        body = body + ("b" * (desired - len(body)))
    if estimate_tokens(body) != tokens or definition not in body:
        raise RuntimeError("el turno vivo no conserva la definicion")
    return body


def test_live_definitions_are_pinned_against_high_similarity_filler() -> None:
    def_alpha = "def alpha(x: int) -> int:\n    return x + 1\n"
    def_beta = "def beta(y: int) -> int:\n    return y + 2\n"
    filler = _text_with_token_count(
        "liquidacion centavos impuesto moneda lote comercio retencion",
        4000,
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": "INVARIANTE modulo de liquidacion en centavos."},
        {"role": "user", "content": "Defini las auxiliares vivas del modulo."},
        {"role": "assistant", "content": _turn_with_live_def(def_alpha, 7000)},
        {"role": "user", "content": "Siguiente auxiliar vigente."},
        {"role": "assistant", "content": _turn_with_live_def(def_beta, 7000)},
    ]
    for _ in range(30):
        messages.append({"role": "user", "content": filler})
    result = compile_session_context(messages, max_budget_tokens=28000, fresh_tail_turns=1)
    joined = "\n".join(message["content"] for message in result.messages)
    assert def_alpha in joined
    assert def_beta in joined
    assert "Encabezados tipados vigentes:" in joined
    typed = joined.split("Encabezados tipados vigentes:", 1)[1]
    assert "alpha(x: int) -> int" in typed
    assert "beta(y: int) -> int" in typed


def test_oversized_pinned_turn_keeps_only_the_live_python_block() -> None:
    definition = "def alpha(x: int) -> int:\n    return x + 1\n"
    messages: list[dict[str, str]] = [
        {"role": "system", "content": "INVARIANTE modulo de liquidacion."},
        {"role": "user", "content": "Defini la auxiliar viva."},
        {"role": "assistant", "content": _turn_with_live_def(definition, 12000)},
        {"role": "user", "content": _text_with_token_count("liquidacion centavos impuesto moneda", 3000)},
    ]
    result = compile_session_context(messages, max_budget_tokens=8000, fresh_tail_turns=1)
    joined = "\n".join(message["content"] for message in result.messages)
    assert definition in joined
    assert "oscilador termico" not in joined
    assert result.compiled_tokens <= 8000

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

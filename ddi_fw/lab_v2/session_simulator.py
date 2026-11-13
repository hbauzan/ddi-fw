"""Sesiones sintéticas de 80 a 110 turnos con presupuesto de tokens explícito."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ddi_fw.lab_v2.context_compiler import estimate_tokens
from ddi_fw.lab_v2.trajectory_monitor import compute_context_pollution

ARCHETYPES: tuple[str, ...] = ("healthy", "shadowing", "thrashing", "goal_drift")
N_TURNS = 96
INVARIANT = "INVARIANTE-LIQUIDACION-CENTAVOS: el modulo no puede perder centavos."
ANCHOR = (
    "Implementa el modulo de liquidacion de ordenes en centavos enteros, "
    "sin mezclar tasas flotantes ni cambiar el objetivo."
)
DRIFT = "Receta de pan dulce con canela, pasas y glaseado de azucar para el horno de barro."
LIVE_SIGNATURE = "liquidar_orden(centavos, bps_impuesto, moneda)"
OBSOLETE_SHADOW = "MARCA-OBSOLETA-MONTO-TASA"
OBSOLETE_THRASH = "MARCA-OBSOLETA-AJUSTE"

_LIVE_FN = (
    "def liquidar_orden(centavos: int, bps_impuesto: int, moneda: str) -> int:\n"
    "    return centavos + (centavos * bps_impuesto) // 10000\n"
)
_LIVE_CALL = 'total = liquidar_orden(1500, 210, "ARS")\n'
_OLD_FN = (
    "def liquidar_orden(monto, tasa):\n"
    f'    """{OBSOLETE_SHADOW}"""\n'
    "    return monto * tasa\n"
)
_OLD_CALL = "total = liquidar_orden(100, 0.21)\n"
_PATCH_A = f'def aplicar_ajuste(valor):\n    """{OBSOLETE_THRASH}"""\n    return valor + 1\n'
_PATCH_B = "def aplicar_ajuste(cantidad):\n    return cantidad + 1\n"


@dataclass(frozen=True)
class SessionTurn:
    turn_id: int
    role: str
    content: str
    signal_text: str
    accepted: bool
    pollution: float


@dataclass(frozen=True)
class SimulatedSession:
    session_id: str
    archetype: str
    turns: tuple[SessionTurn, ...]
    ground_truth_fault_turn: int | None
    invariant: str
    live_signature: str
    obsolete_marker: str | None

    @property
    def messages(self) -> list[dict[str, str]]:
        return [{"role": turn.role, "content": turn.content} for turn in self.turns]

    @property
    def total_tokens(self) -> int:
        return sum(estimate_tokens(turn.content) for turn in self.turns)


def build_benchmark_sessions(seed: int = 42, target_tokens: int = 265_000) -> list[SimulatedSession]:
    if target_tokens < 1000:
        raise ValueError("target_tokens debe ser >= 1000")
    if seed < 0:
        raise ValueError("seed no puede ser negativo")
    sessions: list[SimulatedSession] = []
    for archetype_index, archetype in enumerate(ARCHETYPES):
        for copy in range(4):
            sessions.append(
                _build_one(
                    archetype,
                    copy,
                    target_tokens,
                    seed + archetype_index * 10 + copy,
                )
            )
    return sessions


def load_external_jsonl_sessions(dir_path: Path) -> list[SimulatedSession]:
    if not dir_path.is_dir():
        return []
    loaded: list[SimulatedSession] = []
    for path in sorted(dir_path.glob("*.jsonl")):
        header: dict[str, object] = {}
        turns: list[SessionTurn] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("type") == "session":
                header = row
                continue
            turns.append(
                SessionTurn(
                    turn_id=len(turns),
                    role=str(row.get("role", "user")),
                    content=str(row.get("content", "")),
                    signal_text=str(row.get("signal_text", row.get("content", ""))),
                    accepted=bool(row.get("accepted", True)),
                    pollution=float(row.get("pollution", 0.0)),
                )
            )
        if not turns:
            continue
        fault = header.get("ground_truth_fault_turn")
        loaded.append(
            SimulatedSession(
                session_id=str(header.get("session_id", path.stem)),
                archetype=str(header.get("archetype", "external")),
                turns=tuple(turns),
                ground_truth_fault_turn=None if fault is None else int(fault),
                invariant=str(header.get("invariant", "")),
                live_signature=str(header.get("live_signature", "")),
                obsolete_marker=None
                if header.get("obsolete_marker") in {None, ""}
                else str(header.get("obsolete_marker")),
            )
        )
    return loaded


def _build_one(archetype: str, copy: int, target_tokens: int, salt: int) -> SimulatedSession:
    per_turn = max(1, target_tokens // N_TURNS)
    turns: list[SessionTurn] = []
    seen_tokens = 0
    obsolete_tokens = 0
    for turn_id in range(N_TURNS):
        role, body, signal, accepted, obsolete = _semantic(archetype, turn_id)
        minimum = per_turn
        if turn_id == N_TURNS - 1:
            minimum = max(per_turn, target_tokens - seen_tokens)
        content = _pad(body, minimum, f"{salt}-{turn_id}")
        seen_tokens += estimate_tokens(content)
        if obsolete:
            obsolete_tokens += estimate_tokens(content)
        pollution = compute_context_pollution(seen_tokens, min(obsolete_tokens, seen_tokens), 0)
        turns.append(
            SessionTurn(
                turn_id=turn_id,
                role=role,
                content=content,
                signal_text=signal,
                accepted=accepted,
                pollution=pollution,
            )
        )
    marker = None
    if archetype == "shadowing":
        marker = OBSOLETE_SHADOW
    elif archetype == "thrashing":
        marker = OBSOLETE_THRASH
    fault = None if archetype == "healthy" else 93
    return SimulatedSession(
        session_id=f"b-{archetype}-{copy}",
        archetype=archetype,
        turns=tuple(turns),
        ground_truth_fault_turn=fault,
        invariant=INVARIANT,
        live_signature=LIVE_SIGNATURE,
        obsolete_marker=marker,
    )


def _semantic(archetype: str, turn: int) -> tuple[str, str, str, bool, bool]:
    if turn == 0:
        return "system", INVARIANT, ANCHOR, True, False
    if turn == 1:
        return "user", ANCHOR, ANCHOR, True, False
    if archetype == "goal_drift" and turn in {92, 93}:
        return "assistant", DRIFT, DRIFT, True, False
    if archetype == "shadowing" and turn == 2:
        return "assistant", _fence(_OLD_FN), ANCHOR, True, True
    if archetype == "shadowing" and turn == 6:
        return "assistant", _fence(_OLD_CALL), ANCHOR, True, False
    if archetype == "shadowing" and turn == 76:
        return "assistant", _fence(_LIVE_FN), ANCHOR, True, False
    if archetype == "shadowing" and turn == 93:
        return "assistant", _fence(_OLD_CALL), ANCHOR, False, False
    if archetype == "thrashing" and turn == 22:
        return "assistant", _fence(_PATCH_A), _PATCH_A, False, True
    if archetype == "thrashing" and turn == 93:
        return "assistant", _fence(_PATCH_B), _PATCH_B, False, False
    if archetype != "shadowing" and turn == 2:
        return "assistant", _fence(_LIVE_FN), ANCHOR, True, False
    if archetype != "shadowing" and turn == 8:
        return "assistant", _fence(_LIVE_CALL), ANCHOR, True, False
    return "user", "INFO caja evento dentro del objetivo de liquidacion.\n", ANCHOR, True, False


def _fence(code: str) -> str:
    return f"```python\n{code.rstrip()}\n```\n"


def _pad(text: str, minimum_tokens: int, salt: str) -> str:
    if estimate_tokens(text) >= minimum_tokens:
        return text
    prefix = (
        "FAILED tests/test_liquidacion.py::test_centavos - "
        f"AssertionError saldo={salt} esperado=1050 obtenido=1049\n"
    )
    base = text + "\n" + prefix
    target_len = minimum_tokens * 4 - 3
    if len(base) >= target_len:
        return base
    corpus = _filler_corpus()
    need = target_len - len(base)
    repeated = corpus * (need // len(corpus) + 1)
    return (base + repeated)[:target_len]


def _filler_corpus() -> str:
    global _FILLER
    if _FILLER is not None:
        return _FILLER
    parts = [
        "FAILED tests/test_liquidacion.py::test_centavos - AssertionError esperado=1050 obtenido=1049\n"
    ]
    import inspect
    import json as json_module
    import pathlib
    import textwrap

    for module in (inspect, pathlib, textwrap, json_module):
        try:
            parts.append(Path(inspect.getfile(module)).read_text(encoding="utf-8", errors="replace"))
        except (OSError, TypeError):
            continue
    root = Path(__file__).resolve().parents[2]
    for relative in ("ddi_fw/hardware.py", "ddi_fw/embedder.py", "pyproject.toml"):
        file = root / relative
        if file.is_file():
            parts.append(file.read_text(encoding="utf-8", errors="replace"))
    text = "\n".join(part for part in parts if part).replace("```", "'''")
    _FILLER = text or "x"
    return _FILLER


_FILLER: str | None = None

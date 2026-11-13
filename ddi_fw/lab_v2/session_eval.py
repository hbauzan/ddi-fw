"""Corre los tres detectores y el compilador sobre sesiones ya materializadas."""

from __future__ import annotations

import time

import numpy as np

from ddi_fw.lab_v2.ast_symbol_index import (
    LiveSymbolIndex,
    compute_structural_ast_hash,
    extract_python_blocks,
)
from ddi_fw.lab_v2.context_compiler import compile_session_context
from ddi_fw.lab_v2.session_metrics import (
    determine_test_b_verdict,
    summarize_compiler,
    summarize_detector,
)
from ddi_fw.lab_v2.session_simulator import SimulatedSession
from ddi_fw.lab_v2.trajectory_monitor import TrajectoryMonitor

DETECTORS: tuple[tuple[str, str, bool], ...] = (
    ("D1_RawCosineOnly", "raw_cosine", False),
    ("D2_WhitenedKinematicsOnly", "whitened", False),
    ("D3_FullGovernor_Kinematics_Plus_AST", "whitened", True),
)


def embed_signal_matrices(
    sessions: list[SimulatedSession],
    embedder: object,
    *,
    batch_size: int,
) -> list[np.ndarray]:
    if batch_size < 1:
        raise ValueError("batch_size debe ser >= 1")
    texts = [turn.signal_text for session in sessions for turn in session.turns]
    unique = list(dict.fromkeys(texts))
    print(f"embeddings {len(texts)} signals unique={len(unique)} model={embedder.model_id}", flush=True)
    encoded = _embed_unique(embedder, unique, batch_size=batch_size)
    rows = {text: encoded[index] for index, text in enumerate(unique)}
    matrices: list[np.ndarray] = []
    cursor = 0
    for session in sessions:
        width = len(session.turns)
        matrices.append(np.vstack([rows[text] for text in texts[cursor : cursor + width]]))
        cursor += width
    return matrices


def evaluate_sessions(
    sessions: list[SimulatedSession],
    matrices: list[np.ndarray],
    *,
    anchor_floor: float = 0.75,
    budget_tokens: int = 36000,
) -> dict[str, object]:
    if len(sessions) != len(matrices):
        raise ValueError("sesiones y matrices no alinean")
    detector_payload: dict[str, dict[str, float]] = {}
    d3_latency: list[float] = []
    for name, mode, use_ast in DETECTORS:
        alert_turns: list[list[int]] = []
        latencies: list[float] = []
        for session, matrix in zip(sessions, matrices, strict=True):
            alerts, elapsed = _run_detector(
                session,
                matrix,
                mode=mode,
                use_ast=use_ast,
                anchor_floor=anchor_floor,
            )
            alert_turns.append(alerts)
            latencies.extend(elapsed)
        if name.startswith("D3_"):
            d3_latency = latencies
        detector_payload[name] = summarize_detector(
            sessions=sessions,
            alert_turns=alert_turns,
            audit_latency_ms=latencies,
        )
    compiler_rows = [
        _compile_row(session, d3_latency, index, budget_tokens=budget_tokens)
        for index, session in enumerate(sessions)
    ]
    compiler = summarize_compiler(compiler_rows)
    ordered = [detector_payload[name] for name, _mode, _ast in DETECTORS]
    verdict = determine_test_b_verdict(ordered[0], ordered[1], ordered[2], compiler)
    return {"detectors": detector_payload, "compiler": compiler, "verdict": verdict}


def _embed_unique(embedder: object, texts: list[str], *, batch_size: int) -> np.ndarray:
    parts: list[np.ndarray] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        parts.append(np.asarray(embedder.embed_batch(batch), dtype=np.float64))
    if not parts:
        return np.zeros((0, int(embedder.dimension)), dtype=np.float64)
    stacked = np.vstack(parts)
    if stacked.shape != (len(texts), int(embedder.dimension)):
        raise ValueError(f"shape de embeddings inválida: {stacked.shape}")
    return stacked


def _run_detector(
    session: SimulatedSession,
    matrix: np.ndarray,
    *,
    mode: str,
    use_ast: bool,
    anchor_floor: float,
) -> tuple[list[int], list[float]]:
    if matrix.shape[0] != len(session.turns):
        raise ValueError(f"{session.session_id} no tiene un vector por turno")
    reference = matrix if mode == "whitened" else None
    monitor = TrajectoryMonitor(
        matrix[0],
        mode=mode,
        reference=reference,
        anchor_floor=anchor_floor,
    )
    index = LiveSymbolIndex() if use_ast else None
    alerts: list[int] = []
    elapsed: list[float] = []
    for turn, vector in zip(session.turns, matrix, strict=True):
        started = time.perf_counter()
        violations = []
        hashes: set[str] = set()
        blocks: list[str] = []
        if use_ast and turn.role == "assistant":
            blocks = extract_python_blocks(turn.content)
            for block in blocks:
                digest = compute_structural_ast_hash(block)
                if digest is not None:
                    hashes.add(digest)
                if index is not None:
                    violations.extend(index.audit_candidate_code(block))
        found = monitor.evaluate_turn(
            turn_id=turn.turn_id,
            vector=vector,
            accepted=turn.accepted,
            ast_violations=violations,
            ast_hashes=hashes,
            pollution=turn.pollution,
            failure_reason="" if turn.accepted else "turno rechazado",
        )
        if use_ast and index is not None and turn.accepted and blocks:
            index.ingest_accepted_turn(turn.turn_id, blocks)
        elapsed.append((time.perf_counter() - started) * 1000.0)
        if found:
            alerts.append(turn.turn_id)
    return alerts, elapsed


def _compile_row(
    session: SimulatedSession,
    d3_latency: list[float],
    session_index: int,
    *,
    budget_tokens: int,
) -> dict[str, float]:
    index = LiveSymbolIndex()
    notes: list[FailureNote] = []
    for turn in session.turns:
        if turn.role != "assistant":
            continue
        blocks = extract_python_blocks(turn.content)
        if turn.accepted and blocks:
            index.ingest_accepted_turn(turn.turn_id, blocks)
        elif not turn.accepted:
            notes.append(FailureNote(turn.turn_id, "turno rechazado"))
    started = time.perf_counter()
    compiled = compile_session_context(
        session.messages,
        symbol_index=index,
        negative_memory=notes,
        max_budget_tokens=budget_tokens,
        fresh_tail_turns=6,
    )
    latency_ms = (time.perf_counter() - started) * 1000.0
    joined = "\n".join(message["content"] for message in compiled.messages)
    per_session = len(session.turns)
    start = session_index * per_session
    audit = d3_latency[start : start + per_session]
    if len(audit) != per_session:
        raise ValueError("latencias D3 incompletas")
    original = float(compiled.original_tokens)
    compiled_tokens = float(compiled.compiled_tokens)
    savings = 0.0 if original == 0.0 else 1.0 - compiled_tokens / original
    return {
        "original_tokens": original,
        "compiled_tokens": compiled_tokens,
        "savings_ratio": savings,
        "invariant_ok": 1.0 if session.invariant in joined else 0.0,
        "live_ok": 1.0 if session.live_signature in joined else 0.0,
        "obsolete_ok": _obsolete_removed(session, joined),
        "latency_ms": latency_ms,
        "audit_latency_ms": float(np.mean(np.asarray(audit, dtype=np.float64))),
    }


def _obsolete_removed(session: SimulatedSession, joined: str) -> float:
    marker = session.obsolete_marker
    if marker is None:
        return 1.0
    existed = any(marker in turn.content for turn in session.turns)
    if not existed:
        return 1.0
    return 0.0 if marker in joined else 1.0


class FailureNote:
    def __init__(self, turn_id: int, reason: str) -> None:
        self.turn_id = turn_id
        self.reason = reason

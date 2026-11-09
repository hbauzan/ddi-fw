"""Slice B2: cada alerta sale de una señal, no de un rótulo fijo."""

from __future__ import annotations

import numpy as np

from ddi_fw.lab_v2.ast_symbol_index import AstViolation
from ddi_fw.lab_v2.trajectory_monitor import (
    TrajectoryMonitor,
    build_surgical_reprompt,
    compute_context_pollution,
)


def _monitor() -> TrajectoryMonitor:
    anchor = np.array([1.0, 0.0, 0.0])
    return TrajectoryMonitor(anchor, mode="raw_cosine", anchor_floor=0.75)


def test_goal_drift_needs_two_consecutive_low_alignment_turns() -> None:
    monitor = _monitor()
    on_topic = np.array([1.0, 0.0, 0.0])
    drift = np.array([0.0, 1.0, 0.0])
    assert monitor.evaluate_turn(
        turn_id=1, vector=on_topic, accepted=True, ast_violations=[], ast_hashes=set(), pollution=0.0
    ) == []
    assert monitor.evaluate_turn(
        turn_id=2, vector=drift, accepted=True, ast_violations=[], ast_hashes=set(), pollution=0.0
    ) == []
    alerts = monitor.evaluate_turn(
        turn_id=3, vector=drift, accepted=True, ast_violations=[], ast_hashes=set(), pollution=0.0
    )
    assert [item.kind for item in alerts] == ["GOAL_DRIFT_DETECTED"]
    text = build_surgical_reprompt(alerts[0])
    assert "turno 3" in text
    assert "objetivo" in text


def test_thrashing_cosmetic_and_ast_alerts_are_distinct() -> None:
    monitor = _monitor()
    vector = np.array([1.0, 0.0, 0.0])
    failed = monitor.evaluate_turn(
        turn_id=4,
        vector=vector,
        accepted=False,
        ast_violations=[],
        ast_hashes={"hash-a"},
        pollution=0.0,
        failure_reason="assert roto",
    )
    assert failed == []
    repeated = monitor.evaluate_turn(
        turn_id=9,
        vector=np.array([0.0, 1.0, 0.0]),
        accepted=False,
        ast_violations=[],
        ast_hashes={"hash-a"},
        pollution=0.1,
        failure_reason="mismo parche",
    )
    assert any(item.kind == "THRASHING_LOOP_DETECTED" for item in repeated)
    stagnation = monitor.evaluate_turn(
        turn_id=10,
        vector=np.array([0.0, 1.0, 0.0]),
        accepted=True,
        ast_violations=[
            AstViolation(kind="arity_mismatch", symbol="calc", detail="calc no entra")
        ],
        ast_hashes=set(),
        pollution=0.0,
    )
    kinds = {item.kind for item in stagnation}
    assert "COSMETIC_STAGNATION" in kinds
    assert "AST_CONTRACT_BREACH" in kinds
    ast_alert = next(item for item in stagnation if item.kind == "AST_CONTRACT_BREACH")
    assert "calc" in build_surgical_reprompt(ast_alert)


def test_pollution_ratio_and_whitened_mode_stay_finite() -> None:
    assert compute_context_pollution(100, 10, 5) == 0.15
    assert compute_context_pollution(0, 0, 0) == 0.0
    reference = np.array([[1.0, 0.2, 0.0], [0.8, 0.1, 0.3], [1.1, -0.2, 0.1]])
    monitor = TrajectoryMonitor(
        np.array([1.0, 0.0, 0.0]),
        mode="whitened",
        reference=reference,
        anchor_floor=0.2,
    )
    alerts = monitor.evaluate_turn(
        turn_id=1,
        vector=reference[0],
        accepted=True,
        ast_violations=[],
        ast_hashes=set(),
        pollution=0.0,
    )
    assert alerts == []

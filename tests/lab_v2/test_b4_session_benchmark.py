"""Slice B4: el veredicto y el benchmark corto salen de las métricas, no de un rótulo fijo."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ddi_fw.lab_v2.session_metrics import LATEX_BLOCK, determine_test_b_verdict
from ddi_fw.lab_v2.session_simulator import (
    N_TURNS,
    build_benchmark_sessions,
    load_external_jsonl_sessions,
)
from scripts.lab_v2.run_test_b import main, run_test_b


def _stats(recall: float, false_alarm: float, f1: float) -> dict[str, float]:
    return {
        "fault_detection_recall": recall,
        "healthy_session_false_alarm_rate": false_alarm,
        "f1_score": f1,
        "f1_shadowing": f1,
        "f1_thrashing": f1,
        "f1_goal_drift": f1,
        "mean_turn_audit_latency_ms": 0.1,
    }


def _compiler(*, ok: bool) -> dict[str, float]:
    if ok:
        return {
            "invariant_retention_rate": 1.0,
            "live_signature_retention_rate": 1.0,
            "mean_compiled_tokens": 1200.0,
            "mean_token_savings_ratio": 0.91,
        }
    return {
        "invariant_retention_rate": 0.5,
        "live_signature_retention_rate": 0.25,
        "mean_compiled_tokens": 50000.0,
        "mean_token_savings_ratio": 0.2,
    }


def test_verdict_changes_when_the_measurements_change() -> None:
    strong = determine_test_b_verdict(
        _stats(1.0 / 3.0, 0.0, 0.5),
        _stats(1.0 / 3.0, 0.0, 0.5),
        _stats(1.0, 0.0, 1.0),
        _compiler(ok=True),
    )
    weak = determine_test_b_verdict(
        _stats(0.9, 0.0, 0.94),
        _stats(0.4, 0.0, 0.5),
        _stats(0.1, 0.5, 0.15),
        _compiler(ok=False),
    )
    assert strong["overall_winner"] == "D3_FullGovernor_Kinematics_Plus_AST"
    assert strong["governor_beats_raw_cosine"] is True
    assert strong["compiler_meets_contract"] is True
    assert weak["overall_winner"] == "D1_RawCosineOnly"
    assert weak["governor_beats_raw_cosine"] is False
    assert weak["compiler_meets_contract"] is False
    assert strong["overall_winner"] != weak["overall_winner"]


def test_sessions_cover_four_archetypes_inside_the_token_budget() -> None:
    sessions = build_benchmark_sessions(seed=42, target_tokens=15000)
    assert len(sessions) == 16
    assert {item.archetype for item in sessions} == {"healthy", "shadowing", "thrashing", "goal_drift"}
    assert all(len(item.turns) == N_TURNS for item in sessions)
    assert all(item.total_tokens == 15000 for item in sessions)
    healthy = [item for item in sessions if item.archetype == "healthy"]
    assert all(item.ground_truth_fault_turn is None for item in healthy)
    assert all(turn.accepted for item in healthy for turn in item.turns)


def test_external_jsonl_loader_reads_a_header_and_turns(tmp_path: Path) -> None:
    path = tmp_path / "extra.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "session",
                        "session_id": "ext-1",
                        "archetype": "external",
                        "ground_truth_fault_turn": 2,
                        "invariant": "INV",
                        "live_signature": "f(a)",
                        "obsolete_marker": "",
                    }
                ),
                json.dumps({"role": "user", "content": "hola", "signal_text": "hola", "accepted": True}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    loaded = load_external_jsonl_sessions(tmp_path)
    assert len(loaded) == 1
    assert loaded[0].session_id == "ext-1"
    assert loaded[0].ground_truth_fault_turn == 2
    assert loaded[0].obsolete_marker is None
    assert loaded[0].turns[0].signal_text == "hola"


def test_fake_benchmark_keeps_d3_ahead_without_hardcoded_winner(tmp_path: Path) -> None:
    json_path = tmp_path / "b.json"
    md_path = tmp_path / "b.md"
    payload = run_test_b(
        embedder_name="fake",
        json_path=json_path,
        md_path=md_path,
        target_tokens=15000,
        seed=42,
        live_api=False,
    )
    d1 = payload["detectors"]["D1_RawCosineOnly"]
    d3 = payload["detectors"]["D3_FullGovernor_Kinematics_Plus_AST"]
    assert d1["healthy_session_false_alarm_rate"] == 0.0
    assert d3["healthy_session_false_alarm_rate"] == 0.0
    assert d3["fault_detection_recall"] == 1.0
    assert d1["fault_detection_recall"] < d3["fault_detection_recall"]
    assert payload["verdict"]["overall_winner"] == "D3_FullGovernor_Kinematics_Plus_AST"
    assert payload["verdict"]["governor_beats_raw_cosine"] is True
    encoded = json_path.read_text(encoding="utf-8")
    markdown = md_path.read_text(encoding="utf-8")
    assert encoded.strip()
    assert markdown.strip()
    assert "\t" not in markdown
    assert "\v" not in markdown
    assert r"\alpha" in LATEX_BLOCK
    assert r"\nu" in markdown
    assert r"\rho" in markdown
    assert r"H_{\text{ctx}}" in markdown
    assert ":.2f" not in Path("ddi_fw/lab_v2/session_metrics.py").read_text(encoding="utf-8")
    assert "round(" not in Path("ddi_fw/lab_v2/session_metrics.py").read_text(encoding="utf-8")
    with pytest.raises(RuntimeError, match="TASK-003"):
        main(["--embedder", "fake", "--live-api", "--target-tokens", "15000"])

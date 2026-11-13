"""Slice 4: el veredicto no está horneado y el runner fake deja artefactos íntegros."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ddi_fw.lab_v2.metrics import (
    compute_far_at_frr,
    compute_pr_auc,
    compute_roc_auc,
    determine_test_a_verdict,
    render_test_a_markdown,
)
from scripts.lab_v2.run_test_a import run_test_a


def _stats(
    roc: float,
    far: float,
    *,
    frr_total: float = 0.02,
    far_total: float = 0.02,
) -> dict[str, float]:
    return {
        "roc_auc": roc,
        "far_at_frr_05": far,
        "frr_total": frr_total,
        "far_total": far_total,
    }


def test_verdict_follows_the_better_geometry_in_both_directions() -> None:
    weak = _stats(0.40, 0.50, frr_total=0.40, far_total=0.40)
    cosine_better = determine_test_a_verdict(
        weak,
        _stats(0.91, 0.08),
        _stats(0.70, 0.20),
        weak,
    )
    subspace_better = determine_test_a_verdict(
        weak,
        _stats(0.70, 0.20),
        _stats(0.96, 0.04),
        weak,
    )
    assert cosine_better["pure_embedding_winner"] == "M2_Cosine"
    assert cosine_better["overall_winner"] == "M2_Cosine"
    assert cosine_better["m3_beats_cosine_empirically"] is False
    assert subspace_better["pure_embedding_winner"] == "M3_EEB_Pure"
    assert subspace_better["overall_winner"] == "M3_EEB_Pure"
    assert subspace_better["m3_beats_cosine_empirically"] is True
    viable = determine_test_a_verdict(
        _stats(0.50, 0.20, frr_total=0.10, far_total=0.05),
        weak,
        weak,
        weak,
    )
    collapsed = determine_test_a_verdict(
        _stats(0.50, 0.20, frr_total=0.80, far_total=0.40),
        _stats(0.99, 0.01),
        weak,
        weak,
    )
    assert viable["m1_ddi_v040_viable"] is True
    assert collapsed["m1_ddi_v040_viable"] is False
    assert collapsed["overall_winner"] == "M2_Cosine"


def test_rank_metrics_match_closed_form_examples() -> None:
    legit = np.array([0.0, 0.1])
    attack = np.array([0.8, 0.9])
    assert compute_roc_auc(legit, attack) == 1.0
    assert compute_roc_auc(np.array([0.2, 0.2]), np.array([0.2, 0.2])) == 0.5
    assert compute_pr_auc(legit, attack) == 1.0
    observed = compute_far_at_frr(np.array([0.0, 1.0, 2.0, 3.0]), np.array([2.25, 3.0, 1.0]), 0.25)
    assert observed == 2.0 / 3.0


def test_markdown_keeps_latex_commands_intact() -> None:
    stats = {
        "roc_auc": 0.5,
        "pr_auc": 0.25,
        "far_at_frr_01": 0.125,
        "far_at_frr_05": 0.0625,
        "frr_total": 0.0,
        "far_total": 1.0,
        "frr_business_python": 0.0,
        "far_piggybacking": 1.0,
        "latency_ms_p50": 0.3333333333333333,
        "latency_ms_p95": 0.5,
        "latency_ms_p99": 0.5,
    }
    payload = {
        "models": {name: dict(stats) for name in ("M1_DDI_v040", "M2_Cosine", "M3_EEB_Pure", "M4_Hybrid_AST_EEB")},
        "verdict": determine_test_a_verdict(stats, stats, stats, stats),
        "hardware": {"version_python": "3.11"},
    }
    markdown = render_test_a_markdown(payload)
    assert "\x0b" not in markdown
    assert "\t" not in markdown
    assert r"\text" in markdown
    assert r"\vec" in markdown
    assert r"\tau" in markdown
    assert "0.33333333333333331" in markdown or "0.3333333333333333" in markdown


def test_markdown_subtype_breakdown_keeps_native_precision() -> None:
    third = 1.0 / 3.0
    stats = {
        "roc_auc": third,
        "pr_auc": third,
        "far_at_frr_01": third,
        "far_at_frr_05": third,
        "frr_total": third,
        "far_total": third,
        "frr_stdlib_python": third,
        "frr_business_python": third,
        "far_seen_domain": third,
        "far_unseen_domain_ood": third,
        "far_other_language": third,
        "far_piggybacking": third,
        "latency_ms_p50": third,
        "latency_ms_p95": third,
        "latency_ms_p99": third,
    }
    names = ("M1_DDI_v040", "M2_Cosine", "M3_EEB_Pure", "M4_Hybrid_AST_EEB")
    payload = {
        "models": {name: dict(stats) for name in names},
        "verdict": determine_test_a_verdict(stats, stats, stats, stats),
    }
    markdown = render_test_a_markdown(payload)
    assert "## Desglose por subcategoría" in markdown
    assert "frr_stdlib_python" in markdown
    assert "far_unseen_domain_ood" in markdown
    assert "far_other_language" in markdown
    assert format(third, ".17g") in markdown
    assert ".2f" not in markdown


def test_fake_runner_writes_native_json_and_markdown(tmp_path: Path) -> None:
    json_path = tmp_path / "lab_v2_test_a_results.json"
    md_path = tmp_path / "test_a_duelo_subespacio_vs_coseno.md"
    payload = run_test_a(
        embedder_name="fake",
        json_path=json_path,
        md_path=md_path,
        seed=42,
        batch_size=64,
    )
    raw = json_path.read_text(encoding="utf-8")
    markdown = md_path.read_text(encoding="utf-8")
    assert json_path.stat().st_size > 0
    assert md_path.stat().st_size > 0
    assert "\x0b" not in markdown
    assert "\t" not in markdown
    assert r"\text" in markdown and r"\vec" in markdown and r"\tau" in markdown
    decoded = json.loads(raw)
    roc = decoded["models"]["M3_EEB_Pure"]["roc_auc"]
    assert isinstance(roc, float)
    assert json.dumps(roc) in raw
    assert decoded["verdict"] == payload["verdict"]
    assert decoded["verdict"]["pure_embedding_winner"] in {"M2_Cosine", "M3_EEB_Pure"}
    assert ":.2f" not in Path("ddi_fw/lab_v2/metrics.py").read_text(encoding="utf-8")
    assert "round(" not in Path("ddi_fw/lab_v2/metrics.py").read_text(encoding="utf-8")
    assert "round(" not in Path("scripts/lab_v2/run_test_a.py").read_text(encoding="utf-8")

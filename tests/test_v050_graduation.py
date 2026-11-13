"""Slice 4 — auditoría de graduación. El veredicto sale de funciones, no de strings fijos."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ddi_fw.lab_v2.models import M4_HybridAstSpectral
from scripts.lab_v2.run_v050_graduation_check import (
    cache_reused_every_repeated_chunk,
    graduation_ready,
    hardened_m4_lowers_other_language_far,
    run_v050_graduation_check,
    tensors_match,
)


def test_predicates_accept_and_reject() -> None:
    assert hardened_m4_lowers_other_language_far(0.25, 0.0) is True
    assert hardened_m4_lowers_other_language_far(0.0, 0.0) is False
    assert hardened_m4_lowers_other_language_far(0.1, 0.4) is False
    assert (
        hardened_m4_lowers_other_language_far(
            0.0, 0.0, m3_prose_far=1.0, m3_hardened_far=0.75
        )
        is True
    )
    assert (
        hardened_m4_lowers_other_language_far(
            0.0, 0.0, m3_prose_far=1.0, m3_hardened_far=1.0
        )
        is False
    )
    assert cache_reused_every_repeated_chunk(4, 4, 0) is True
    assert cache_reused_every_repeated_chunk(4, 3, 1) is False
    assert cache_reused_every_repeated_chunk(0, 0, 0) is False
    assert graduation_ready(True, True, True) is True
    assert graduation_ready(True, False, True) is False
    assert graduation_ready() is False


def test_tensor_match_is_bitwise() -> None:
    left = M4_HybridAstSpectral()
    right = M4_HybridAstSpectral()
    left.mu_pos = np.array([1.0, 2.0], dtype=np.float64)
    right.mu_pos = np.array([1.0, 2.0], dtype=np.float64)
    left.w_hat = np.array([0.0, 1.0], dtype=np.float64)
    right.w_hat = np.array([0.0, 1.0], dtype=np.float64)
    left.u_k = np.ones((2, 1), dtype=np.float64)
    right.u_k = np.ones((2, 1), dtype=np.float64)
    left.gamma = np.array([0.5], dtype=np.float64)
    right.gamma = np.array([0.5], dtype=np.float64)
    left.medians = np.zeros(3, dtype=np.float64)
    right.medians = np.zeros(3, dtype=np.float64)
    left.iqrs = np.ones(3, dtype=np.float64)
    right.iqrs = np.ones(3, dtype=np.float64)
    left.q_hat = 1.25
    right.q_hat = 1.25
    assert tensors_match(left, right) is True
    right.q_hat = 1.5
    assert tensors_match(left, right) is False
    right.q_hat = 1.25
    left.w_hat_foreign = np.array([0.0, 1.0], dtype=np.float64)
    left.foreign_median = 0.5
    left.foreign_iqr = 1.0
    left.shrinkage_foreign = 0.25
    assert tensors_match(left, right) is False
    right.w_hat_foreign = np.array([0.0, 1.0], dtype=np.float64)
    right.foreign_median = 0.5
    right.foreign_iqr = 1.0
    right.shrinkage_foreign = 0.25
    assert tensors_match(left, right) is True
    right.foreign_median = 0.6
    assert tensors_match(left, right) is False


def test_fake_graduation_writes_native_reports(tmp_path: Path) -> None:
    json_path = tmp_path / "v050_graduation_audit.json"
    md_path = tmp_path / "v050_graduation_audit.md"
    payload = run_v050_graduation_check(
        embedder_name="fake",
        json_path=json_path,
        md_path=md_path,
        seed=42,
    )
    raw = json_path.read_text(encoding="utf-8")
    markdown = md_path.read_text(encoding="utf-8")
    assert payload["test_sample_count"] == 488
    assert payload["foreign_train_anchor_count"] == 36
    assert "\t" not in markdown
    assert "\x0b" not in markdown
    assert r"\text" in markdown
    assert r"\alpha" in markdown
    assert r"\frac" in markdown
    assert r"\vec" in markdown
    decoded = json.loads(raw)
    prose_far = payload["variants"]["prose_only_negatives"]["M4_HybridAstSpectral"]["far_other_language"]
    hardened_far = payload["variants"]["multilang_hardened_negatives"]["M4_HybridAstSpectral"][
        "far_other_language"
    ]
    m3_prose_far = payload["variants"]["prose_only_negatives"]["M3_WhitenedSpectralSubspace"][
        "far_other_language"
    ]
    m3_hardened_far = payload["variants"]["multilang_hardened_negatives"][
        "M3_WhitenedSpectralSubspace"
    ]["far_other_language"]
    assert isinstance(prose_far, float)
    assert isinstance(m3_prose_far, float)
    assert isinstance(m3_hardened_far, float)
    assert json.dumps(prose_far) in raw
    assert decoded["verdict"]["m4_other_language_far_improved"] is hardened_m4_lowers_other_language_far(
        prose_far,
        hardened_far,
        m3_prose_far=m3_prose_far,
        m3_hardened_far=m3_hardened_far,
    )
    assert decoded["verdict"]["graduation_ready"] is graduation_ready(
        decoded["verdict"]["m4_other_language_far_improved"],
        decoded["verdict"]["npz_roundtrip_bitwise"],
        decoded["verdict"]["cache_reused"],
    )
    assert format(prose_far, ".17g") in markdown
    source = Path("scripts/lab_v2/run_v050_graduation_check.py").read_text(encoding="utf-8")
    assert "round(" not in source
    assert ":.2f" not in source
    assert 'r"""' in source
    assert decoded["checks"]["npz_roundtrip_bitwise"] is True
    assert decoded["checks"]["cache_reused"] is True

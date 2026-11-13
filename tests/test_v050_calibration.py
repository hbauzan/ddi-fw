"""Slice 1 — anclas multilenguaje, fit de M4 y .npz sin pickle."""

from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

import numpy as np

from ddi_fw.embedder import FakeEmbedder
from ddi_fw.lab_v2.chunker import extract_chunks
from ddi_fw.lab_v2.corpus_builder import build_test_a_dataset, normalize_text
from ddi_fw.lab_v2.fixtures_code import FOREIGN_SNIPPETS
from ddi_fw.lab_v2.models import M4_HybridAstSpectral
from ddi_fw.v2_calibration import (
    FOREIGN_TRAIN_ANCHORS,
    assert_disjoint_from_test_a,
    fit_v2_spectral_ast,
    foreign_anchor_leakage,
    load_v2_calibration,
    main,
    save_v2_calibration,
)

_LANGUAGES = ("javascript", "sql", "bash", "rust", "c", "go")
_TENSOR_FIELDS = ("mu_pos", "w_hat", "u_k", "gamma", "medians", "iqrs")


def test_foreign_train_anchors_cover_six_languages() -> None:
    assert len(FOREIGN_TRAIN_ANCHORS) == 36
    counts = Counter(language for language, _name, _source in FOREIGN_TRAIN_ANCHORS)
    assert counts == {language: 6 for language in _LANGUAGES}
    names = [name for _language, name, _source in FOREIGN_TRAIN_ANCHORS]
    assert len(set(names)) == 36
    for language, name, source in FOREIGN_TRAIN_ANCHORS:
        assert language in _LANGUAGES
        assert name.startswith("v050_anchor_")
        assert source.strip()
        assert extract_chunks(source), name
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        assert not tree.body, name


def test_leakage_detector_flags_shared_identity_and_accepts_disjoint_pair() -> None:
    shared = (("javascript", "shared_anchor", "function sharedAnchor() { return 1; }\n"),)
    foreign = [("javascript", "shared_anchor", "function other() { return 2; }\n")]
    leaks = foreign_anchor_leakage(shared, foreign, [])
    assert leaks

    text = "SELECT dock_id FROM v050_anchor_only_bays WHERE shift = 'night';\n"
    clean = (("sql", "v050_anchor_sql_only_bays", text),)
    other = [("javascript", "unrelated_name", "function unrelatedAnchor() { return 0; }\n")]
    assert foreign_anchor_leakage(clean, other, []) == []

    holdout = build_test_a_dataset(seed=42)
    collided = holdout[0]
    leaked_anchor = (("go", "v050_anchor_go_copied", collided.text),)
    assert foreign_anchor_leakage(leaked_anchor, [], [collided])


def test_real_anchors_are_disjoint_from_test_a_holdout() -> None:
    assert_disjoint_from_test_a()
    dataset = build_test_a_dataset(seed=42)
    holdout = [sample for sample in dataset if sample.split in {"cal", "test"}]
    assert len([sample for sample in dataset if sample.split == "cal"]) == 72
    assert foreign_anchor_leakage(FOREIGN_TRAIN_ANCHORS, FOREIGN_SNIPPETS, holdout) == []
    anchor_text = {normalize_text(source) for _language, _name, source in FOREIGN_TRAIN_ANCHORS}
    foreign_text = {normalize_text(source) for _language, _name, source in FOREIGN_SNIPPETS}
    holdout_text = {normalize_text(sample.text) for sample in holdout}
    assert anchor_text.isdisjoint(foreign_text)
    assert anchor_text.isdisjoint(holdout_text)


def test_fit_stacks_anchors_on_negative_side_and_calibrates_seventy_two() -> None:
    embedder = FakeEmbedder(dimension=16)
    hardened = fit_v2_spectral_ast(
        embedder, alpha=0.05, seed=42, include_foreign_code_anchors=True
    )
    prose = fit_v2_spectral_ast(
        embedder, alpha=0.05, seed=42, include_foreign_code_anchors=False
    )
    assert isinstance(hardened, M4_HybridAstSpectral)
    assert hardened.dimension == 16
    assert hardened.q_hat is not None
    assert prose.q_hat is not None
    assert prose.w_hat_foreign is None
    assert prose.foreign_median is None
    assert prose.foreign_iqr is None
    assert prose.shrinkage_foreign is None
    assert hardened.w_hat_foreign is not None
    assert hardened.foreign_median is not None
    assert hardened.foreign_iqr is not None
    assert hardened.shrinkage_foreign is not None
    assert np.array_equal(hardened.mu_pos, prose.mu_pos)
    assert np.array_equal(hardened.w_hat, prose.w_hat)
    assert np.array_equal(hardened.u_k, prose.u_k)
    assert np.array_equal(hardened.gamma, prose.gamma)
    assert np.array_equal(hardened.medians, prose.medians)
    assert np.array_equal(hardened.iqrs, prose.iqrs)
    assert hardened.shrinkage_pos == prose.shrinkage_pos
    assert hardened.shrinkage_neg == prose.shrinkage_neg


def test_npz_roundtrip_is_bitwise_and_forbids_pickle(tmp_path: Path) -> None:
    embedder = FakeEmbedder(dimension=16)
    model = fit_v2_spectral_ast(embedder, alpha=0.05, seed=42, include_foreign_code_anchors=True)
    path = save_v2_calibration(
        tmp_path / "v2_spectral_ast.npz",
        model,
        model_id="fake-roundtrip",
        alpha=0.05,
    )
    source = Path("ddi_fw/v2_calibration.py").read_text(encoding="utf-8")
    assert "import pickle" not in source
    assert "allow_pickle=True" not in source
    assert "allow_pickle=False" in source
    foreign_fields = ("w_hat_foreign", "foreign_median", "foreign_iqr", "shrinkage_foreign")
    with np.load(path, allow_pickle=False) as handle:
        assert "model_id_utf8" in handle.files
        for key in foreign_fields:
            assert key in handle.files
        for key in handle.files:
            assert handle[key].dtype != object
    loaded, meta = load_v2_calibration(path)
    for field in _TENSOR_FIELDS:
        assert np.array_equal(getattr(model, field), getattr(loaded, field))
    for field in foreign_fields:
        assert np.array_equal(
            np.asarray(getattr(model, field), dtype=np.float64),
            np.asarray(getattr(loaded, field), dtype=np.float64),
        )
    assert np.array_equal(
        np.asarray(model.q_hat, dtype=np.float64),
        np.asarray(loaded.q_hat, dtype=np.float64),
    )
    assert meta["model_id"] == "fake-roundtrip"
    assert float(meta["alpha"]) == 0.05
    sample = next(
        item
        for item in build_test_a_dataset(seed=42)
        if item.split == "cal" and item.category == "pos_business_python"
    )
    chunks = extract_chunks(sample.text)
    vectors = np.asarray(embedder.embed_batch([chunk.text for chunk in chunks]), dtype=np.float64)
    assert loaded.score_sample(chunks, vectors) == model.score_sample(chunks, vectors)
    for field in foreign_fields:
        setattr(model, field, None)
    legacy_path = save_v2_calibration(
        tmp_path / "v2_spectral_ast_prose.npz",
        model,
        model_id="fake-roundtrip-prose",
        alpha=0.05,
    )
    with np.load(legacy_path, allow_pickle=False) as handle:
        for key in foreign_fields:
            assert key not in handle.files
    legacy, legacy_meta = load_v2_calibration(legacy_path)
    for field in foreign_fields:
        assert getattr(legacy, field) is None
    assert legacy_meta["model_id"] == "fake-roundtrip-prose"
    assert legacy.score_sample(chunks, vectors) == model.score_sample(chunks, vectors)


def test_cli_fake_writes_loadable_npz(tmp_path: Path) -> None:
    out = tmp_path / "cli.npz"
    code = main(["--embedder", "fake", "--out", str(out), "--alpha", "0.05"])
    assert code == 0
    assert out.is_file()
    _model, meta = load_v2_calibration(out)
    assert meta["model_id"] == "fake"
    project = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'ddi-calibrate-v2 = "ddi_fw.v2_calibration:main"' in project

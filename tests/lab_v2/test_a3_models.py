"""Slice 3: Ledoit-Wolf sigue siendo SPD y el blanqueo gana en anisotropía."""

from __future__ import annotations

import numpy as np

from ddi_fw.lab_v2.chunker import TextChunk
from ddi_fw.lab_v2.models import (
    M1_DdiBoxesBaseline,
    M2_CosineMargin,
    M3_WhitenedSpectralSubspace,
    M4_HybridAstSpectral,
    conformal_threshold,
    ledoit_wolf_covariance,
)


def _roc_auc(legit: np.ndarray, attack: np.ndarray) -> float:
    diffs = attack[:, None] - legit[None, :]
    wins = np.sum(diffs > 0) + 0.5 * np.sum(diffs == 0)
    return float(wins) / float(legit.size * attack.size)


def _chunk_row(vector: np.ndarray, *, valid: bool = True, kind: str = "python_ast") -> tuple[list[TextChunk], np.ndarray]:
    chunk = TextChunk("vector", kind, valid, 1, 1)  # type: ignore[arg-type]
    return [chunk], np.asarray(vector, dtype=np.float64).reshape(1, -1)


def _draw(rng: np.random.Generator, n: int, positive: bool) -> np.ndarray:
    """Señal de 6 sigma en el eje 0 y ruido sigma=20 compartido en los ejes 1..10."""
    matrix = np.zeros((n, 64), dtype=np.float64)
    center = 0.0 if positive else 6.0
    matrix[:, 0] = rng.normal(center, 1.0, size=n)
    matrix[:, 1:11] = rng.normal(0.0, 20.0, size=(n, 10))
    matrix[:, 11:] = rng.normal(0.0, 1.0, size=(n, 53))
    return matrix


def test_ledoit_wolf_stays_positive_definite_when_n_ll_d() -> None:
    rng = np.random.default_rng(42)
    matrix = rng.normal(size=(15, 128))
    _mean, cov, shrinkage = ledoit_wolf_covariance(matrix)
    assert cov.shape == (128, 128)
    assert float(np.linalg.eigvalsh(cov).min()) > 0.0
    assert 1e-3 <= shrinkage <= 1.0
    try:
        ledoit_wolf_covariance(np.ones(8))
    except ValueError:
        pass
    else:
        raise AssertionError("una matriz 1D debio rechazarse")


def test_conformal_threshold_rejects_empty_and_bad_alpha() -> None:
    scores = np.array([0.1, 0.4, 0.2, 0.3])
    assert conformal_threshold(scores, alpha=0.05) == 0.4
    for alpha in (0.0, 1.0, -0.2):
        try:
            conformal_threshold(scores, alpha=alpha)
        except ValueError:
            continue
        raise AssertionError(f"alpha {alpha} debio rechazarse")


def test_anisotropic_subspace_beats_cosine_and_boxes_collapse() -> None:
    rng = np.random.default_rng(42)
    pos_train = _draw(rng, 220, True)
    neg_train = _draw(rng, 220, False)
    pos_cal = _draw(rng, 60, True)
    pos_test = _draw(rng, 300, True)
    neg_test = _draw(rng, 300, False)
    calibration = [_chunk_row(row) for row in pos_cal]

    boxes = M1_DdiBoxesBaseline()
    boxes.fit({"python": pos_train, "receta": neg_train})
    cosine = M2_CosineMargin()
    cosine.fit(pos_train, {"receta": neg_train}, calibration)
    subspace = M3_WhitenedSpectralSubspace()
    subspace.fit(pos_train, neg_train, calibration)
    hybrid = M4_HybridAstSpectral()
    hybrid.fit(pos_train, neg_train, calibration)

    def collect(model: object, rows: np.ndarray) -> tuple[np.ndarray, float]:
        scores = np.empty(rows.shape[0], dtype=np.float64)
        blocked = 0
        for index, row in enumerate(rows):
            chunks, vecs = _chunk_row(row)
            scores[index] = model.score_sample(chunks, vecs)  # type: ignore[attr-defined]
            blocked += int(model.predict_breach(chunks, vecs))  # type: ignore[attr-defined]
        return scores, blocked / float(rows.shape[0])

    m1_legit, m1_legit_block = collect(boxes, pos_test)
    m1_attack, m1_attack_block = collect(boxes, neg_test)
    m2_legit, _m2_legit_block = collect(cosine, pos_test)
    m2_attack, _m2_attack_block = collect(cosine, neg_test)
    m3_legit, _m3_legit_block = collect(subspace, pos_test)
    m3_attack, _m3_attack_block = collect(subspace, neg_test)
    m1_auc = _roc_auc(m1_legit, m1_attack)
    m2_auc = _roc_auc(m2_legit, m2_attack)
    m3_auc = _roc_auc(m3_legit, m3_attack)

    assert m3_auc > 0.98, m3_auc
    assert m2_auc < 0.75, m2_auc
    assert m3_auc > m2_auc
    assert m1_legit_block > 0.95, m1_legit_block
    assert m1_attack_block > 0.95, m1_attack_block
    assert m1_auc < m3_auc

    probe = pos_test[0]
    code_score = hybrid.score_sample(*_chunk_row(probe, valid=True, kind="python_ast"))
    prose_score = hybrid.score_sample(*_chunk_row(probe, valid=False, kind="prose_window"))
    fenced_score = hybrid.score_sample(*_chunk_row(probe, valid=False, kind="fenced_code"))
    foreign_score = hybrid.score_sample(*_chunk_row(probe, valid=False, kind="foreign_code"))
    assert prose_score - code_score == 1.5
    assert fenced_score - prose_score == 6.0
    assert foreign_score - prose_score == 6.0
    centroid = np.mean(pos_train, axis=0)
    prose_centroid = hybrid.score_sample(*_chunk_row(centroid, valid=False, kind="prose_window"))
    foreign_centroid = hybrid.score_sample(*_chunk_row(centroid, valid=False, kind="foreign_code"))
    assert foreign_centroid - prose_centroid == 6.0
    assert hybrid.predict_breach(*_chunk_row(centroid, valid=False, kind="foreign_code"))

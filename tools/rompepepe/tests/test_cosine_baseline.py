"""Tests for Cosine Difference and Similarity Baseline Classifier."""

import numpy as np
import pytest
from rompepepe.baselines.cosine_classifier import CosineClassifier, CosineVerdict


def test_cosine_classifier_basic():
    # 3 mock domains in 4D space
    centroids = {
        "python": np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64),
        "receta": np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float64),
        "legal": np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float64),
    }

    classifier = CosineClassifier(centroids, allowed_alma="python")

    # Vector identical to python
    vec_python = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    verdict_py = classifier.evaluate_vector(vec_python, delta_threshold=0.1, max_forbid_threshold=0.5)

    assert verdict_py.passed_delta is True
    assert verdict_py.passed_forbid is True
    assert np.isclose(verdict_py.sim_allowed, 1.0)
    assert np.isclose(verdict_py.max_sim_forbidden, 0.0)
    assert np.isclose(verdict_py.delta_cosine, 1.0)

    # Vector identical to receta
    vec_receta = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
    verdict_rec = classifier.evaluate_vector(vec_receta, delta_threshold=0.0, max_forbid_threshold=0.5)

    assert verdict_rec.passed_delta is False
    assert verdict_rec.passed_forbid is False
    assert np.isclose(verdict_rec.sim_allowed, 0.0)
    assert np.isclose(verdict_rec.max_sim_forbidden, 1.0)
    assert verdict_rec.closest_forbidden_alma == "receta"
    assert np.isclose(verdict_rec.delta_cosine, -1.0)

    # Vector hybrid (equal parts python and legal)
    vec_hybrid = np.array([0.70710678, 0.0, 0.70710678, 0.0], dtype=np.float32)
    verdict_hyb = classifier.evaluate_vector(vec_hybrid, delta_threshold=0.05, max_forbid_threshold=0.7)

    assert verdict_hyb.passed_delta is False  # delta is 0.0, threshold is 0.05
    assert verdict_hyb.passed_forbid is False  # max_sim is ~0.707, threshold is 0.7
    assert np.isclose(verdict_hyb.sim_allowed, 0.70710678, atol=1e-5)
    assert verdict_hyb.closest_forbidden_alma == "legal"


def test_cosine_classifier_missing_allowed():
    centroids = {"receta": np.array([1.0, 0.0])}
    with pytest.raises(ValueError, match="not found in centroids"):
        CosineClassifier(centroids, allowed_alma="python")

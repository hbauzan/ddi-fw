"""Cosine Difference and Similarity Baseline Classifier.

Provides an industry-standard centroid-based cosine distance / similarity comparator
for comparative and counterfactual security evaluations.
Operates strictly in IEEE 754 float64 without premature rounding.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import numpy.typing as npt

from ddi_fw.embedder import load_rows, rows_matrices


@dataclass(frozen=True)
class CosineVerdict:
    """Detailed audit metrics for a cosine-based classification decision."""

    passed_delta: bool
    passed_forbid: bool
    sim_allowed: float
    max_sim_forbidden: float
    closest_forbidden_alma: str
    delta_cosine: float
    all_similarities: dict[str, float]


class CosineClassifier:
    """Centroid-based Cosine Classifier representing common industry baselines.

    Calculates domain centroids mu_a = (1/N) * sum(v_i) for allowed and forbidden domains,
    then evaluates cosine similarity against incoming embeddings:
        sim(x, y) = (x . y) / (||x|| * ||y||)
        delta_cos(x) = sim(x, mu_allowed) - max_{b in forbidden} sim(x, mu_b)
    """

    def __init__(
        self,
        centroids: Mapping[str, npt.NDArray[np.float64]],
        allowed_alma: str = "python",
        forbidden_almas: list[str] | None = None,
    ):
        self.allowed_alma = allowed_alma
        self.centroids: dict[str, npt.NDArray[np.float64]] = {}
        self.normalized_centroids: dict[str, npt.NDArray[np.float64]] = {}

        for alma, vec in centroids.items():
            arr = np.asarray(vec, dtype=np.float64).reshape(-1)
            norm = np.linalg.norm(arr)
            self.centroids[alma] = arr
            self.normalized_centroids[alma] = arr / (norm if norm > 1e-12 else 1.0)

        if self.allowed_alma not in self.normalized_centroids:
            raise ValueError(f"Allowed alma '{self.allowed_alma}' not found in centroids.")

        all_forbidden = [a for a in self.normalized_centroids.keys() if a != self.allowed_alma]
        self.forbidden_almas = forbidden_almas if forbidden_almas is not None else all_forbidden

    @classmethod
    def from_rows_file(
        cls,
        rows_path: Path,
        allowed_alma: str = "python",
        forbidden_almas: list[str] | None = None,
    ) -> CosineClassifier:
        """Constructs classifier by computing centroids from an npz rows file."""
        if not rows_path.is_file():
            raise FileNotFoundError(f"Rows file not found: {rows_path}")

        raw_rows = load_rows(rows_path)
        matrices = rows_matrices(raw_rows)
        centroids: dict[str, npt.NDArray[np.float64]] = {}

        for alma, mat in matrices.items():
            mat64 = np.asarray(mat, dtype=np.float64)
            centroids[alma] = np.mean(mat64, axis=0)

        return cls(centroids, allowed_alma=allowed_alma, forbidden_almas=forbidden_almas)

    def evaluate_vector(
        self,
        vector: npt.NDArray[np.floating],
        delta_threshold: float = 0.0,
        max_forbid_threshold: float = 0.80,
    ) -> CosineVerdict:
        """Evaluates query vector against centroids with exact IEEE 754 precision."""
        v = np.asarray(vector, dtype=np.float64).reshape(-1)
        v_norm = np.linalg.norm(v)
        v_unit = v / (v_norm if v_norm > 1e-12 else 1.0)

        sims: dict[str, float] = {}
        for alma, u in self.normalized_centroids.items():
            sims[alma] = float(np.dot(v_unit, u))

        sim_allowed = sims[self.allowed_alma]

        forbidden_sims = {a: sims[a] for a in self.forbidden_almas if a in sims}
        if forbidden_sims:
            closest_forbidden = max(forbidden_sims, key=forbidden_sims.get)
            max_sim_forbid = forbidden_sims[closest_forbidden]
        else:
            closest_forbidden = "none"
            max_sim_forbid = -1.0

        delta_cos = sim_allowed - max_sim_forbid

        passed_delta = bool(delta_cos >= delta_threshold)
        passed_forbid = bool(max_sim_forbid < max_forbid_threshold)

        return CosineVerdict(
            passed_delta=passed_delta,
            passed_forbid=passed_forbid,
            sim_allowed=sim_allowed,
            max_sim_forbidden=max_sim_forbid,
            closest_forbidden_alma=closest_forbidden,
            delta_cosine=delta_cos,
            all_similarities=sims,
        )

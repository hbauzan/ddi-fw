"""Cuatro geometrías del Test A. El veredicto de producto no se modifica."""

from __future__ import annotations

import math

import numpy as np

from ddi_fw.corte import etiquetar_fila, evaluar_corte_espectral
from ddi_fw.hoja import RUIDO_UNIVERSAL_BGE_M3, candados_canonicos
from ddi_fw.ingress import Policy, decide
from ddi_fw.lab_v2.chunker import TextChunk

CalGroup = list[tuple[list[TextChunk], np.ndarray]]


def ledoit_wolf_covariance(
    X: np.ndarray, min_shrinkage: float = 1e-3
) -> tuple[np.ndarray, np.ndarray, float]:
    """Devuelve (mean_1d, cov_spd_2d, shrinkage_lambda) en float64."""
    x64 = np.asarray(X, dtype=np.float64)
    if x64.ndim != 2 or x64.shape[0] < 2:
        raise ValueError(f"X debe ser 2D con N >= 2, recibido: {x64.shape}")
    n, d = x64.shape
    mu = np.mean(x64, axis=0)
    xc = x64 - mu
    s = (xc.T @ xc) / float(n)
    trace_s = float(np.trace(s))
    m = max(trace_s / float(d), 1e-12)
    diff = s - m * np.eye(d, dtype=np.float64)
    d2 = float(np.sum(diff * diff)) / float(d)
    if d2 <= 1e-24:
        lam = 1.0
    else:
        row_sq_norms = np.sum(xc * xc, axis=1)
        s_frob_sq = float(np.sum(s * s))
        b2_raw = (float(np.mean(row_sq_norms**2)) - s_frob_sq) / float(n * d)
        b2 = min(d2, max(0.0, b2_raw))
        lam = float(np.clip(b2 / d2, min_shrinkage, 1.0))
    cov = (1.0 - lam) * s + lam * m * np.eye(d, dtype=np.float64)
    return mu, cov, lam


def conformal_threshold(cal_anomaly_scores: np.ndarray, alpha: float = 0.05) -> float:
    """Garantiza P(score_legit > q_hat) <= alpha en muestras intercambiables."""
    scores = np.sort(np.asarray(cal_anomaly_scores, dtype=np.float64).reshape(-1))
    n_cal = scores.shape[0]
    if n_cal < 1:
        raise ValueError("cal_anomaly_scores no puede estar vacío")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha debe estar en (0, 1), recibido: {alpha}")
    k_1based = min(n_cal, max(1, math.ceil((n_cal + 1) * (1.0 - alpha))))
    return float(scores[k_1based - 1])


def _as_matrix(rows: np.ndarray, name: str, *, min_rows: int = 1) -> np.ndarray:
    array = np.asarray(rows, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] < min_rows or array.shape[1] < 1:
        raise ValueError(f"{name} debe ser 2D con N >= {min_rows}, recibido: {array.shape}")
    return array


def _aligned_rows(chunks: list[TextChunk], chunk_vecs: np.ndarray, dimension: int | None) -> np.ndarray:
    array = np.asarray(chunk_vecs, dtype=np.float64)
    if array.ndim != 2:
        raise ValueError(f"chunk_vecs debe ser 2D, recibido: {array.shape}")
    if array.shape[0] != len(chunks):
        raise ValueError(
            f"chunks ({len(chunks)}) y vectores ({array.shape[0]}) no coinciden"
        )
    if dimension is not None and array.shape[0] > 0 and array.shape[1] != dimension:
        raise ValueError(f"dimension {array.shape[1]} != modelo {dimension}")
    return array


class M1_DdiBoxesBaseline:
    """Cajas [lo, hi] de ddi-fw v0.4.0, usadas en solo lectura."""

    def __init__(self) -> None:
        self.candados: dict[str, object] = {}
        self.policy: Policy | None = None
        self.dimension: int | None = None

    def fit(self, matrices: dict[str, np.ndarray]) -> None:
        if "python" not in matrices:
            raise ValueError("M1 requiere la matriz 'python'")
        ordered: dict[str, np.ndarray] = {}
        python = _as_matrix(matrices["python"], "python")
        ordered["python"] = python
        for name, rows in matrices.items():
            if name == "python":
                continue
            ordered[name] = _as_matrix(rows, name)
        dimension = python.shape[1]
        for name, rows in ordered.items():
            if rows.shape[1] != dimension:
                raise ValueError(f"{name} tiene dimension {rows.shape[1]} != {dimension}")
        ruido = RUIDO_UNIVERSAL_BGE_M3 if dimension == 1024 else None
        pairs = [("python", name) for name in ordered if name != "python"]
        self.candados = candados_canonicos(
            ordered,
            pairs=pairs,
            ruido_indices=ruido,
            modo_espectral=True,
            quorum_ratio=0.10,
        )
        self.policy = Policy(
            allowed="python",
            forbidden=frozenset(name for name in ordered if name != "python"),
        )
        self.dimension = dimension

    def score_sample(self, chunks: list[TextChunk], chunk_vecs: np.ndarray) -> float:
        rows = _aligned_rows(chunks, chunk_vecs, self.dimension)
        if rows.shape[0] == 0:
            return 0.0
        per_chunk = [self._chunk_min_votes(row) for row in rows]
        return float(-min(per_chunk))

    def predict_breach(self, chunks: list[TextChunk], chunk_vecs: np.ndarray) -> bool:
        if self.policy is None:
            raise RuntimeError("M1 no fue entrenado")
        rows = _aligned_rows(chunks, chunk_vecs, self.dimension)
        if rows.shape[0] == 0:
            return True
        for row in rows:
            decision = decide(np.asarray(row, dtype=np.float32), self.candados, self.policy)
            if decision.verdict == "BREACH":
                return True
        return False

    def _chunk_min_votes(self, vector: np.ndarray) -> float:
        votes: list[float] = []
        penalize = False
        for candado in self.candados.values():
            label, ballot = etiquetar_fila(vector, candado.hoja)
            _label, metrics = evaluar_corte_espectral(
                ballot,
                ejes_trigo=candado.ejes_trigo,
                quorum_min=candado.quorum_min,
                ruido_indices=candado.hoja.ruido_indices,
            )
            votes.append(float(metrics["votos_trigo_a"]))
            if label in {"right", "split"}:
                penalize = True
        base = float(min(votes)) if votes else 0.0
        if penalize:
            base -= 1000.0
        return base


class M2_CosineMargin:
    """Margen de coseno contra el centroide python y los dominios vistos."""

    def __init__(self) -> None:
        self.mu_python: np.ndarray | None = None
        self.mu_negative: dict[str, np.ndarray] = {}
        self.q_hat: float | None = None
        self.dimension: int | None = None

    def fit(
        self,
        positive: np.ndarray,
        negative_by_domain: dict[str, np.ndarray],
        calibration: CalGroup,
    ) -> None:
        pos = _as_matrix(positive, "positive")
        if not negative_by_domain:
            raise ValueError("M2 requiere al menos un dominio negativo")
        centroids: dict[str, np.ndarray] = {}
        for name, rows in negative_by_domain.items():
            matrix = _as_matrix(rows, name)
            if matrix.shape[1] != pos.shape[1]:
                raise ValueError(f"{name} tiene dimension distinta de python")
            centroids[name] = _l2_centroid(matrix)
        self.mu_python = _l2_centroid(pos)
        self.mu_negative = centroids
        self.dimension = int(pos.shape[1])
        self.q_hat = conformal_threshold(self._calibration_scores(calibration), alpha=0.05)

    def score_sample(self, chunks: list[TextChunk], chunk_vecs: np.ndarray) -> float:
        rows = _aligned_rows(chunks, chunk_vecs, self.dimension)
        if rows.shape[0] == 0:
            return 0.0
        return float(max(self._margin(row) for row in rows))

    def predict_breach(self, chunks: list[TextChunk], chunk_vecs: np.ndarray) -> bool:
        if self.q_hat is None:
            raise RuntimeError("M2 no fue calibrado")
        return self.score_sample(chunks, chunk_vecs) > self.q_hat

    def _margin(self, vector: np.ndarray) -> float:
        if self.mu_python is None:
            raise RuntimeError("M2 no fue entrenado")
        hat = _l2(np.asarray(vector, dtype=np.float64))
        positive = float(np.dot(hat, self.mu_python))
        negative = max(float(np.dot(hat, centroid)) for centroid in self.mu_negative.values())
        return negative - positive

    def _calibration_scores(self, calibration: CalGroup) -> np.ndarray:
        if not calibration:
            raise ValueError("M2 requiere muestras de calibracion")
        return np.asarray(
            [self.score_sample(chunks, vectors) for chunks, vectors in calibration],
            dtype=np.float64,
        )


class M3_WhitenedSpectralSubspace:
    """Subespacio blanqueado: Fisher + residuo PCA + split conformal."""

    def __init__(self) -> None:
        self.mu_pos: np.ndarray | None = None
        self.w_hat: np.ndarray | None = None
        self.u_k: np.ndarray | None = None
        self.gamma: np.ndarray | None = None
        self.medians: np.ndarray | None = None
        self.iqrs: np.ndarray | None = None
        self.q_hat: float | None = None
        self.dimension: int | None = None
        self.shrinkage_pos: float | None = None
        self.shrinkage_neg: float | None = None
        self.subspace_rank: int | None = None

    def fit(self, positive: np.ndarray, negative: np.ndarray, calibration: CalGroup) -> None:
        self._fit_geometry(positive, negative)
        self.q_hat = conformal_threshold(self._calibration_scores(calibration), alpha=0.05)

    def score_sample(self, chunks: list[TextChunk], chunk_vecs: np.ndarray) -> float:
        rows = _aligned_rows(chunks, chunk_vecs, self.dimension)
        if rows.shape[0] == 0:
            return 0.0
        return float(np.max(self.chunk_scores(rows)))

    def predict_breach(self, chunks: list[TextChunk], chunk_vecs: np.ndarray) -> bool:
        if self.q_hat is None:
            raise RuntimeError("M3 no fue calibrado")
        return self.score_sample(chunks, chunk_vecs) > self.q_hat

    def chunk_scores(self, rows: np.ndarray) -> np.ndarray:
        return self._eeb_scores(_as_matrix(rows, "rows"))

    def _fit_geometry(self, positive: np.ndarray, negative: np.ndarray) -> None:
        x_pos = _as_matrix(positive, "positive", min_rows=2)
        x_neg = _as_matrix(negative, "negative", min_rows=2)
        if x_pos.shape[1] != x_neg.shape[1]:
            raise ValueError("positive y negative tienen distinta dimension")
        mu_pos, cov_pos, lam_pos = ledoit_wolf_covariance(x_pos)
        mu_neg, cov_neg, lam_neg = ledoit_wolf_covariance(x_neg)
        n_pos = float(x_pos.shape[0])
        n_neg = float(x_neg.shape[0])
        sigma_w = (n_pos * cov_pos + n_neg * cov_neg) / (n_pos + n_neg)
        w_raw = np.linalg.solve(sigma_w, mu_pos - mu_neg)
        self.w_hat = w_raw / max(float(np.linalg.norm(w_raw)), 1e-12)
        self.mu_pos = mu_pos
        centered = x_pos - mu_pos
        _left, singular, vt = np.linalg.svd(centered, full_matrices=False)
        rank = min(48, vt.shape[0] - 1, vt.shape[1])
        if rank < 1:
            raise ValueError("no hay rango suficiente para el subespacio positivo")
        self.u_k = np.asarray(vt[:rank].T, dtype=np.float64)
        self.gamma = (singular[:rank] ** 2) / max(1, x_pos.shape[0] - 1) + 1e-4
        self.subspace_rank = int(rank)
        raw = self._raw_components(x_pos)
        self.medians = np.median(raw, axis=0)
        q75 = np.percentile(raw, 75, axis=0)
        q25 = np.percentile(raw, 25, axis=0)
        self.iqrs = np.maximum(q75 - q25, 1e-6)
        self.dimension = int(x_pos.shape[1])
        self.shrinkage_pos = float(lam_pos)
        self.shrinkage_neg = float(lam_neg)

    def _calibration_scores(self, calibration: CalGroup) -> np.ndarray:
        if not calibration:
            raise ValueError("M3 requiere muestras de calibracion")
        return np.asarray(
            [self.score_sample(chunks, vectors) for chunks, vectors in calibration],
            dtype=np.float64,
        )

    def _raw_components(self, rows: np.ndarray) -> np.ndarray:
        if self.mu_pos is None or self.w_hat is None or self.u_k is None or self.gamma is None:
            raise RuntimeError("M3 no tiene geometria ajustada")
        matrix = np.asarray(rows, dtype=np.float64)
        fisher = -(matrix @ self.w_hat)
        centered = matrix - self.mu_pos
        projected = centered @ self.u_k
        parallel = np.sum((projected**2) / self.gamma, axis=1)
        orthogonal = np.maximum(
            0.0, np.sum(centered**2, axis=1) - np.sum(projected**2, axis=1)
        )
        return np.column_stack((fisher, parallel, orthogonal))

    def _eeb_scores(self, rows: np.ndarray) -> np.ndarray:
        if self.medians is None or self.iqrs is None:
            raise RuntimeError("M3 no estandarizo las componentes")
        standardized = (self._raw_components(rows) - self.medians) / self.iqrs
        return 0.50 * standardized[:, 0] + 0.20 * standardized[:, 1] + 0.30 * standardized[:, 2]


class M4_HybridAstSpectral(M3_WhitenedSpectralSubspace):
    """M3 con descuento en AST válido y penalización en código ajeno."""

    def score_sample(self, chunks: list[TextChunk], chunk_vecs: np.ndarray) -> float:
        rows = _aligned_rows(chunks, chunk_vecs, self.dimension)
        if rows.shape[0] == 0:
            return 0.0
        base = self._eeb_scores(rows)
        adjusted = np.array(
            [self._adjust(chunk, float(score)) for chunk, score in zip(chunks, base, strict=True)],
            dtype=np.float64,
        )
        return float(np.max(adjusted))

    @staticmethod
    def _adjust(chunk: TextChunk, score: float) -> float:
        if chunk.is_valid_python_ast:
            return score - 1.5
        if chunk.kind in {"fenced_code", "foreign_code"}:
            return score + 6.0
        return score


def _l2(vector: np.ndarray) -> np.ndarray:
    array = np.asarray(vector, dtype=np.float64).reshape(-1)
    norm = float(np.linalg.norm(array))
    if norm < 1e-12:
        return array
    return array / norm


def _l2_centroid(rows: np.ndarray) -> np.ndarray:
    return _l2(np.mean(_unit_rows(rows), axis=0))


def _unit_rows(rows: np.ndarray) -> np.ndarray:
    matrix = np.asarray(rows, dtype=np.float64)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, 1e-12)

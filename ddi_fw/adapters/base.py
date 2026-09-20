"""Base abstractions for embedding adapters."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float32]


@runtime_checkable
class BaseEmbedder(Protocol):
    model_id: str
    dimension: int

    def embed_text(self, text: str) -> FloatArray: ...

    def embed_batch(self, texts: list[str]) -> FloatArray: ...


def l2_normalize(matrix: npt.NDArray[np.floating]) -> FloatArray:
    rows = np.asarray(matrix, dtype=np.float32)
    if rows.ndim == 1:
        norm = float(np.linalg.norm(rows))
        if norm <= 1e-12:
            return rows
        return (rows / norm).astype(np.float32)
    norms = np.linalg.norm(rows, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return (rows / norms).astype(np.float32)


def matryoshka_cut(matrix: npt.NDArray[np.floating], dim: int) -> FloatArray:
    rows = np.asarray(matrix, dtype=np.float32)
    if dim < 1 or dim > rows.shape[-1]:
        raise ValueError(f"corte MRL {dim} fuera de rango 1..{rows.shape[-1]}")
    return l2_normalize(rows[..., :dim])


class _SentenceTransformerEmbedder:
    model_id: str
    dimension: int
    _output_dim: int | None
    _trust_remote_code: bool
    _prefix: str
    _model: object | None

    def __init__(
        self,
        model_id: str,
        dimension: int,
        *,
        output_dim: int | None = None,
        trust_remote_code: bool = False,
        prefix: str = "",
    ) -> None:
        self.model_id = model_id
        self.dimension = dimension
        self._output_dim = output_dim
        self._trust_remote_code = trust_remote_code
        self._prefix = prefix
        self._model = None

    def _prepare_load(self) -> dict[str, object]:
        """Extra kwargs for SentenceTransformer(...). Subclasses may patch the Hub first."""
        return {}

    def _load(self) -> object:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            extra = self._prepare_load()
            self._model = SentenceTransformer(
                self.model_id,
                trust_remote_code=self._trust_remote_code,
                **extra,
            )
        return self._model

    def _prepare(self, texts: list[str]) -> list[str]:
        if not self._prefix:
            return texts
        return [self._prefix + text for text in texts]

    def embed_batch(self, texts: list[str]) -> FloatArray:
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        model = self._load()
        vectors = np.asarray(
            model.encode(self._prepare(texts), convert_to_numpy=True, normalize_embeddings=False),
            dtype=np.float32,
        )
        if self._output_dim is not None:
            vectors = matryoshka_cut(vectors, self._output_dim)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"{self.model_id} produjo dim {vectors.shape[1]}, esperaba {self.dimension}"
            )
        return vectors.astype(np.float32)

    def embed_text(self, text: str) -> FloatArray:
        return self.embed_batch([text])[0]

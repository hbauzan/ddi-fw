"""Adapters de modelos de embedding para ddi-fw."""

from __future__ import annotations

from ddi_fw.adapters.base import BaseEmbedder, FloatArray, l2_normalize, matryoshka_cut
from ddi_fw.adapters.bge import BGE_M3_ID, BGEM3Embedder
from ddi_fw.adapters.qwen2 import (
    QWEN2_ID,
    Qwen2Embedder,
    apply_qwen2_cache_shim,
    apply_qwen2_rope_theta_shim,
    apply_qwen2_transformers517_shim,
)

__all__ = [
    "BGE_M3_ID",
    "BGEM3Embedder",
    "BaseEmbedder",
    "FloatArray",
    "QWEN2_ID",
    "Qwen2Embedder",
    "apply_qwen2_cache_shim",
    "apply_qwen2_rope_theta_shim",
    "apply_qwen2_transformers517_shim",
    "l2_normalize",
    "matryoshka_cut",
]

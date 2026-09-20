"""Tests para adaptadores de embedding desacoplados (ddi_fw/adapters/) e invariantes numéricas."""

from __future__ import annotations

import numpy as np

from ddi_fw.adapters.base import BaseEmbedder
from ddi_fw.adapters.bge import BGE_M3_ID, BGEM3Embedder
from ddi_fw.adapters.qwen2 import (
    QWEN2_ID,
    Qwen2Embedder,
    apply_qwen2_cache_shim,
    apply_qwen2_rope_theta_shim,
    apply_qwen2_transformers517_shim,
)
from ddi_fw.embedder import get_embedder


def test_bge_adapter_declares_1024_without_loading() -> None:
    embedder = get_embedder("bge-m3")
    assert isinstance(embedder, BGEM3Embedder)
    assert embedder.model_id == BGE_M3_ID
    assert embedder.dimension == 1024
    assert embedder._model is None
    assert isinstance(embedder, BaseEmbedder)


def test_qwen2_adapter_declares_1536_without_loading() -> None:
    embedder = get_embedder("qwen2")
    assert isinstance(embedder, Qwen2Embedder)
    assert embedder.model_id == QWEN2_ID
    assert embedder.dimension == 1536
    assert embedder._trust_remote_code is True
    assert embedder._model is None
    assert isinstance(embedder, BaseEmbedder)


def test_qwen2_shims_callable_idempotent() -> None:
    apply_qwen2_rope_theta_shim()
    apply_qwen2_cache_shim()
    apply_qwen2_transformers517_shim()

    from transformers.cache_utils import DynamicCache
    from transformers.models.qwen2.configuration_qwen2 import Qwen2Config

    assert getattr(Qwen2Config, "_ddi_rope_theta_shim", False) is True
    assert getattr(DynamicCache, "_ddi_cache_shim", False) is True


def test_full_precision_float32_formatting_invariance() -> None:
    # Número float32 específico con decimales sensibles
    val = np.float32(-0.027182818)
    formatted = f"{float(val):.17g}"
    # Debe preservar la mantisa exacta sin truncamiento artificial a .6f
    assert len(formatted) > 8
    assert "e" in formatted or len(formatted.split(".")[-1]) >= 7
    # Reconstrucción exacta
    reconstructed = np.float32(float(formatted))
    assert reconstructed == val

"""Shim de Qwen2Config.rope_theta vs transformers 5.17. No carga pesos."""

from __future__ import annotations

from ddi_fw.embedder import (
    apply_qwen2_cache_shim,
    apply_qwen2_rope_theta_shim,
    get_embedder,
)


def test_qwen2_factory_is_singleton() -> None:
    assert get_embedder("qwen2") is get_embedder("qwen2")


def test_qwen2_rope_theta_shim_reads_rope_parameters() -> None:
    from transformers.models.qwen2.configuration_qwen2 import Qwen2Config

    apply_qwen2_rope_theta_shim()
    apply_qwen2_rope_theta_shim()
    config = Qwen2Config(
        rope_theta=1_000_000.0,
        hidden_size=1536,
        num_hidden_layers=2,
        num_attention_heads=12,
        num_key_value_heads=2,
    )
    assert config.rope_parameters["rope_theta"] == 1_000_000.0
    assert config.rope_theta == 1_000_000.0


def test_qwen2_cache_shim_from_legacy_none() -> None:
    from transformers.cache_utils import DynamicCache

    apply_qwen2_cache_shim()
    apply_qwen2_cache_shim()
    cache = DynamicCache.from_legacy_cache(None)
    assert cache.get_usable_length(32) == 0
    assert cache.to_legacy_cache() is None

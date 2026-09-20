"""Adapter para Alibaba-NLP/gte-Qwen2-1.5B-instruct (1536-D).

Aplica shims para compatibilidad con transformers >= 5.17:
1. `rope_theta` retro-compatibilidad en Qwen2Config.
2. `DynamicCache` capa de compatibilidad (from_legacy_cache, get_usable_length).
3. Carga en fp16 para contención de memoria en el anfitrión.
"""

from __future__ import annotations

from ddi_fw.adapters.base import _SentenceTransformerEmbedder

QWEN2_ID = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"


def apply_qwen2_rope_theta_shim() -> None:
    """transformers 5.17 moved rope_theta into rope_parameters; Hub custom_code still reads config.rope_theta."""
    from transformers.models.qwen2.configuration_qwen2 import Qwen2Config

    if getattr(Qwen2Config, "_ddi_rope_theta_shim", False):
        return

    def _rope_theta(self: object) -> float:
        params = getattr(self, "rope_parameters", None) or {}
        if isinstance(params, dict) and params.get("rope_theta") is not None:
            return float(params["rope_theta"])
        return 1_000_000.0

    Qwen2Config.rope_theta = property(_rope_theta)
    Qwen2Config._ddi_rope_theta_shim = True


def apply_qwen2_cache_shim() -> None:
    """Hub custom_code (transformers 4.41) calls DynamicCache APIs removed in 5.17."""
    from transformers.cache_utils import DynamicCache

    if getattr(DynamicCache, "_ddi_cache_shim", False):
        return

    @classmethod
    def from_legacy_cache(cls, past_key_values: object = None, **_kwargs: object) -> object:
        if past_key_values is None:
            return cls()
        if isinstance(past_key_values, cls):
            return past_key_values
        return cls(ddp_cache_data=past_key_values)

    def get_usable_length(self: object, new_seq_length: int, layer_idx: int = 0) -> int:
        del new_seq_length
        get_seq = getattr(self, "get_seq_length", None)
        if callable(get_seq):
            return int(get_seq(layer_idx))
        return 0

    def to_legacy_cache(self: object) -> object:
        return None

    DynamicCache.from_legacy_cache = from_legacy_cache
    DynamicCache.get_usable_length = get_usable_length
    DynamicCache.to_legacy_cache = to_legacy_cache
    DynamicCache._ddi_cache_shim = True


def apply_qwen2_transformers517_shim() -> None:
    apply_qwen2_rope_theta_shim()
    apply_qwen2_cache_shim()


class Qwen2Embedder(_SentenceTransformerEmbedder):
    """1.5B. fp16 so a 16 GiB host can load it. Singleton: one live copy per process."""

    _instance: Qwen2Embedder | None = None

    def __init__(self) -> None:
        super().__init__(QWEN2_ID, 1536, trust_remote_code=True)

    @classmethod
    def instance(cls) -> Qwen2Embedder:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _prepare_load(self) -> dict[str, object]:
        import torch

        apply_qwen2_transformers517_shim()
        return {
            "model_kwargs": {"torch_dtype": torch.float16},
            "config_kwargs": {"use_cache": False},
        }

    def _load(self) -> object:
        model = super()._load()
        first = model[0]
        auto = getattr(first, "auto_model", None)
        if auto is not None and hasattr(auto, "config"):
            auto.config.use_cache = False
        return model

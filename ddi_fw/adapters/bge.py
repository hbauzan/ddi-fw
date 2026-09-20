"""Adapter para BAAI/bge-m3 (1024-D, dense FP32)."""

from __future__ import annotations

from ddi_fw.adapters.base import _SentenceTransformerEmbedder

BGE_M3_ID = "BAAI/bge-m3"


class BGEM3Embedder(_SentenceTransformerEmbedder):
    _instance: BGEM3Embedder | None = None

    def __init__(self) -> None:
        super().__init__(BGE_M3_ID, 1024)

    @classmethod
    def instance(cls) -> BGEM3Embedder:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

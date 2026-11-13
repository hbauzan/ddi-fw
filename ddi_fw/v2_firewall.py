"""Inspección productiva M4 sobre turnos no confiables, con caché LRU por chunk."""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from ddi_fw.adapters.base import BaseEmbedder
from ddi_fw.lab_v2.chunker import TextChunk, extract_chunks
from ddi_fw.lab_v2.models import M4_HybridAstSpectral

_DEFAULT_ROLES = frozenset({"user", "system", "developer", "tool"})


def chunk_cache_key(chunk: TextChunk) -> str:
    payload = f"{chunk.kind}\0{int(chunk.is_valid_python_ast)}\0{chunk.text}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ChunkAudit:
    chunk_kind: str
    is_valid_python_ast: bool
    start_line: int
    end_line: int
    score: float
    cached: bool
    role: str = "user"
    message_index: int = 0


@dataclass(frozen=True)
class V2FirewallResult:
    verdict: Literal["PASS", "BREACH"]
    max_score: float
    threshold_q_hat: float
    chunk_count: int
    cache_hits: int
    cache_misses: int
    reason: str
    chunks: tuple[ChunkAudit, ...] = ()

    @property
    def audit(self) -> list[dict[str, object]]:
        return [
            {
                "chunk_kind": chunk.chunk_kind,
                "is_valid_python_ast": chunk.is_valid_python_ast,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "score": float(chunk.score),
                "cached": chunk.cached,
                "role": chunk.role,
                "message_index": chunk.message_index,
            }
            for chunk in self.chunks
        ]


class SpectralAstFirewall:
    """Fail-closed. El texto crudo no sale en la auditoría."""

    def __init__(
        self,
        model: M4_HybridAstSpectral,
        embedder: BaseEmbedder,
        *,
        max_cache_entries: int = 4096,
    ) -> None:
        if model.q_hat is None or model.dimension is None:
            raise ValueError("modelo sin umbral conformal")
        if int(model.dimension) != int(embedder.dimension):
            raise ValueError(
                f"dimension del embedder {embedder.dimension} != modelo {model.dimension}"
            )
        if max_cache_entries < 1:
            raise ValueError("max_cache_entries debe ser >= 1")
        self._model = model
        self._embedder = embedder
        self._max_cache_entries = int(max_cache_entries)
        self._cache: OrderedDict[str, float] = OrderedDict()

    def inspect_text(
        self,
        text: str | None,
        *,
        role: str = "user",
        message_index: int = 0,
    ) -> V2FirewallResult:
        if text is None or not str(text).strip():
            return self._closed("empty_chunks")
        chunks = extract_chunks(str(text))
        if not chunks:
            return self._closed("empty_chunks")
        keys = [chunk_cache_key(chunk) for chunk in chunks]
        scores: list[float | None] = [None] * len(chunks)
        cached_flags = [False] * len(chunks)
        misses: list[int] = []
        for index, key in enumerate(keys):
            if key in self._cache:
                self._cache.move_to_end(key)
                scores[index] = float(self._cache[key])
                cached_flags[index] = True
            else:
                misses.append(index)
        if misses:
            try:
                rows = self._embed_misses([chunks[index].text for index in misses])
                prose_base = self._model._eeb_scores_prose(rows)
                polytope_base = self._model._eeb_scores(rows)
            except Exception as exc:
                return V2FirewallResult(
                    verdict="BREACH",
                    max_score=0.0,
                    threshold_q_hat=float(self._model.q_hat),
                    chunk_count=len(chunks),
                    cache_hits=sum(cached_flags),
                    cache_misses=len(misses),
                    reason=f"embedder_down:{exc.__class__.__name__}",
                )
            for local, index in enumerate(misses):
                chunk = chunks[index]
                base_score = (
                    prose_base[local] if chunk.is_valid_python_ast else polytope_base[local]
                )
                score = float(self._model._adjust(chunk, float(base_score)))
                scores[index] = score
                self._remember(keys[index], score)
        audits = tuple(
            ChunkAudit(
                chunk_kind=chunk.kind,
                is_valid_python_ast=chunk.is_valid_python_ast,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                score=float(scores[index]),
                cached=cached_flags[index],
                role=role,
                message_index=message_index,
            )
            for index, chunk in enumerate(chunks)
        )
        max_score = float(max(item.score for item in audits))
        breach = max_score > float(self._model.q_hat)
        return V2FirewallResult(
            verdict="BREACH" if breach else "PASS",
            max_score=max_score,
            threshold_q_hat=float(self._model.q_hat),
            chunk_count=len(audits),
            cache_hits=sum(cached_flags),
            cache_misses=len(misses),
            reason="conformal_threshold_exceeded" if breach else "all_chunks_within_conformal_bound",
            chunks=audits,
        )

    def inspect_messages(
        self,
        messages: list[dict[str, Any]],
        *,
        inspect_roles: frozenset[str] = _DEFAULT_ROLES,
    ) -> V2FirewallResult:
        if not isinstance(messages, list):
            return self._closed("missing_user_message")
        selected: list[tuple[int, str, str]] = []
        user_present = False
        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                continue
            role = str(message.get("role", ""))
            text = _message_text(message)
            if role == "user" and text.strip():
                user_present = True
            if role in inspect_roles and text.strip():
                selected.append((index, role, text))
        if not user_present:
            return self._closed("missing_user_message")
        if not selected:
            return self._closed("empty_chunks")
        parts = [
            self.inspect_text(text, role=role, message_index=index)
            for index, role, text in selected
        ]
        return self._merge(parts)

    def _embed_misses(self, texts: list[str]) -> np.ndarray:
        rows = np.asarray(self._embedder.embed_batch(texts), dtype=np.float64)
        expected = (len(texts), int(self._model.dimension))
        if rows.ndim != 2 or rows.shape != expected:
            raise ValueError(f"embed_batch shape {rows.shape} != {expected}")
        return rows

    def _remember(self, key: str, score: float) -> None:
        self._cache[key] = float(score)
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_cache_entries:
            self._cache.popitem(last=False)

    def _closed(self, reason: str) -> V2FirewallResult:
        return V2FirewallResult(
            verdict="BREACH",
            max_score=0.0,
            threshold_q_hat=float(self._model.q_hat),
            chunk_count=0,
            cache_hits=0,
            cache_misses=0,
            reason=reason,
        )

    def _merge(self, parts: list[V2FirewallResult]) -> V2FirewallResult:
        chunks = tuple(chunk for part in parts for chunk in part.chunks)
        if chunks:
            max_score = float(max(chunk.score for chunk in chunks))
        else:
            max_score = float(max(part.max_score for part in parts))
        reasons = [part.reason for part in parts]
        breach = any(part.verdict == "BREACH" for part in parts)
        if not breach:
            reason = "all_chunks_within_conformal_bound"
        elif any(item.startswith("embedder_down:") for item in reasons):
            reason = next(item for item in reasons if item.startswith("embedder_down:"))
        elif "conformal_threshold_exceeded" in reasons:
            reason = "conformal_threshold_exceeded"
        elif "empty_chunks" in reasons:
            reason = "empty_chunks"
        else:
            reason = next(item for item in reasons if item != "all_chunks_within_conformal_bound")
        return V2FirewallResult(
            verdict="BREACH" if breach else "PASS",
            max_score=max_score,
            threshold_q_hat=float(self._model.q_hat),
            chunk_count=sum(part.chunk_count for part in parts),
            cache_hits=sum(part.cache_hits for part in parts),
            cache_misses=sum(part.cache_misses for part in parts),
            reason=reason,
            chunks=chunks,
        )


def _message_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(str(part.get("text", "")))
        return "".join(parts)
    return ""

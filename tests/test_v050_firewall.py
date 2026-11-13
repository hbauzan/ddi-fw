"""Slice 2 — SpectralAstFirewall multi-turno con caché SHA-256."""

from __future__ import annotations

import hashlib
import json

import numpy as np

from ddi_fw.lab_v2.chunker import TextChunk, extract_chunks
from ddi_fw.lab_v2.models import M4_HybridAstSpectral
from ddi_fw.v2_firewall import (
    ChunkAudit,
    SpectralAstFirewall,
    V2FirewallResult,
    chunk_cache_key,
)

_BENIGN = (
    "El muelle norte recibio pallets secos durante el turno de la manana sin novedades."
)
_ATTACK = (
    "El sensor del anden marco una alarma continua y detuvo la cinta de salida."
)


class _TableEmbedder:
    def __init__(self, table: dict[str, np.ndarray], *, dimension: int) -> None:
        self.table = table
        self.dimension = dimension
        self.model_id = "table"
        self.batches = 0

    def embed_text(self, text: str) -> np.ndarray:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        self.batches += 1
        rows = []
        for text in texts:
            if text not in self.table:
                raise KeyError(text)
            rows.append(np.asarray(self.table[text], dtype=np.float32))
        if not rows:
            return np.zeros((0, self.dimension), dtype=np.float32)
        return np.stack(rows, axis=0)


class _DownEmbedder:
    dimension = 16
    model_id = "down"

    def embed_text(self, text: str) -> np.ndarray:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        raise RuntimeError("encoder offline")


def _separable_model() -> tuple[M4_HybridAstSpectral, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    dimension = 16
    positive = rng.normal(loc=0.0, scale=0.02, size=(48, dimension))
    positive[:, 0] += 5.0
    negative = rng.normal(loc=0.0, scale=0.02, size=(48, dimension))
    negative[:, 1] += 5.0
    groups: list[tuple[list[TextChunk], np.ndarray]] = []
    for index in range(16):
        chunk = TextChunk(
            text=f"Calibracion positiva {index} del muelle seco con texto suficiente.",
            kind="prose_window",
            is_valid_python_ast=False,
            start_line=1,
            end_line=1,
        )
        vector = rng.normal(loc=0.0, scale=0.02, size=(1, dimension))
        vector[0, 0] += 5.0
        groups.append(([chunk], vector))
    model = M4_HybridAstSpectral()
    model.fit(positive, negative, groups)
    pos_vec = np.mean(positive, axis=0)
    neg_vec = np.mean(negative, axis=0)
    return model, pos_vec, neg_vec


def _firewall(
    *,
    max_cache_entries: int = 8,
) -> tuple[SpectralAstFirewall, _TableEmbedder, str, str]:
    model, pos_vec, neg_vec = _separable_model()
    benign_chunks = extract_chunks(_BENIGN)
    attack_chunks = extract_chunks(_ATTACK)
    assert len(benign_chunks) == 1
    assert len(attack_chunks) == 1
    table = {
        benign_chunks[0].text: pos_vec,
        attack_chunks[0].text: neg_vec,
    }
    embedder = _TableEmbedder(table, dimension=16)
    firewall = SpectralAstFirewall(model, embedder, max_cache_entries=max_cache_entries)
    return firewall, embedder, benign_chunks[0].text, attack_chunks[0].text


def test_cache_key_binds_kind_ast_flag_and_text() -> None:
    prose = TextChunk("mismo", "prose_window", False, 1, 1)
    foreign = TextChunk("mismo", "foreign_code", False, 1, 1)
    python = TextChunk("mismo", "python_ast", True, 1, 1)
    assert chunk_cache_key(prose) != chunk_cache_key(foreign)
    assert chunk_cache_key(prose) != chunk_cache_key(python)
    expected = hashlib.sha256(f"prose_window\0{0}\0mismo".encode()).hexdigest()
    assert chunk_cache_key(prose) == expected


def test_constructor_rejects_uncalibrated_model_and_dimension_mismatch() -> None:
    model, _pos, _neg = _separable_model()
    embedder = _firewall()[1]
    bare = M4_HybridAstSpectral()
    try:
        SpectralAstFirewall(bare, embedder)
        raise AssertionError("debio rechazar q_hat ausente")
    except ValueError:
        pass
    model.dimension = 4
    try:
        SpectralAstFirewall(model, embedder)
        raise AssertionError("debio rechazar dimension distinta")
    except ValueError:
        pass


def test_empty_input_and_embedder_down_fail_closed() -> None:
    firewall, _embedder, _benign, _attack = _firewall()
    for text in (None, "", "   ", "??"):
        result = firewall.inspect_text(text)  # type: ignore[arg-type]
        assert result.verdict == "BREACH"
        assert result.reason == "empty_chunks"
        assert result.chunk_count == 0
    down_model, _pos, _neg = _separable_model()
    down = SpectralAstFirewall(down_model, _DownEmbedder())
    failed = down.inspect_text(_BENIGN)
    assert failed.verdict == "BREACH"
    assert failed.reason == "embedder_down:RuntimeError"
    assert _BENIGN not in json.dumps(failed.audit)


def test_scores_cross_conformal_bound_and_cache_is_lru() -> None:
    firewall, embedder, benign_text, attack_text = _firewall(max_cache_entries=1)
    first = firewall.inspect_text(_BENIGN)
    assert first.verdict == "PASS"
    assert first.reason == "all_chunks_within_conformal_bound"
    assert first.cache_misses == 1
    assert first.cache_hits == 0
    assert first.max_score <= first.threshold_q_hat
    assert embedder.batches == 1
    second = firewall.inspect_text(_BENIGN)
    assert second.verdict == "PASS"
    assert second.cache_hits == 1
    assert second.cache_misses == 0
    assert second.chunks[0].cached is True
    assert embedder.batches == 1
    attack = firewall.inspect_text(_ATTACK)
    assert attack.verdict == "BREACH"
    assert attack.reason == "conformal_threshold_exceeded"
    assert attack.max_score > attack.threshold_q_hat
    assert attack.chunks[0].cached is False
    replay = firewall.inspect_text(_BENIGN)
    assert replay.cache_hits == 0
    assert replay.cache_misses == 1
    assert benign_text
    assert attack_text
    dumped = json.dumps(attack.audit)
    assert _ATTACK not in dumped
    assert "text" not in attack.audit[0]
    assert isinstance(attack.audit[0]["score"], float)


def test_messages_cover_untrusted_roles_and_share_the_cache() -> None:
    firewall, embedder, _benign, _attack = _firewall()
    missing = firewall.inspect_messages(
        [{"role": "system", "content": _ATTACK}, {"role": "assistant", "content": _BENIGN}]
    )
    assert missing.verdict == "BREACH"
    assert missing.reason == "missing_user_message"
    assert missing.chunk_count == 0

    listed = firewall.inspect_messages(
        [
            {
                "role": "user",
                "content": [{"type": "text", "text": _BENIGN}],
            }
        ]
    )
    assert listed.verdict == "PASS"
    assert listed.chunks[0].role == "user"
    assert listed.chunks[0].message_index == 0

    mixed = firewall.inspect_messages(
        [
            {"role": "system", "content": _ATTACK},
            {"role": "developer", "content": _BENIGN},
            {"role": "tool", "content": _BENIGN},
            {"role": "assistant", "content": _ATTACK},
            {"role": "user", "content": _BENIGN},
        ]
    )
    assert mixed.verdict == "BREACH"
    assert mixed.reason == "conformal_threshold_exceeded"
    roles = {chunk.role for chunk in mixed.chunks}
    assert roles == {"system", "developer", "tool", "user"}
    assert mixed.max_score == max(chunk.score for chunk in mixed.chunks)
    assert any(chunk.cached for chunk in mixed.chunks)
    assert embedder.batches >= 1
    blank_system = firewall.inspect_messages(
        [{"role": "system", "content": "  "}, {"role": "user", "content": _BENIGN}]
    )
    assert blank_system.verdict == "PASS"
    assert all(chunk.role == "user" for chunk in blank_system.chunks)
    assert isinstance(mixed, V2FirewallResult)
    assert isinstance(mixed.chunks[0], ChunkAudit)

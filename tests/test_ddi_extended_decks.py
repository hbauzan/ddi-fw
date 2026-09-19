"""Pruebas para mazos extendidos (≥2000 palabras) e integración de rompepepe."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ddi_fw.almas import ALMA_NAMES, load_almas
from ddi_fw.embedder import FakeEmbedder, embed_mazos
from scripts.audit_corpus_words import audit_deck

EXTENDED_DIR = Path("ddi_fw/data/extended")


def test_extended_decks_exist_and_reach_min_words():
    assert EXTENDED_DIR.is_dir(), "Directorio ddi_fw/data/extended debe existir"
    for alma in ALMA_NAMES:
        path = EXTENDED_DIR / f"{alma}.json"
        assert path.is_file(), f"Mazo extendido {alma}.json no encontrado"
        report = audit_deck(path)
        assert report["total_words"] >= 2000, (
            f"Mazo {alma} tiene {report['total_words']} palabras (exigido: >= 2000)"
        )
        assert report["clause_count"] >= 80, (
            f"Mazo {alma} tiene {report['clause_count']} cláusulas (esperado: >= 80)"
        )


def test_extended_decks_have_balanced_es_en():
    for alma in ALMA_NAMES:
        path = EXTENDED_DIR / f"{alma}.json"
        report = audit_deck(path)
        total = report["total_words"]
        es_pct = report["es_words"] / total
        en_pct = report["en_words"] / total
        assert 0.40 <= es_pct <= 0.60, f"Mazo {alma} porcentaje ES ({es_pct:.2%}) desbalanceado"
        assert 0.40 <= en_pct <= 0.60, f"Mazo {alma} porcentaje EN ({en_pct:.2%}) desbalanceado"


def test_extended_decks_embed_with_fake_cleanly():
    mazos = load_almas(EXTENDED_DIR)
    embedder = FakeEmbedder(dimension=16)
    matrices, ids = embed_mazos(mazos, embedder)
    for alma in ALMA_NAMES:
        assert alma in matrices
        mat = matrices[alma]
        assert mat.shape[0] >= 80
        assert mat.shape[1] == 16
        assert np.all(np.isfinite(mat)), f"Valores no finitos detectados en {alma}"
        assert len(ids[alma]) == mat.shape[0]


def test_rompepepe_local_bundle_integrity():
    rompepepe_dir = Path("tools/rompepepe")
    assert rompepepe_dir.is_dir(), "Directorio tools/rompepepe no encontrado"
    assert (rompepepe_dir / "config.py").is_file()
    assert (rompepepe_dir / "main.py").is_file()
    assert (rompepepe_dir / "client").is_dir()
    assert (rompepepe_dir / "engines").is_dir()
    assert (rompepepe_dir / "test_dataset" / "seed_corpus.json").is_file()

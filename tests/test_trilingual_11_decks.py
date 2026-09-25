"""Pruebas para los 11 mazos trilingües (Opción B: 5.500 cláusulas en el punto dulce)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.audit_corpus_words import (
    COMMON_DE_WORDS,
    COMMON_EN_WORDS,
    COMMON_ES_WORDS,
    audit_deck,
)
from scripts.generate_11_trilingual_decks import extract_words
from scripts.trilingual_generators import ALMAS_11

TRILINGUAL_DIR = Path("ddi_fw/data/trilingual")
STOPWORDS = COMMON_ES_WORDS | COMMON_EN_WORDS | COMMON_DE_WORDS


def test_11_trilingual_decks_exist_and_exact_clause_counts():
    assert TRILINGUAL_DIR.is_dir(), "Directorio ddi_fw/data/trilingual debe existir"
    total_clauses = 0

    for alma in ALMAS_11:
        path = TRILINGUAL_DIR / f"{alma}.json"
        assert path.is_file(), f"Mazo trilingüe {alma}.json no encontrado"

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        assert data["alma"] == alma
        assert data["n"] == 500
        clauses = data["clauses"]
        assert len(clauses) == 500

        es_clauses = [c for c in clauses if c.get("lang") == "es"]
        en_clauses = [c for c in clauses if c.get("lang") == "en"]
        de_clauses = [c for c in clauses if c.get("lang") == "de"]

        assert len(es_clauses) == 167, f"Mazo {alma} debe tener exactamente 167 cláusulas ES"
        assert len(en_clauses) == 167, f"Mazo {alma} debe tener exactamente 167 cláusulas EN"
        assert len(de_clauses) == 166, f"Mazo {alma} debe tener exactamente 166 cláusulas DE"

        total_clauses += len(clauses)

    assert total_clauses == 5500, (
        f"Total global de cláusulas ({total_clauses}) debe ser exactamente 5.500"
    )


def test_11_trilingual_decks_words_and_uniqueness():
    all_clause_ids: set[str] = set()

    for alma in ALMAS_11:
        path = TRILINGUAL_DIR / f"{alma}.json"
        report = audit_deck(path)
        assert report["total_words"] >= 8000, (
            f"Mazo {alma} tiene {report['total_words']} palabras (exigido: >= 8000)"
        )

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        ids = [c["id"] for c in data["clauses"]]
        texts = [c["text"] for c in data["clauses"]]

        assert len(set(ids)) == 500, f"IDs duplicados en {alma}"
        assert len(set(texts)) == 500, f"Cláusulas duplicadas en {alma}"

        for cid in ids:
            assert cid not in all_clause_ids, f"ID {cid} duplicado globalmente"
            all_clause_ids.add(cid)

    assert len(all_clause_ids) == 5500


def test_11_trilingual_decks_jaccard_content_isolation():
    """Valida la invariante canónica: Jaccard de contenido < 0.05 entre los 55 pares."""
    deck_words: dict[str, set[str]] = {}

    for alma in ALMAS_11:
        path = TRILINGUAL_DIR / f"{alma}.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        words = set()
        for c in data["clauses"]:
            words.update(extract_words(c["text"]))
        deck_words[alma] = words - STOPWORDS

    almas = list(ALMAS_11)
    pair_count = 0
    max_jac = 0.0

    for i in range(len(almas)):
        for j in range(i + 1, len(almas)):
            a1, a2 = almas[i], almas[j]
            s1, s2 = deck_words[a1], deck_words[a2]
            intersection = s1 & s2
            union = s1 | s2
            jac = len(intersection) / len(union) if union else 0.0
            pair_count += 1
            if jac > max_jac:
                max_jac = jac
            assert jac < 0.05, f"Violación Jaccard en par {a1} <-> {a2}: J={jac:.4f} >= 0.05"

    assert pair_count == 55
    assert max_jac < 0.05

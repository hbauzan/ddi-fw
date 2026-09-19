"""Auditoría léxica, conteo de palabras y detección de puentes semánticos para mazos DDI-FW."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORD_RE = re.compile(r"\b[^\W\d_]+(?:'[^\W\d_]+)?\b", re.UNICODE)

COMMON_EN_WORDS = {
    "the",
    "and",
    "to",
    "of",
    "a",
    "in",
    "is",
    "that",
    "for",
    "it",
    "as",
    "was",
    "with",
    "be",
    "by",
    "on",
    "not",
    "he",
    "i",
    "this",
    "are",
    "or",
    "an",
    "they",
    "which",
    "one",
    "you",
    "were",
    "her",
    "all",
    "she",
    "there",
    "would",
    "their",
    "we",
    "him",
    "been",
    "has",
    "when",
    "who",
    "will",
    "more",
    "no",
    "if",
    "out",
    "so",
    "said",
    "what",
    "up",
    "its",
    "about",
    "into",
    "than",
    "them",
    "can",
    "only",
    "other",
    "new",
    "some",
    "could",
    "time",
    "these",
    "two",
    "may",
    "then",
    "do",
    "first",
    "any",
    "my",
    "now",
    "such",
    "like",
    "our",
    "over",
    "man",
    "me",
    "even",
    "most",
    "made",
    "after",
    "also",
    "did",
    "many",
    "before",
    "must",
    "through",
}

COMMON_ES_WORDS = {
    "de",
    "la",
    "que",
    "el",
    "en",
    "y",
    "a",
    "los",
    "se",
    "del",
    "las",
    "un",
    "por",
    "con",
    "no",
    "una",
    "su",
    "para",
    "es",
    "al",
    "lo",
    "como",
    "más",
    "mas",
    "pero",
    "sus",
    "le",
    "ya",
    "o",
    "fue",
    "este",
    "ha",
    "si",
    "porque",
    "esta",
    "son",
    "entre",
    "está",
    "esta",
    "cuando",
    "muy",
    "sin",
    "sobre",
    "ser",
    "tiene",
    "también",
    "tambien",
    "me",
    "hasta",
    "hay",
    "donde",
    "quien",
    "desde",
    "todo",
    "nos",
    "durante",
    "todos",
    "uno",
    "les",
    "ni",
    "contra",
    "otros",
    "ese",
    "eso",
    "ante",
    "ellos",
    "e",
    "esto",
    "mí",
    "mi",
    "antes",
    "algunos",
    "qué",
    "que",
    "unos",
    "yo",
    "otro",
    "otras",
    "otra",
}


def classify_language(text: str) -> str:
    tokens = set(WORD_RE.findall(text.lower()))
    es_hits = len(tokens & COMMON_ES_WORDS)
    en_hits = len(tokens & COMMON_EN_WORDS)
    if es_hits > en_hits:
        return "es"
    if en_hits > es_hits:
        return "en"
    return "mixed_or_neutral"


def audit_deck(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    alma = data.get("alma", path.stem)
    clauses = data.get("clauses", [])

    total_words = 0
    words_set = set()
    clause_stats = []

    es_words = 0
    en_words = 0

    for c in clauses:
        txt = c["text"]
        tokens = WORD_RE.findall(txt.lower())
        wcount = len(tokens)
        total_words += wcount
        words_set.update(tokens)
        lang = classify_language(txt)
        if lang == "es":
            es_words += wcount
        elif lang == "en":
            en_words += wcount
        else:
            es_words += wcount // 2
            en_words += wcount - (wcount // 2)

        clause_stats.append(
            {
                "id": c.get("id"),
                "words": wcount,
                "lang": lang,
            }
        )

    return {
        "alma": alma,
        "path": str(path),
        "clause_count": len(clauses),
        "total_words": total_words,
        "unique_words": len(words_set),
        "words_set": words_set,
        "es_words": es_words,
        "en_words": en_words,
        "clause_stats": clause_stats,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Auditar conteo de palabras e idiomas en mazos DDI-FW."
    )
    parser.add_argument(
        "--dir", default="ddi_fw/data/extended", help="Directorio con archivos JSON de mazos"
    )
    parser.add_argument("--min-words", type=int, default=2000, help="Mínimo de palabras exigidas")
    args = parser.parse_args()

    deck_dir = Path(args.dir)
    if not deck_dir.exists():
        print(f"Error: Directorio {deck_dir} no existe.", file=sys.stderr)
        sys.exit(1)

    json_files = sorted(deck_dir.glob("*.json"))
    if not json_files:
        print(f"Error: No se encontraron archivos .json en {deck_dir}", file=sys.stderr)
        sys.exit(1)

    reports = []
    print("\n========================================================")
    print(f"  AUDITORÍA LÉXICA DDI-FW: {deck_dir}")
    print(f"  Requisito: Mínimo {args.min_words} palabras por mazo")
    print("========================================================\n")

    all_pass = True
    for jf in json_files:
        rep = audit_deck(jf)
        reports.append(rep)
        ok_min = rep["total_words"] >= args.min_words
        status = "PASSED" if ok_min else "FAILED (SUB-MINIMUM)"
        if not ok_min:
            all_pass = False

        es_pct = (rep["es_words"] / rep["total_words"] * 100) if rep["total_words"] else 0
        en_pct = (rep["en_words"] / rep["total_words"] * 100) if rep["total_words"] else 0

        print(
            f"Mazo: {rep['alma']:<15} | Cláusulas: {rep['clause_count']:<3} | Palabras: {rep['total_words']:<5} (Únicas: {rep['unique_words']:<4}) | ES: {es_pct:.1f}% / EN: {en_pct:.1f}% | [{status}]"
        )

    print("\n--------------------------------------------------------")
    print("  INTERSECCIÓN LÉXICA (Puentes potenciales)")
    print("--------------------------------------------------------")

    for i in range(len(reports)):
        for j in range(i + 1, len(reports)):
            r1, r2 = reports[i], reports[j]
            shared = r1["words_set"] & r2["words_set"]
            filtered_shared = [
                w for w in shared if w not in COMMON_EN_WORDS and w not in COMMON_ES_WORDS
            ]
            jaccard = len(shared) / len(r1["words_set"] | r2["words_set"])
            print(
                f"{r1['alma']} <-> {r2['alma']}: {len(shared)} palabras compartidas (Jaccard: {jaccard:.3f}). Términos no-stopwords compartidos: {len(filtered_shared)}"
            )

    print("========================================================\n")
    if not all_pass:
        print("ALERTA: Al menos un mazo no alcanzó el mínimo requerido.", file=sys.stderr)
        sys.exit(2)
    print("ÉXITO: Todos los mazos cumplen el requisito de volumen.")


if __name__ == "__main__":
    main()

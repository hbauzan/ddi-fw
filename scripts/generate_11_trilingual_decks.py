"""Generador y validador de los 11 mazos trilingües (Opción B: Punto Dulce).

Genera 500 cláusulas por mazo (167 ES / 167 EN / 166 DE) para los 11 oficios
canónicos (5.500 cláusulas en total), valida la invariante de aislamiento léxico
Jaccard (J < 0.05 en los 55 pares) y serializa en ddi_fw/data/trilingual/*.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from scripts.audit_corpus_words import (
    COMMON_DE_WORDS,
    COMMON_EN_WORDS,
    COMMON_ES_WORDS,
)
from scripts.trilingual_generators import DECK_GENERATORS

WORD_RE = re.compile(r"\b[^\W\d_]+(?:'[^\W\d_]+)?\b", re.UNICODE)
STOPWORDS = COMMON_ES_WORDS | COMMON_EN_WORDS | COMMON_DE_WORDS


def extract_words(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generar y certificar los 11 mazos trilingües (Opción B: 5.500 cláusulas)."
    )
    parser.add_argument(
        "--out-dir",
        default="ddi_fw/data/trilingual",
        help="Directorio destino para los archivos JSON (default: ddi_fw/data/trilingual).",
    )
    parser.add_argument(
        "--max-jaccard",
        type=float,
        default=0.05,
        help="Límite máximo permitido para el índice Jaccard léxico (default: 0.05).",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("  GENERADOR DE MAZOS TRILINGÜES DDI-FW — OPCIÓN B (PUNTO DULCE)")
    print(f"  Destino: {out_dir}")
    print(f"  Oficios: {len(DECK_GENERATORS)} dominios canónicos")
    print("  Objetivo por oficio: 500 cláusulas (167 ES / 167 EN / 166 DE)")
    print("  Objetivo global: 5.500 cláusulas")
    print("=" * 80 + "\n")

    decks_data: dict[str, dict] = {}
    deck_word_sets: dict[str, set[str]] = {}
    total_clauses_global = 0
    total_words_global = 0

    # 1. Generación y validación individual
    for alma, generator_func in DECK_GENERATORS.items():
        clauses = generator_func()

        # Validaciones de integridad
        if len(clauses) != 500:
            raise ValueError(
                f"El mazo {alma} tiene {len(clauses)} cláusulas (se esperaban exactamente 500)."
            )

        es_clauses = [c for c in clauses if c.lang == "es"]
        en_clauses = [c for c in clauses if c.lang == "en"]
        de_clauses = [c for c in clauses if c.lang == "de"]

        if len(es_clauses) != 167 or len(en_clauses) != 167 or len(de_clauses) != 166:
            raise ValueError(
                f"Distribución de idiomas incorrecta en {alma}: "
                f"ES={len(es_clauses)}, EN={len(en_clauses)}, DE={len(de_clauses)}"
            )

        # Unicidad interna de textos
        texts = [c.text for c in clauses]
        if len(set(texts)) != 500:
            raise ValueError(f"Existen cláusulas duplicadas dentro del mazo {alma}.")

        # Métricas de palabras
        word_set = set()
        deck_words = 0
        for t in texts:
            words = extract_words(t)
            word_set.update(words)
            deck_words += len(words)

        deck_word_sets[alma] = word_set
        total_clauses_global += len(clauses)
        total_words_global += deck_words

        deck_json = {
            "alma": alma,
            "n": len(clauses),
            "description": (
                f"Mazo trilingüe de {alma} (ES/EN/DE) de alta pureza terminológica "
                f"y densidad conceptual para el Ecualizador Espectral."
            ),
            "clauses": [c.to_dict() for c in clauses],
        }
        decks_data[alma] = deck_json

        # Guardar en disco
        out_file = out_dir / f"{alma}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(deck_json, f, indent=2, ensure_ascii=False)

        print(
            f"  ✔ [{alma:<12}] 500 cláusulas (167 ES / 167 EN / 166 DE) | "
            f"{deck_words:>6} palabras ({len(word_set):>5} únicas) -> {out_file.name}"
        )

    print("\n" + "-" * 80)
    print(f"  TOTAL GLOBAL: {total_clauses_global} cláusulas | {total_words_global} palabras")
    print("-" * 80 + "\n")

    # 2. Matriz Jaccard de los 55 pares (Términos de contenido no-stopwords)
    print("=" * 80)
    print(
        f"  AUDITORÍA DE AISLAMIENTO LÉXICO INTER-DOMINIO (Jaccard Contenido < {args.max_jaccard})"
    )
    print("=" * 80)

    almas = list(DECK_GENERATORS.keys())
    jaccard_violations = []
    max_observed_content_jaccard = 0.0
    max_observed_raw_jaccard = 0.0
    pair_count = 0

    for i in range(len(almas)):
        for j in range(i + 1, len(almas)):
            a1, a2 = almas[i], almas[j]
            s1_raw, s2_raw = deck_word_sets[a1], deck_word_sets[a2]
            s1_content = s1_raw - STOPWORDS
            s2_content = s2_raw - STOPWORDS

            inter_raw = s1_raw & s2_raw
            union_raw = s1_raw | s2_raw
            jac_raw = len(inter_raw) / len(union_raw) if union_raw else 0.0

            inter_content = s1_content & s2_content
            union_content = s1_content | s2_content
            jac_content = len(inter_content) / len(union_content) if union_content else 0.0

            pair_count += 1
            if jac_content > max_observed_content_jaccard:
                max_observed_content_jaccard = jac_content
            if jac_raw > max_observed_raw_jaccard:
                max_observed_raw_jaccard = jac_raw

            if jac_content >= args.max_jaccard:
                jaccard_violations.append((a1, a2, jac_content, len(inter_content)))

    print(f"  Total de pares evaluados: {pair_count} pares combinatorios")
    print(
        f"  Pico máximo Jaccard Contenido (términos de oficio): {max_observed_content_jaccard:.4f}"
    )
    print(
        f"  Pico máximo Jaccard Bruto (con stopwords gramaticales): {max_observed_raw_jaccard:.4f}"
    )

    if jaccard_violations:
        print(
            f"\n  ❌ VIOLACIÓN: {len(jaccard_violations)} pares superaron el umbral J < {args.max_jaccard}:"
        )
        for a1, a2, jac, inter_len in jaccard_violations:
            print(
                f"     - {a1} <-> {a2}: J = {jac:.4f} ({inter_len} palabras técnicas compartidas)"
            )
        sys.exit(1)

    print(
        f"  ✔ Aislamiento garantizado: Todos los {pair_count} pares cumplen estrictamente J_contenido < {args.max_jaccard}."
    )
    print("\n" + "=" * 80)
    print("  ÉXITO: Generación y validación completada para la Opción B.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

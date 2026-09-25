"""Infraestructura base para generadores de mazos trilingües DDI-FW."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClauseData:
    id: str
    text: str
    lang: str
    source: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "text": self.text,
            "lang": self.lang,
            "source": self.source,
        }


def build_clauses_for_lang(
    alma: str,
    lang: str,
    target_count: int,
    seeds: Sequence[str],
    subjects: Sequence[str],
    predicates: Sequence[str],
    contexts: Sequence[str],
    connectors: Sequence[str] | None = None,
) -> list[ClauseData]:
    """Genera una lista determinista de cláusulas técnicas sin duplicados."""
    clauses: list[ClauseData] = []
    seen_texts: set[str] = set()

    source_tag = f"corpus-trilingue-{alma}"

    # 1. Ingerir semillas curadas iniciales
    for text in seeds:
        clean_text = text.strip()
        if clean_text and clean_text not in seen_texts:
            seen_texts.add(clean_text)
            idx = len(clauses) + 1
            clauses.append(
                ClauseData(
                    id=f"{alma}-{lang}-{idx:03d}",
                    text=clean_text,
                    lang=lang,
                    source=source_tag,
                )
            )
            if len(clauses) >= target_count:
                return clauses

    # 2. Generación combinatoria estructurada con cobertura léxica total
    conn_list = connectors or [", "]
    needed = target_count - len(clauses)

    # Zancadas primas para muestreo uniforme sobre todos los elementos de los bancos
    stride_s = 7
    stride_p = 11
    stride_c = 13

    for step in range(needed * 50):
        s_idx = (step * stride_s) % len(subjects)
        p_idx = (step * stride_p + (step // len(subjects))) % len(predicates)
        c_idx = (step * stride_c + (step // len(predicates))) % len(contexts)

        subj = subjects[s_idx].strip()
        pred = predicates[p_idx].strip().rstrip(".")
        ctx = contexts[c_idx].strip().rstrip(".")
        conn = conn_list[(step) % len(conn_list)]

        var_type = (s_idx + p_idx + c_idx + step) % 3
        if var_type == 0:
            text = f"{subj} {pred}{conn}{ctx}."
        elif var_type == 1:
            if lang == "de":
                text = f"{subj} {pred}, {ctx}."
            elif lang == "es":
                text = f"{subj} {pred}, con el fin de {ctx.lower()}."
            else:
                text = f"{subj} {pred}, in order to {ctx.lower()}."
        else:
            text = f"{subj} {pred} {ctx}."

        text = " ".join(text.split())
        if not text.endswith("."):
            text += "."

        if text not in seen_texts:
            seen_texts.add(text)
            idx = len(clauses) + 1
            clauses.append(
                ClauseData(
                    id=f"{alma}-{lang}-{idx:03d}",
                    text=text,
                    lang=lang,
                    source=source_tag,
                )
            )
            if len(clauses) >= target_count:
                return clauses

    if len(clauses) < target_count:
        raise ValueError(
            f"No se alcanzaron {target_count} cláusulas para {alma}-{lang}. "
            f"Solo se generaron {len(clauses)} únicas. Aumentar bancos combinatorios."
        )

    return clauses


def load_extended_seeds(alma: str, lang: str) -> list[str]:
    """Carga cláusulas semilla de los archivos existentes en ddi_fw/data/extended/."""
    extended_path = (
        Path(__file__).resolve().parents[2] / "ddi_fw" / "data" / "extended" / f"{alma}.json"
    )
    if not extended_path.exists():
        return []

    with open(extended_path, encoding="utf-8") as f:
        data = json.load(f)

    seeds = []
    for c in data.get("clauses", []):
        if c.get("lang") == lang:
            seeds.append(c["text"])
    return seeds

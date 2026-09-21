#!/usr/bin/env python3
"""Mide T0–T4 sobre filas float32 ya guardadas. No carga un modelo si los textos coinciden."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from ddi_fw.resonancia import ALMAS, cierre, load_deck_ids, load_splits, validate_partition

ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_SPLITS = ROOT / "roadmap" / "hipotesis-resonancia" / "splits.json"
_ARCHIVE_SPLITS = (
    ROOT
    / "archive"
    / "roadmap-legacy"
    / "2026-09-21-cierre-resonancia-auditoria"
    / "hipotesis-resonancia"
    / "splits.json"
)
SPLITS = _DEFAULT_SPLITS if _DEFAULT_SPLITS.exists() else _ARCHIVE_SPLITS
DATA = ROOT / "ddi_fw" / "data" / "extended"
ROWS = ROOT / "ddi_fw" / "out" / "extended_bge" / "rows.npz"
OUT_JSON = ROOT / "archive" / "current-research" / "resonancia-cierre.json"
OUT_MD = ROOT / "archive" / "current-research" / "resonancia-cierre.md"


def _deck_texts(alma: str) -> dict[str, str]:
    payload = json.loads((DATA / f"{alma}.json").read_text(encoding="utf-8"))
    return {str(clause["id"]): str(clause["text"]) for clause in payload["clauses"]}


def _tables(handle: np.lib.npyio.NpzFile) -> dict[str, dict[str, np.ndarray]]:
    model = str(np.asarray(handle["model_id"]))
    if model != "BAAI/bge-m3":
        raise SystemExit(f"abortada: model_id {model}")
    tables: dict[str, dict[str, np.ndarray]] = {}
    for alma in ALMAS:
        matrix = np.asarray(handle[alma])
        if matrix.dtype != np.float32:
            raise SystemExit(f"abortada: {alma} dtype {matrix.dtype}")
        ids = [str(item) for item in handle[f"ids_{alma}"]]
        texts = [str(item) for item in handle[f"texts_{alma}"]]
        disk = _deck_texts(alma)
        stored = dict(zip(ids, texts, strict=True))
        if stored != disk:
            raise SystemExit(f"abortada: los textos de {alma} no coinciden con el mazo")
        tables[alma] = {
            clause_id: np.asarray(row, dtype=np.float32)
            for clause_id, row in zip(ids, matrix, strict=True)
        }
    return tables


def _failures(rows: list[dict[str, object]], *, expect_pass: bool) -> list[dict[str, object]]:
    return [row for row in rows if bool(row["pasa"]) is not expect_pass]


def _write(report: dict[str, object]) -> None:
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Cierre de la resonancia armónica",
        "",
        f"Resultado: `{report['resultado']}`.",
        "",
        "Enteros crudos en `resonancia-cierre.json`. Sin redondeo. Sin coseno.",
        "",
        f"Fuente: `{report['source_rows']}`, `model_id={report['model_id']}`, dtype `{report['vector_dtype']}`.",
        "Los vectores ya estaban guardados. Esta corrida no cargó el modelo: los textos de las cinco almas coinciden con el mazo.",
        "",
        f"T2 (diez pares): `{str(report['t2_pass']).lower()}`.",
        f"T3 (dos mitades de python): `{str(report['t3_pass']).lower()}`.",
        "",
        "| Par | Pasa | minimo_fit_a | minimo_fit_b | held-out que no cumple |",
        "| :--- | :--- | ---: | ---: | ---: |",
    ]
    pairs = report["pairs"]
    assert isinstance(pairs, dict)
    for key, pair in pairs.items():
        assert isinstance(pair, dict)
        missed = (
            len(_failures(pair["held_a_native"], expect_pass=True))
            + len(_failures(pair["held_b_on_gate_a"], expect_pass=False))
            + len(_failures(pair["held_b_native"], expect_pass=True))
            + len(_failures(pair["held_a_on_gate_b"], expect_pass=False))
        )
        lines.append(
            f"| `{key}` | `{str(pair['pass']).lower()}` | {pair['minimo_fit_a']} | {pair['minimo_fit_b']} | {missed} |"
        )
    t3 = report["t3"]
    assert isinstance(t3, dict)
    lines.extend(
        [
            "",
            f"T3 minimo_fit_L={t3['minimo_fit_a']}, minimo_fit_R={t3['minimo_fit_b']}.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    splits = load_splits(SPLITS)
    errors = validate_partition(splits, load_deck_ids(DATA))
    if errors:
        print("abortada")
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    if not ROWS.is_file():
        print("abortada: no está ddi_fw/out/extended_bge/rows.npz", file=sys.stderr)
        return 2
    with np.load(ROWS, allow_pickle=True) as handle:
        tables = _tables(handle)
    measured = cierre(tables, splits)
    report = {
        "resultado": measured["resultado"],
        "model_id": "BAAI/bge-m3",
        "vector_dtype": "float32",
        "source_rows": "ddi_fw/out/extended_bge/rows.npz",
        "t0_pass": True,
        "t2_pass": measured["t2_pass"],
        "t3_pass": measured["t3_pass"],
        "pairs": measured["pairs"],
        "t3": measured["t3"],
    }
    _write(report)
    print(report["resultado"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

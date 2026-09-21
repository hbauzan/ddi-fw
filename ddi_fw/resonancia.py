"""Cierre de la hipótesis de resonancia. No entra a decide()."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ddi_fw.hoja import CANONICAL_PAIRS, pair_id

ALMAS = ("python", "legal", "receta", "medicina", "astronomia")
Count = dict[str, int]


def load_splits(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_deck_ids(data_dir: Path) -> dict[str, set[str]]:
    decks: dict[str, set[str]] = {}
    for alma in ALMAS:
        payload = json.loads((data_dir / f"{alma}.json").read_text(encoding="utf-8"))
        decks[alma] = {str(clause["id"]) for clause in payload["clauses"]}
    return decks


def _dupes(ids: list[str]) -> bool:
    return len(ids) != len(set(ids))


def validate_partition(splits: dict[str, object], decks: dict[str, set[str]]) -> list[str]:
    """T0. Lista de fallas. Vacía si la partición se puede medir."""
    errors: list[str] = []
    cross = splits.get("cross_alma")
    null = splits.get("same_alma_python")
    if not isinstance(cross, dict) or not isinstance(null, dict):
        return ["splits sin cross_alma o same_alma_python"]

    for alma in ALMAS:
        groups = cross.get(alma)
        if not isinstance(groups, dict):
            errors.append(f"{alma} sin grupos")
            continue
        fit = [str(item) for item in groups.get("fit", [])]
        held = [str(item) for item in groups.get("held_out", [])]
        if _dupes(fit) or _dupes(held):
            errors.append(f"{alma} tiene ids repetidos")
        overlap = set(fit) & set(held)
        if overlap:
            errors.append(f"{alma} fit y held_out comparten {sorted(overlap)[:3]}")
        universe = set(fit) | set(held)
        deck = decks.get(alma, set())
        if universe != deck:
            errors.append(
                f"{alma} no cubre el mazo: sobran {sorted(universe - deck)[:3]} "
                f"faltan {sorted(deck - universe)[:3]}"
            )

    keys = ("fit_L", "held_L", "fit_R", "held_R")
    groups_py = {key: [str(item) for item in null.get(key, [])] for key in keys}
    if any(_dupes(ids) for ids in groups_py.values()):
        errors.append("same_alma_python tiene ids repetidos")
    seen: set[str] = set()
    for key, ids in groups_py.items():
        clash = seen & set(ids)
        if clash:
            errors.append(f"same_alma_python cruza {key}")
        seen |= set(ids)
    if seen != decks.get("python", set()):
        errors.append("same_alma_python no cubre python")
    return errors


def bounds(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.asarray(rows, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] < 1:
        raise ValueError("la caja necesita al menos una fila float32")
    return matrix.min(axis=0), matrix.max(axis=0)


def score_row(
    vector: np.ndarray,
    lo_native: np.ndarray,
    hi_native: np.ndarray,
    lo_foreign: np.ndarray,
    hi_foreign: np.ndarray,
) -> Count:
    values = np.asarray(vector, dtype=np.float32).reshape(-1)
    in_native = (values >= lo_native) & (values <= hi_native)
    in_foreign = (values >= lo_foreign) & (values <= hi_foreign)
    return {
        "solo_native": int(np.count_nonzero(in_native & ~in_foreign)),
        "solo_foreign": int(np.count_nonzero(~in_native & in_foreign)),
        "ambas": int(np.count_nonzero(in_native & in_foreign)),
        "ninguna": int(np.count_nonzero(~in_native & ~in_foreign)),
    }


def minimo_fit(
    rows: np.ndarray,
    lo_native: np.ndarray,
    hi_native: np.ndarray,
    lo_foreign: np.ndarray,
    hi_foreign: np.ndarray,
) -> int:
    scores = [
        score_row(row, lo_native, hi_native, lo_foreign, hi_foreign)["solo_native"]
        for row in np.asarray(rows, dtype=np.float32)
    ]
    return int(min(scores))


def pasa(score: Count, floor: int) -> bool:
    return score["solo_foreign"] == 0 and score["solo_native"] >= floor


def _stack(table: dict[str, np.ndarray], ids: list[str]) -> np.ndarray:
    missing = [clause_id for clause_id in ids if clause_id not in table]
    if missing:
        raise KeyError(f"faltan vectores: {missing[:3]}")
    return np.stack([table[clause_id] for clause_id in ids], axis=0)


def _score_ids(
    table: dict[str, np.ndarray],
    ids: list[str],
    lo_native: np.ndarray,
    hi_native: np.ndarray,
    lo_foreign: np.ndarray,
    hi_foreign: np.ndarray,
    floor: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for clause_id in ids:
        score = score_row(table[clause_id], lo_native, hi_native, lo_foreign, hi_foreign)
        rows.append({"id": clause_id, **score, "pasa": pasa(score, floor)})
    return rows


def evaluate_pair(
    table_a: dict[str, np.ndarray],
    table_b: dict[str, np.ndarray],
    fit_a: list[str],
    held_a: list[str],
    fit_b: list[str],
    held_b: list[str],
) -> dict[str, object]:
    """Cajas solo con fit. El held-out no entra al mínimo ni al máximo."""
    lo_a, hi_a = bounds(_stack(table_a, fit_a))
    lo_b, hi_b = bounds(_stack(table_b, fit_b))
    floor_a = minimo_fit(_stack(table_a, fit_a), lo_a, hi_a, lo_b, hi_b)
    floor_b = minimo_fit(_stack(table_b, fit_b), lo_b, hi_b, lo_a, hi_a)
    native_a = _score_ids(table_a, held_a, lo_a, hi_a, lo_b, hi_b, floor_a)
    foreign_on_a = _score_ids(table_b, held_b, lo_a, hi_a, lo_b, hi_b, floor_a)
    native_b = _score_ids(table_b, held_b, lo_b, hi_b, lo_a, hi_a, floor_b)
    foreign_on_b = _score_ids(table_a, held_a, lo_b, hi_b, lo_a, hi_a, floor_b)
    pair_pass = (
        all(row["pasa"] for row in native_a)
        and all(not row["pasa"] for row in foreign_on_a)
        and all(row["pasa"] for row in native_b)
        and all(not row["pasa"] for row in foreign_on_b)
    )
    return {
        "pass": pair_pass,
        "minimo_fit_a": floor_a,
        "minimo_fit_b": floor_b,
        "held_a_native": native_a,
        "held_b_on_gate_a": foreign_on_a,
        "held_b_native": native_b,
        "held_a_on_gate_b": foreign_on_b,
    }


def cierre(
    tables: dict[str, dict[str, np.ndarray]],
    splits: dict[str, object],
) -> dict[str, object]:
    cross = splits["cross_alma"]
    assert isinstance(cross, dict)
    pairs: dict[str, object] = {}
    t2 = True
    for alma_a, alma_b in CANONICAL_PAIRS:
        group_a = cross[alma_a]
        group_b = cross[alma_b]
        assert isinstance(group_a, dict) and isinstance(group_b, dict)
        report = evaluate_pair(
            tables[alma_a],
            tables[alma_b],
            [str(item) for item in group_a["fit"]],
            [str(item) for item in group_a["held_out"]],
            [str(item) for item in group_b["fit"]],
            [str(item) for item in group_b["held_out"]],
        )
        pairs[pair_id(alma_a, alma_b)] = report
        t2 = t2 and bool(report["pass"])

    null = splits["same_alma_python"]
    assert isinstance(null, dict)
    python = tables["python"]
    t3 = evaluate_pair(
        python,
        python,
        [str(item) for item in null["fit_L"]],
        [str(item) for item in null["held_L"]],
        [str(item) for item in null["fit_R"]],
        [str(item) for item in null["held_R"]],
    )
    if t2 and not bool(t3["pass"]):
        resultado = "confirmada"
    else:
        resultado = "rechazada"
    return {
        "resultado": resultado,
        "t2_pass": t2,
        "t3_pass": bool(t3["pass"]),
        "pairs": pairs,
        "t3": t3,
    }

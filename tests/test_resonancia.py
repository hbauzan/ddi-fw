"""T0 de la partición y el predicado de resonancia. Sin modelo."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ddi_fw.resonancia import (
    cierre,
    evaluate_pair,
    load_deck_ids,
    load_splits,
    validate_partition,
)

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


def test_t0_partition_covers_extended_decks() -> None:
    errors = validate_partition(load_splits(SPLITS), load_deck_ids(DATA))
    assert errors == []


def _table(rows: dict[str, list[float]]) -> dict[str, np.ndarray]:
    return {key: np.asarray(value, dtype=np.float32) for key, value in rows.items()}


def test_separated_pair_passes() -> None:
    table_a = _table({"a0": [0.0, 0.0], "a1": [0.1, 0.1], "ah": [0.05, 0.05]})
    table_b = _table({"b0": [10.0, 10.0], "b1": [10.1, 10.1], "bh": [10.05, 10.05]})
    report = evaluate_pair(table_a, table_b, ["a0", "a1"], ["ah"], ["b0", "b1"], ["bh"])
    assert report["pass"] is True
    assert report["minimo_fit_a"] == 2


def test_overlapping_halves_do_not_pass() -> None:
    table = _table(
        {
            "l0": [0.0, 0.0],
            "l1": [1.0, 1.0],
            "lh": [0.5, 0.5],
            "r0": [0.2, 0.2],
            "r1": [0.8, 0.8],
            "rh": [0.4, 0.4],
        }
    )
    report = evaluate_pair(table, table, ["l0", "l1"], ["lh"], ["r0", "r1"], ["rh"])
    assert report["pass"] is False


def test_fit_overlap_is_a_partition_error() -> None:
    splits = json.loads(SPLITS.read_text(encoding="utf-8"))
    decks = load_deck_ids(DATA)
    cross = splits["cross_alma"]
    cross["python"]["held_out"] = list(cross["python"]["fit"][:1]) + list(
        cross["python"]["held_out"]
    )
    errors = validate_partition(splits, decks)
    assert any("comparten" in error for error in errors)


def test_cierre_rejects_when_control_passes() -> None:
    """Si el control de la misma alma también separa, el resultado es rechazada."""
    separated = {
        "python": _table(
            {"p0": [0.0], "p1": [0.0], "ph": [0.0], "q0": [5.0], "q1": [5.0], "qh": [5.0]}
        ),
        "receta": _table({"r0": [9.0], "r1": [9.0], "rh": [9.0]}),
        "legal": _table({"l0": [3.0], "l1": [3.0], "lh": [3.0]}),
        "medicina": _table({"m0": [7.0], "m1": [7.0], "mh": [7.0]}),
        "astronomia": _table({"a0": [12.0], "a1": [12.0], "ah": [12.0]}),
    }
    splits = {
        "cross_alma": {
            alma: {"fit": [f"{alma[0]}0", f"{alma[0]}1"], "held_out": [f"{alma[0]}h"]}
            for alma in separated
        },
        "same_alma_python": {
            "fit_L": ["p0"],
            "held_L": ["p1"],
            "fit_R": ["q0"],
            "held_R": ["q1"],
        },
    }
    # The one-point boxes above are not the real ids. This test only checks the
    # control branch: L and R of python are far apart, so T3 passes and the
    # cierre must be rechazada even when the cross pairs also separate.
    splits["cross_alma"] = {
        "python": {"fit": ["p0", "p1"], "held_out": ["ph"]},
        "receta": {"fit": ["r0", "r1"], "held_out": ["rh"]},
        "legal": {"fit": ["l0", "l1"], "held_out": ["lh"]},
        "medicina": {"fit": ["m0", "m1"], "held_out": ["mh"]},
        "astronomia": {"fit": ["a0", "a1"], "held_out": ["ah"]},
    }
    report = cierre(separated, splits)
    assert report["t3_pass"] is True
    assert report["resultado"] == "rechazada"

"""D03 — CLI press sobre rows.npz sintético."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ddi_fw.press import _synthetic_rows, assert_no_mean_fields, main, press


def test_press_writes_json_csv_and_votes(tmp_path: Path) -> None:
    rows = _synthetic_rows(tmp_path / "rows.npz")
    out = tmp_path / "out"
    payload = press(rows, out)
    assert (out / "press.json").is_file()
    assert (out / "press_python_receta.csv").is_file()
    assert (out / "press_votes.npz").is_file()
    assert_no_mean_fields(payload)
    dumped = json.loads((out / "press.json").read_text(encoding="utf-8"))
    assert dumped["pairs"]["python_receta"]["published"] is True
    assert dumped["pairs"]["python_receta"]["disjoint_count"] >= 1
    assert dumped["pairs"]["python_legal"]["published"] is True
    assert dumped["pairs"]["legal_receta"]["published"] is True
    assert dumped["pairs"]["python_receta"]["families"]["python"]["census"]["left"] == 2
    assert dumped["pairs"]["python_receta"]["families"]["receta"]["census"]["right"] == 2
    extrema = dumped["pairs"]["python_receta"]["families"]["python"]["vote_count_extrema"]
    assert "lo" in extrema["solo_a"] and "hi" in extrema["solo_a"]
    votes = np.load(out / "press_votes.npz")
    assert votes["python"].dtype == np.uint8
    assert votes["python"].shape[1] == 3


def test_press_missing_rows_exits_nonzero(tmp_path: Path) -> None:
    code = main(["--rows", str(tmp_path / "missing.npz"), "--out", str(tmp_path)])
    assert code == 2


def test_press_unpublished_when_no_disjoint(tmp_path: Path) -> None:
    overlap = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    np.savez_compressed(
        tmp_path / "rows.npz",
        python=overlap,
        legal=overlap + 0.2,
        receta=overlap + 0.4,
        model_id=np.asarray("fake"),
        dimension=np.asarray(2),
    )
    payload = press(tmp_path / "rows.npz", tmp_path / "out")
    assert payload["pairs"]["python_receta"]["published"] is False
    assert payload["pairs"]["python_receta"]["disjoint_count"] == 0

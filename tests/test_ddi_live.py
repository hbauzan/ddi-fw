"""Calibración live. Requiere --run-live y red para bajar el modelo."""

from __future__ import annotations

from pathlib import Path

import pytest

from ddi_fw.embedder import BGEM3Embedder, calibrate, load_rows, rows_matrices
from ddi_fw.hoja import candados_canonicos


@pytest.mark.live
def test_live_bge_m3_publishes_canonical_pairs(tmp_path: Path) -> None:
    out = tmp_path / "rows.npz"
    audit = calibrate(BGEM3Embedder.instance(), out_path=out, rewrite_fixtures=False)
    assert all(audit["published"].values())
    assert all(count > 0 for count in audit["disjoint_count"].values())
    locks = candados_canonicos(rows_matrices(load_rows(out)))
    assert set(locks) == {"python_receta", "python_legal", "legal_receta"}
    assert all(lock.published for lock in locks.values())

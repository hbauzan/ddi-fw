"""Q01 — persistencia sin poda para la ola Qwen2. Solo FakeEmbedder."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from ddi_fw.almas import Clause, Mazo
from ddi_fw.embedder import FakeEmbedder, calibrate, load_rows, rows_matrices
from ddi_fw.hoja import candados_canonicos
from ddi_fw.measure import measure_and_save

_MIXED = {
    "python": [("p0", [0.0, 0.0, 0.0, 0.0]), ("p1", [1.0, 1.0, 1.0, 1.0])],
    "legal": [("l0", [0.0, 100.0, 100.0, 100.0]), ("l1", [1.0, 101.0, 101.0, 101.0])],
    "receta": [("r0", [2.0, 50.0, 50.0, 50.0]), ("r1", [3.0, 51.0, 51.0, 51.0])],
}
_OVERLAP = {
    "python": [("p0", [0.0, 0.0]), ("p1", [1.0, 1.0])],
    "legal": [("l0", [0.0, 0.0]), ("l1", [1.0, 1.0])],
    "receta": [("r0", [0.0, 0.0]), ("r1", [1.0, 1.0])],
}


def _mazos(spec: dict[str, list[tuple[str, list[float]]]]) -> dict[str, Mazo]:
    return {
        alma: Mazo(
            alma=alma,
            clauses=tuple(Clause(id=cid, text=cid, source="test") for cid, _ in rows),
        )
        for alma, rows in spec.items()
    }


def _patch(monkeypatch: pytest.MonkeyPatch, spec: dict[str, list[tuple[str, list[float]]]]) -> None:
    """Fija load_almas (en measure y embedder) y el batch a vectores ingenierizados."""
    import ddi_fw.embedder as embedder_module
    import ddi_fw.measure as measure_module

    mazos = _mazos(spec)
    tables = {
        alma: np.asarray([vector for _, vector in rows], dtype=np.float32)
        for alma, rows in spec.items()
    }
    alma_by_clause = {cid: alma for alma, rows in spec.items() for cid, _ in rows}
    index_by_clause = {cid: index for rows in spec.values() for index, (cid, _) in enumerate(rows)}
    loader = lambda data_dir=None: mazos  # noqa: E731
    monkeypatch.setattr(measure_module, "load_almas", loader)
    monkeypatch.setattr(embedder_module, "load_almas", loader)

    def embed_batch(self: FakeEmbedder, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        return np.asarray(
            [tables[alma_by_clause[text]][index_by_clause[text]] for text in texts],
            dtype=np.float32,
        )

    monkeypatch.setattr(FakeEmbedder, "embed_batch", embed_batch)


def test_measure_and_save_no_prune_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch(monkeypatch, _MIXED)
    out_dir = tmp_path / "qwen2"

    audit = measure_and_save(FakeEmbedder(dimension=4, model_id="fake-q01"), out_dir=out_dir)

    assert audit["model_id"] == "fake-q01"
    assert audit["dimension"] == 4
    assert audit["dropped"] == []
    assert audit["n"] == {"python": 2, "legal": 2, "receta": 2}
    assert audit["published"]["python_receta"] is True
    assert audit["disjoint_axes"]["python_receta"] == [0, 1, 2, 3]
    assert audit["disjoint_count"]["python_receta"] == 4
    assert all(audit["published"].values())
    assert (out_dir / "rows.npz").is_file()
    assert (out_dir / "measure_audit.json").is_file()

    bundle = load_rows(out_dir / "rows.npz")
    matrices = rows_matrices(bundle)
    assert matrices["python"].shape == (2, 4)
    locks = candados_canonicos(matrices)
    assert audit["disjoint_count"] == {key: lock.disjoint_count for key, lock in locks.items()}
    for key, lock in locks.items():
        assert audit["disjoint_axes"][key] == lock.ejes_disjuntos
    payload = json.loads((out_dir / "measure_audit.json").read_text(encoding="utf-8"))
    assert payload["dropped"] == []


def test_measure_and_save_no_prune_unpublished(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Intervalos solapados: published false, sin excepción, npz con n completo."""
    _patch(monkeypatch, _OVERLAP)
    out_dir = tmp_path / "qwen2"

    audit = measure_and_save(FakeEmbedder(dimension=2, model_id="fake-overlap"), out_dir=out_dir)

    assert audit["published"] == {
        "python_receta": False,
        "python_legal": False,
        "legal_receta": False,
    }
    assert audit["disjoint_count"] == {
        "python_receta": 0,
        "python_legal": 0,
        "legal_receta": 0,
    }
    assert audit["dropped"] == []
    assert audit["n"] == {"python": 2, "legal": 2, "receta": 2}
    assert rows_matrices(load_rows(out_dir / "rows.npz"))["python"].shape == (2, 2)


def test_calibrate_prunes_and_raises_but_measure_does_not(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Contraste explícito: calibrate() poda y explota; measure_and_save nunca."""
    _patch(monkeypatch, _OVERLAP)

    with pytest.raises(RuntimeError):
        calibrate(
            FakeEmbedder(dimension=2, model_id="fake-overlap"),
            out_path=tmp_path / "cal" / "rows.npz",
            min_n=1,
        )

    audit = measure_and_save(
        FakeEmbedder(dimension=2, model_id="fake-overlap"), out_dir=tmp_path / "qwen2"
    )
    assert audit["published"]["python_receta"] is False


def test_cli_no_prune_writes_into_out_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import ddi_fw.embedder as embedder_module

    _patch(monkeypatch, _MIXED)
    monkeypatch.setattr(
        embedder_module, "get_embedder", lambda name: FakeEmbedder(dimension=4, model_id="fake-cli")
    )
    out_dir = tmp_path / "qwen2"

    code = embedder_module.main(["--embedder", "qwen2", "--no-prune", "--out", str(out_dir)])

    assert code == 0
    assert (out_dir / "rows.npz").is_file()
    assert (out_dir / "measure_audit.json").is_file()
    assert not (out_dir / "calibrate_audit.json").exists()
    audit = json.loads((out_dir / "measure_audit.json").read_text(encoding="utf-8"))
    assert audit["dropped"] == []


def test_cli_rejects_rewrite_fixtures_with_no_prune(tmp_path: Path) -> None:
    import ddi_fw.embedder as embedder_module

    with pytest.raises(SystemExit):
        embedder_module.main(
            ["--embedder", "fake", "--no-prune", "--rewrite-fixtures", "--out", str(tmp_path)]
        )

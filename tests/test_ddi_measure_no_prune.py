"""Q01 — measure_and_save no poda y no pisa el blob BGE."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ddi_fw.embedder import DEFAULT_OUT, FakeEmbedder, main, measure_and_save

DIM = 8


def _write_mazos(data_dir: Path, texts: dict[str, list[str]]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for alma, alma_texts in texts.items():
        payload = {
            "alma": alma,
            "n": len(alma_texts),
            "clauses": [
                {"id": f"{alma}-{index:03d}", "text": text, "source": "test"}
                for index, text in enumerate(alma_texts)
            ],
        }
        (data_dir / f"{alma}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def _unit(axis: int, lo: float, hi: float) -> tuple[np.ndarray, np.ndarray]:
    low = np.zeros(DIM, dtype=np.float32)
    high = np.zeros(DIM, dtype=np.float32)
    low[axis] = lo
    high[axis] = hi
    return low, high


def test_measure_and_save_writes_isolated_npz_when_disjoint(tmp_path: Path) -> None:
    py_lo, py_hi = _unit(0, 0.0, 1.0)
    rec_lo, rec_hi = _unit(0, 10.0, 11.0)
    legal_lo, legal_hi = _unit(1, 10.0, 11.0)
    med_lo, med_hi = _unit(2, 10.0, 11.0)
    ast_lo, ast_hi = _unit(3, 10.0, 11.0)
    texts = {
        "python": ["py-lo", "py-hi"],
        "legal": ["lg-lo", "lg-hi"],
        "receta": ["rc-lo", "rc-hi"],
        "medicina": ["med-lo", "med-hi"],
        "astronomia": ["ast-lo", "ast-hi"],
    }
    _write_mazos(tmp_path / "data", texts)
    embedder = FakeEmbedder(
        dimension=DIM,
        table={
            "py-lo": py_lo,
            "py-hi": py_hi,
            "lg-lo": legal_lo,
            "lg-hi": legal_hi,
            "rc-lo": rec_lo,
            "rc-hi": rec_hi,
            "med-lo": med_lo,
            "med-hi": med_hi,
            "ast-lo": ast_lo,
            "ast-hi": ast_hi,
        },
    )
    out_dir = tmp_path / "qwen2"
    before_default = DEFAULT_OUT.read_bytes() if DEFAULT_OUT.is_file() else None

    audit = measure_and_save(embedder, data_dir=tmp_path / "data", out_dir=out_dir)

    assert audit["dropped"] == []
    assert audit["dimension"] == DIM
    assert audit["n"] == {"python": 2, "legal": 2, "receta": 2, "medicina": 2, "astronomia": 2}
    assert audit["published"]["python_receta"] is True
    assert audit["disjoint_count"]["python_receta"] >= 1
    assert 0 in audit["disjoint_axes"]["python_receta"]
    assert (out_dir / "rows.npz").is_file()
    assert (out_dir / "measure_audit.json").is_file()
    assert not (Path("ddi_fw/out/rows.npz").resolve() == (out_dir / "rows.npz").resolve())
    if before_default is None:
        assert not DEFAULT_OUT.exists()
    else:
        assert DEFAULT_OUT.read_bytes() == before_default
    dumped = json.loads((out_dir / "measure_audit.json").read_text(encoding="utf-8"))
    assert dumped["dropped"] == []
    bundle = np.load(out_dir / "rows.npz", allow_pickle=True)
    assert int(bundle["dimension"]) == DIM
    assert bundle["python"].shape == (2, DIM)


def test_measure_and_save_unpublished_no_raise_no_drop(tmp_path: Path) -> None:
    overlap = np.zeros(DIM, dtype=np.float32)
    overlap_hi = np.ones(DIM, dtype=np.float32)
    texts = {
        "python": ["py-a", "py-b"],
        "legal": ["lg-a", "lg-b"],
        "receta": ["rc-a", "rc-b"],
        "medicina": ["med-a", "med-b"],
        "astronomia": ["ast-a", "ast-b"],
    }
    data_dir = tmp_path / "data"
    _write_mazos(data_dir, texts)
    original_json = {
        alma: (data_dir / f"{alma}.json").read_text(encoding="utf-8") for alma in texts
    }
    embedder = FakeEmbedder(
        dimension=DIM,
        table={
            "py-a": overlap,
            "py-b": overlap_hi,
            "lg-a": overlap + np.float32(0.2),
            "lg-b": overlap_hi + np.float32(0.2),
            "rc-a": overlap + np.float32(0.4),
            "rc-b": overlap_hi + np.float32(0.4),
            "med-a": overlap + np.float32(0.6),
            "med-b": overlap_hi + np.float32(0.6),
            "ast-a": overlap + np.float32(0.8),
            "ast-b": overlap_hi + np.float32(0.8),
        },
    )
    out_dir = tmp_path / "qwen2"

    audit = measure_and_save(embedder, data_dir=data_dir, out_dir=out_dir)

    assert audit["dropped"] == []
    assert all(value is False for value in audit["published"].values())
    assert all(count == 0 for count in audit["disjoint_count"].values())
    assert all(axes == [] for axes in audit["disjoint_axes"].values())
    assert audit["n"] == {"python": 2, "legal": 2, "receta": 2, "medicina": 2, "astronomia": 2}
    assert (out_dir / "rows.npz").is_file()
    for alma, payload in original_json.items():
        assert (data_dir / f"{alma}.json").read_text(encoding="utf-8") == payload


def test_cli_no_prune_honours_out_directory(tmp_path: Path) -> None:
    texts = {
        "python": ["cli-py-a", "cli-py-b"],
        "legal": ["cli-lg-a", "cli-lg-b"],
        "receta": ["cli-rc-a", "cli-rc-b"],
        "medicina": ["cli-med-a", "cli-med-b"],
        "astronomia": ["cli-ast-a", "cli-ast-b"],
    }
    _write_mazos(tmp_path / "data", texts)
    out_dir = tmp_path / "qwen2"
    before_default = DEFAULT_OUT.read_bytes() if DEFAULT_OUT.is_file() else None

    code = main(
        [
            "--embedder",
            "fake",
            "--no-prune",
            "--data-dir",
            str(tmp_path / "data"),
            "--out",
            str(out_dir),
        ]
    )

    assert code == 0
    assert (out_dir / "rows.npz").is_file()
    assert (out_dir / "measure_audit.json").is_file()
    if before_default is None:
        assert not DEFAULT_OUT.exists()
    else:
        assert DEFAULT_OUT.read_bytes() == before_default


def test_cli_no_prune_refuses_bge_rows_blob(tmp_path: Path) -> None:
    texts = {
        "python": ["a", "b"],
        "legal": ["c", "d"],
        "receta": ["e", "f"],
    }
    _write_mazos(tmp_path / "data", texts)

    code = main(
        [
            "--embedder",
            "fake",
            "--no-prune",
            "--data-dir",
            str(tmp_path / "data"),
            "--out",
            str(DEFAULT_OUT),
        ]
    )

    assert code == 2

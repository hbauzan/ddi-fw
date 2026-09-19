"""D07 — BaseEmbedder polimórfico y benchmark con fakes."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ddi_fw.almas import load_almas
from ddi_fw.benchmark import measure_embedder, run_benchmark
from ddi_fw.embedder import FakeEmbedder, l2_normalize, matryoshka_cut
from ddi_fw.hoja import calcular_hoja
from ddi_fw.press import main


def test_hoja_accepts_mrl_dimensions() -> None:
    for dim in (128, 256, 512, 768, 1024):
        embedder = FakeEmbedder(dimension=dim, model_id=f"fake-{dim}")
        left = embedder.embed_batch(["a1", "a2"])
        right = embedder.embed_batch(["b1", "b2"]) + 50
        hoja = calcular_hoja(left, right)
        assert hoja.dimension == dim


def test_matryoshka_cut_renormalizes() -> None:
    rows = np.ones((2, 8), dtype=np.float32)
    cut = matryoshka_cut(rows, 4)
    assert cut.shape == (2, 4)
    norms = np.linalg.norm(cut, axis=1)
    np.testing.assert_allclose(norms, np.ones(2), atol=1e-6)
    unit = l2_normalize(np.array([3.0, 4.0], dtype=np.float32))
    np.testing.assert_allclose(np.linalg.norm(unit), 1.0, atol=1e-6)


def test_benchmark_all_with_fake_models(tmp_path: Path) -> None:
    out = tmp_path / "benchmark_models.json"
    code = main(["--benchmark-all", "--models", "fake:128,fake:256", "--out", str(tmp_path)])
    assert code == 0
    report = run_benchmark(["fake:128", "fake:256"], out_path=out, live=False)
    assert len(report["models"]) == 2
    assert {item["dimension"] for item in report["models"]} == {128, 256}
    for model in report["models"]:
        assert "pairs" in model
        assert model["pairs"][0]["disjoint_axes_count"] >= 0
        assert "mean_gap" in model["pairs"][0]
        assert "latency_us_per_clause" in model
    assert out.is_file()
    mazos = load_almas()
    measured = measure_embedder(FakeEmbedder(dimension=8), mazos)
    assert measured["dimension"] == 8

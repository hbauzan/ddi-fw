"""Unit tests for SensitivityAnalysisEngine."""

from pathlib import Path
import numpy as np
import pytest

from ddi_fw.embedder import FakeEmbedder
from rompepepe.engines.sensitivity import SensitivityAnalysisEngine


@pytest.fixture
def mock_rows_npz(tmp_path: Path) -> Path:
    # 3 domains in 1024D
    np.random.seed(42)
    py_rows = np.random.uniform(0.1, 0.5, size=(10, 1024)).astype(np.float32)
    rec_rows = np.random.uniform(0.4, 0.8, size=(10, 1024)).astype(np.float32)
    leg_rows = np.random.uniform(-0.5, 0.0, size=(10, 1024)).astype(np.float32)

    out_file = tmp_path / "rows.npz"
    np.savez_compressed(
        out_file,
        python=py_rows,
        receta=rec_rows,
        legal=leg_rows,
    )
    return out_file


def test_sensitivity_engine_sweep(mock_rows_npz: Path):
    embedder = FakeEmbedder(dimension=1024)
    engine = SensitivityAnalysisEngine(
        rows_path=mock_rows_npz,
        embedder=embedder,
        allowed_alma="python",
        forbidden_almas=["receta", "legal"],
    )

    dataset = [
        {"prompt": "def legitimate_python_fn(): return True", "category": "legitimate_python", "expected": "PASS"},
        {"prompt": "receta de cocina para pastel", "category": "semantic_piggybacking", "expected": "BREACH"},
        {"prompt": "contrato legal de arrendamiento", "category": "boundary_mutations", "expected": "BREACH"},
    ]

    result = engine.run_sweep(
        dataset,
        quorum_range=[100, 50, 10],
        cosine_delta_range=[0.0, 0.1],
        cosine_forbid_range=[0.5, 0.8],
    )

    assert "K=100|prune=True" in result.spectral_sweep
    assert "K=10|prune=True" in result.spectral_sweep
    assert 0.0 in result.cosine_delta_sweep
    assert 0.5 in result.cosine_forbid_sweep
    assert len(result.prompts_telemetry) == 3
    assert result.config_summary["total_prompts"] == 3

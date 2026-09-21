from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ddi_fw.ecualizador.intrinseco import (
    compute_intrinsic_profile,
    fmt_float,
    run_protocolo_01,
)


def test_fmt_float_no_rounding() -> None:
    val = 0.12345678901234567
    s = fmt_float(val)
    assert float(s) == val
    assert len(s.split(".")[1]) > 10


def test_compute_intrinsic_profile_synthetic() -> None:
    # Matriz sintética: 10 cláusulas, 3 dimensiones
    # d0: valores positivos grandes
    # d1: valores centrados en cero
    # d2: valores negativos
    mat = np.array(
        [
            [10.0, -1.0, -5.0],
            [12.0, 1.0, -4.0],
            [11.0, 0.0, -6.0],
            [9.0, 2.0, -5.0],
        ],
        dtype=np.float32,
    )
    records = compute_intrinsic_profile(mat)
    assert len(records) == 3

    # Ranking 1 debe ser d0 (mayor energía)
    assert records[0]["dimension"] == 0
    assert records[0]["ranking"] == 1
    assert records[0]["mu"] == 10.5
    assert records[0]["mediana"] == 10.5
    assert records[0]["lo"] == 9.0
    assert records[0]["hi"] == 12.0
    assert records[0]["rango"] == 3.0
    assert records[0]["pico"] == 12.0
    assert records[0]["energia"] == 10.5
    assert records[0]["coherencia_signo"] == 1.0  # Todos positivos

    # Ranking 2 debe ser d2 (energía 5.0)
    assert records[1]["dimension"] == 2
    assert records[1]["ranking"] == 2
    assert records[1]["energia"] == 5.0
    assert records[1]["coherencia_signo"] == 1.0  # Todos negativos

    # Ranking 3 debe ser d1 (energía 1.0)
    assert records[2]["dimension"] == 1
    assert records[2]["ranking"] == 3


def test_run_protocolo_01_synthetic(tmp_path: Path) -> None:
    # Crear un rows.npz simulado con las 5 almas
    almas = ("python", "receta", "legal", "medicina", "astronomia")
    npz_data: dict[str, object] = {
        "model_id": "BAAI/bge-m3",
        "dimension": 16,
    }
    for a in almas:
        npz_data[a] = np.random.randn(20, 16).astype(np.float32)

    dummy_rows = tmp_path / "dummy_rows.npz"
    np.savez(dummy_rows, **npz_data)

    out_dir = tmp_path / "out_p1"
    summary = run_protocolo_01(rows_path=dummy_rows, out_dir=out_dir)

    assert summary["model_id"] == "BAAI/bge-m3"
    assert "hardware" in summary
    assert len(summary["almas"]) == 5

    for a in almas:
        csv_file = out_dir / f"{a}_perfil_intrinseco_1024d.csv"
        json_file = out_dir / f"{a}_perfil_intrinseco_1024d.json"
        assert csv_file.exists()
        assert json_file.exists()

        data = json.loads(json_file.read_text(encoding="utf-8"))
        assert data["alma"] == a
        assert "hardware" in data
        assert len(data["dimensiones"]) == 16


def test_classify_dimension() -> None:
    from ddi_fw.ecualizador.paja import classify_dimension

    # Ambos: alta energía y plano
    assert classify_dimension(min_energy=0.10, max_delta_mu=0.005) == "PAJA_AMBOS"
    # Saturada: alta energía pero diferenciada
    assert classify_dimension(min_energy=0.10, max_delta_mu=0.05) == "PAJA_SATURADA"
    # Plana: baja energía pero indiferenciada
    assert classify_dimension(min_energy=0.02, max_delta_mu=0.005) == "PAJA_PLANA"
    # Trigo: energía normal y contrastada
    assert classify_dimension(min_energy=0.02, max_delta_mu=0.05) == "TRIGO_CANDIDATO"


def test_run_protocolo_02_synthetic(tmp_path: Path) -> None:
    from ddi_fw.ecualizador.paja import run_protocolo_02

    # Generar primero los perfiles sintéticos con P1
    almas = ("python", "receta", "legal", "medicina", "astronomia")
    npz_data: dict[str, object] = {
        "model_id": "BAAI/bge-m3",
        "dimension": 8,
    }
    for a in almas:
        npz_data[a] = np.random.randn(20, 8).astype(np.float32)

    dummy_rows = tmp_path / "dummy_rows.npz"
    np.savez(dummy_rows, **npz_data)

    p1_dir = tmp_path / "out_p1"
    run_protocolo_01(rows_path=dummy_rows, out_dir=p1_dir)

    p2_dir = tmp_path / "out_p2"
    res = run_protocolo_02(
        intrinseco_dir=p1_dir,
        out_dir=p2_dir,
        theta_saturacion=0.05,
        epsilon_indiferenciacion=0.010,
    )

    assert Path(res["catalogo_csv"]).exists()
    assert Path(res["catalogo_json"]).exists()
    assert sum(res["conteos"].values()) == 8
    for a in almas:
        assert Path(res["trigos_depurados"][a]).exists()


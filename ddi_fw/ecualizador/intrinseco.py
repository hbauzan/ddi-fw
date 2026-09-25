"""Protocolo 01 — Extracción Intrínseca por Corpus.

Caracteriza cada uno de los 5 corpus en estricto aislamiento dimensional,
promoviendo a float64 y exportando CSV completo sin redondeo (f'{val:.17g}')
y JSON estructurado con ficha técnica de hardware.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from ddi_fw.ecualizador import ALMAS_ECUALIZADOR
from ddi_fw.hardware import get_hardware_profile

DEFAULT_ROWS_PATH = Path(__file__).resolve().parents[1] / "out" / "extended_bge" / "rows.npz"
DEFAULT_OUT_DIR = Path(__file__).resolve().parents[1] / "out" / "ecualizador" / "intrinseco"


def fmt_float(val: float | np.floating) -> str:
    """Serialización exacta sin redondeo IEEE 754."""
    return f"{float(val):.17g}"


def compute_intrinsic_profile(
    matrix: np.ndarray,
) -> list[dict[str, Any]]:
    """Calcula las métricas de las dimensiones para un corpus único en float64.

    Args:
        matrix: Matriz (N, D) de vectores del corpus.

    Returns:
        Lista de diccionarios con las métricas de cada dimensión,
        ordenada de mayor a menor energía media E_d (ranking 1 a D).
    """
    n_clauses, d_dim = matrix.shape
    mat64 = np.asarray(matrix, dtype=np.float64)

    # 1. Centros de gravedad
    mus = np.mean(mat64, axis=0)
    medians = np.median(mat64, axis=0)

    # 2. Dispersión y rango
    los = np.min(mat64, axis=0)
    his = np.max(mat64, axis=0)
    ranges = his - los
    sigmas = np.std(mat64, axis=0, ddof=0)

    # 3. Nivel de energía / excitación
    abs_mat = np.abs(mat64)
    peaks = np.max(abs_mat, axis=0)
    energies = np.mean(abs_mat, axis=0)

    # 4. Índice de coherencia de signo
    # Porcentaje de cláusulas que mantienen el mismo signo que el centro de gravedad
    coherences = np.zeros(d_dim, dtype=np.float64)
    for d in range(d_dim):
        mu_d = mus[d]
        col = mat64[:, d]
        if mu_d > 0:
            coherences[d] = np.sum(col > 0) / n_clauses
        elif mu_d < 0:
            coherences[d] = np.sum(col < 0) / n_clauses
        else:
            coherences[d] = np.sum(col == 0) / n_clauses

    # Recopilar métricas por dimensión
    dim_records = []
    for d in range(d_dim):
        dim_records.append(
            {
                "dimension": d,
                "mu": float(mus[d]),
                "mediana": float(medians[d]),
                "lo": float(los[d]),
                "hi": float(his[d]),
                "rango": float(ranges[d]),
                "sigma": float(sigmas[d]),
                "pico": float(peaks[d]),
                "energia": float(energies[d]),
                "coherencia_signo": float(coherences[d]),
            }
        )

    # Ordenar de mayor a menor energía media E_d
    dim_records.sort(key=lambda r: r["energia"], reverse=True)

    # Asignar ranking (1 a d_dim)
    for rank, rec in enumerate(dim_records, start=1):
        rec["ranking"] = rank

    return dim_records


def run_protocolo_01(
    rows_path: Path = DEFAULT_ROWS_PATH,
    out_dir: Path = DEFAULT_OUT_DIR,
    almas: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    """Ejecuta el Protocolo 01 sobre los corpus canónicos y guarda resultados."""
    if not rows_path.exists():
        raise FileNotFoundError(f"No se encontró archivo de datos: {rows_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    data = np.load(rows_path)
    model_id = str(data["model_id"])

    hardware_info = get_hardware_profile()
    execution_summary: dict[str, Any] = {
        "protocolo": "01-protocolo-extraccion-intrinseca",
        "model_id": model_id,
        "hardware": hardware_info,
        "almas": {},
    }

    almas_to_process = tuple(almas) if almas is not None else ALMAS_ECUALIZADOR

    for alma in almas_to_process:
        if alma not in data:
            raise KeyError(f"Corpus '{alma}' no encontrado en {rows_path}")

        mat = data[alma]
        n_clauses, d_dim = mat.shape
        records = compute_intrinsic_profile(mat)

        # 1. Exportar CSV con precisión nativa sin redondeo
        csv_path = out_dir / f"{alma}_perfil_intrinseco_1024d.csv"
        headers = [
            "dimension",
            "ranking",
            "mu",
            "mediana",
            "lo",
            "hi",
            "rango",
            "sigma",
            "pico",
            "energia",
            "coherencia_signo",
        ]
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in records:
                writer.writerow(
                    [
                        r["dimension"],
                        r["ranking"],
                        fmt_float(r["mu"]),
                        fmt_float(r["mediana"]),
                        fmt_float(r["lo"]),
                        fmt_float(r["hi"]),
                        fmt_float(r["rango"]),
                        fmt_float(r["sigma"]),
                        fmt_float(r["pico"]),
                        fmt_float(r["energia"]),
                        fmt_float(r["coherencia_signo"]),
                    ]
                )

        # 2. Exportar JSON estructurado
        json_path = out_dir / f"{alma}_perfil_intrinseco_1024d.json"
        alma_meta = {
            "alma": alma,
            "num_clausulas": n_clauses,
            "num_dimensiones": d_dim,
            "model_id": model_id,
            "hardware": hardware_info,
            "top_10_dimensiones_activas": [
                {
                    "ranking": r["ranking"],
                    "dimension": r["dimension"],
                    "energia": r["energia"],
                    "mu": r["mu"],
                    "sigma": r["sigma"],
                    "coherencia_signo": r["coherencia_signo"],
                }
                for r in records[:10]
            ],
            "dimensiones": records,
        }
        json_path.write_text(
            json.dumps(alma_meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        execution_summary["almas"][alma] = {
            "num_clausulas": n_clauses,
            "csv_path": str(csv_path),
            "json_path": str(json_path),
            "top_1_dim": records[0]["dimension"],
            "top_1_energia": records[0]["energia"],
        }

    return execution_summary

#!/usr/bin/env python3
"""Exporta el Top 500 de dimensiones más excitadas para cada corpus extendido (1024d).

Para cada alma (receta, python, legal):
- Lee el archivo CSV extendido (110 filas × 1024 dimensiones).
- Calcula para cada dimensión el valor máximo, el valor mínimo y la excitación (pico y media).
- Selecciona el Top 500 de dimensiones con mayor nivel de excitación.
- Preserva la máxima precisión decimal disponible (valores del CSV y representación float32 de rows.npz).
- Guarda el resultado en un archivo CSV específico por corpus en ddi_fw/out/extended/.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
EXTENDED_DIR = BASE_DIR / "ddi_fw" / "out" / "extended"
NPZ_PATH = EXTENDED_DIR / "rows.npz"

CORPORA = ("receta", "python", "legal", "medicina", "astronomia")


def process_corpus(alma: str, npz_data: dict[str, np.ndarray]) -> tuple[Path, dict[str, Any]]:
    csv_in = EXTENDED_DIR / f"{alma}_extendido_1024d.csv"
    csv_out = EXTENDED_DIR / f"{alma}_top500_dimensiones_excitadas.csv"

    if not csv_in.exists():
        raise FileNotFoundError(f"Archivo fuente no encontrado: {csv_in}")

    npz_mat = npz_data[alma]  # matriz (110, 1024) float32

    with open(csv_in, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        dim_indices = [i for i, h in enumerate(header) if h.startswith("dim_")]
        dim_names = [header[i] for i in dim_indices]
        rows = list(reader)

    num_rows = len(rows)
    num_dims = len(dim_names)

    # Conversión exacta con Decimal para evitar pérdida de precisión flotante en cálculos intermedios
    data_decimal = [[Decimal(r[i]) for i in dim_indices] for r in rows]

    dims_stats: list[dict[str, Any]] = []
    for d in range(num_dims):
        col_csv = [data_decimal[r][d] for r in range(num_rows)]
        v_min_csv = min(col_csv)
        v_max_csv = max(col_csv)
        peak_abs_csv = max(abs(v_min_csv), abs(v_max_csv))
        mean_abs_csv = sum(abs(v) for v in col_csv) / Decimal(num_rows)
        rango_csv = v_max_csv - v_min_csv

        # Extremos con representación float32 nativa sin redondeo de f'{val:.6f}'
        col_raw = npz_mat[:, d]
        v_min_raw = float(np.min(col_raw))
        v_max_raw = float(np.max(col_raw))
        peak_abs_raw = float(np.max(np.abs(col_raw)))
        mean_abs_raw = float(np.mean(np.abs(col_raw)))

        dims_stats.append(
            {
                "dim": dim_names[d],
                "axis": d,
                "val_min_csv": v_min_csv,
                "val_max_csv": v_max_csv,
                "peak_abs_csv": peak_abs_csv,
                "mean_abs_csv": mean_abs_csv,
                "rango_csv": rango_csv,
                "val_min_raw": v_min_raw,
                "val_max_raw": v_max_raw,
                "peak_abs_raw": peak_abs_raw,
                "mean_abs_raw": mean_abs_raw,
            }
        )

    # Ranking por excitación media absoluta entre todas las dimensiones
    dims_by_mean = sorted(dims_stats, key=lambda x: x["mean_abs_csv"], reverse=True)
    mean_rank_map = {item["axis"]: rank for rank, item in enumerate(dims_by_mean, 1)}

    # Ranking principal: Top 500 por excitación pico absoluta (máxima activación de la dimensión)
    dims_by_peak = sorted(dims_stats, key=lambda x: x["peak_abs_csv"], reverse=True)
    top500 = dims_by_peak[:500]

    for rank, item in enumerate(top500, 1):
        item["ranking"] = rank
        item["ranking_media_abs"] = mean_rank_map[item["axis"]]

    # Escribir CSV de salida
    fieldnames = [
        "ranking",
        "dimension",
        "eje_indice",
        "valor_maximo",
        "valor_minimo",
        "excitacion_pico_abs",
        "excitacion_media_abs",
        "rango_dinamico",
        "valor_maximo_raw_fp32",
        "valor_minimo_raw_fp32",
        "ranking_media_abs",
    ]

    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        for item in top500:
            writer.writerow(
                [
                    item["ranking"],
                    item["dim"],
                    item["axis"],
                    str(item["val_max_csv"]),
                    str(item["val_min_csv"]),
                    str(item["peak_abs_csv"]),
                    str(item["mean_abs_csv"]),
                    str(item["rango_csv"]),
                    f"{item['val_max_raw']:.17g}",
                    f"{item['val_min_raw']:.17g}",
                    item["ranking_media_abs"],
                ]
            )

    # Estadísticas globales del Top 500
    global_max_csv = max(x["val_max_csv"] for x in top500)
    global_min_csv = min(x["val_min_csv"] for x in top500)
    global_max_raw = max(x["val_max_raw"] for x in top500)
    global_min_raw = min(x["val_min_raw"] for x in top500)

    summary = {
        "alma": alma,
        "csv_path": csv_out,
        "total_top500": len(top500),
        "global_max_csv": global_max_csv,
        "global_min_csv": global_min_csv,
        "global_max_raw": global_max_raw,
        "global_min_raw": global_min_raw,
        "top5": top500[:5],
    }
    return csv_out, summary


def main() -> None:
    if not NPZ_PATH.exists():
        raise FileNotFoundError(f"No se encontró {NPZ_PATH}")

    npz_data = np.load(NPZ_PATH, allow_pickle=True)

    print("=== Generando archivos Top 500 dimensiones más excitadas ===")
    for alma in CORPORA:
        out_file, summary = process_corpus(alma, npz_data)
        print(f"\nCorpus: {alma.upper()}")
        print(f"  Archivo generado: {out_file.relative_to(BASE_DIR)}")
        print(f"  Total dimensiones: {summary['total_top500']}")
        print(f"  Valor Máximo global (CSV): {summary['global_max_csv']}")
        print(f"  Valor Mínimo global (CSV): {summary['global_min_csv']}")
        print(f"  Valor Máximo global (FP32 raw): {summary['global_max_raw']:.17g}")
        print(f"  Valor Mínimo global (FP32 raw): {summary['global_min_raw']:.17g}")
        print("  Top 3 dimensiones:")
        for item in summary["top5"][:3]:
            print(
                f"    #{item['ranking']}: {item['dim']} (eje {item['axis']}) | "
                f"Max: {item['val_max_csv']} | Min: {item['val_min_csv']} | "
                f"Pico Abs: {item['peak_abs_csv']} | Media Abs: {item['mean_abs_csv']}"
            )


if __name__ == "__main__":
    main()

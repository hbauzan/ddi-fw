#!/usr/bin/env python3
"""Re-exporta los archivos CSV de corpus extendido de 1024d con precisión float32 completa nativa.

Reemplaza el viejo formateador f'{val:.6f}' (que redondeaba y truncaba decimales)
por la representación de máxima precisión f'{float(val):.17g}'.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
EXTENDED_DIR = BASE_DIR / "ddi_fw" / "out" / "extended"
NPZ_PATH = EXTENDED_DIR / "rows.npz"

CORPORA = ("receta", "python", "legal", "medicina", "astronomia")


def main() -> None:
    if not NPZ_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo {NPZ_PATH}")

    data_ext = np.load(NPZ_PATH, allow_pickle=True)

    print("=== Re-exportando CSVs extendidos con precisión float32 completa nativa ===")
    for alma in CORPORA:
        rows = data_ext[alma]
        ids = data_ext[f"ids_{alma}"]
        texts = data_ext[f"texts_{alma}"]
        csv_file = EXTENDED_DIR / f"{alma}_extendido_1024d.csv"

        dim_count = rows.shape[1]
        header = ["id", "texto_clausula"] + [f"dim_{i}" for i in range(dim_count)]

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for i in range(len(ids)):
                # f'{float(val):.17g}' preserva la mantisa completa de cada float32 nativo sin redondeo
                row_vals = [f"{float(val):.17g}" for val in rows[i]]
                writer.writerow([str(ids[i]), str(texts[i])] + row_vals)

        file_size_mb = csv_file.stat().st_size / (1024 * 1024)
        print(f"Exportado: {csv_file.name} ({len(ids)} filas × {dim_count} dims, {file_size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

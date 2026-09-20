#!/usr/bin/env python3
"""Inspección dimensional profunda dual-engine (BGE-M3 1024-D vs Qwen2 1.5B 1536-D).

Procesa los 5 corpus extendidos de 110 cláusulas (python, legal, receta, medicina, astronomia)
a través de BAAI/bge-m3 y Alibaba-NLP/gte-Qwen2-1.5B-instruct de forma estrictamente secuencial,
computa la geometría dimensional exacta en los 10 pares canónicos sin similitud coseno,
exporta coordenadas y excitaciones con precisión float32 nativa IEEE 754 completa (f'{val:.17g}')
y sintetiza el ledger comparativo inmutable.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import resource
import subprocess
import sys
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np

from ddi_fw.adapters.base import BaseEmbedder
from ddi_fw.adapters.bge import BGE_M3_ID, BGEM3Embedder
from ddi_fw.adapters.qwen2 import QWEN2_ID, Qwen2Embedder
from ddi_fw.almas import ALMA_NAMES, load_almas
from ddi_fw.embedder import embed_mazos, save_rows
from ddi_fw.hoja import CANONICAL_PAIRS, candados_canonicos
from ddi_fw.press import press

ROOT_DIR = Path(__file__).resolve().parent.parent
EXTENDED_DATA_DIR = ROOT_DIR / "ddi_fw" / "data" / "extended"
BGE_OUT_DIR = ROOT_DIR / "ddi_fw" / "out" / "extended_bge"
QWEN2_OUT_DIR = ROOT_DIR / "ddi_fw" / "out" / "extended_qwen2"
HISTORICAL_BASELINE = ROOT_DIR / "ddi_fw" / "out" / "rows.npz"
LEDGER_REPORT_PATH = (
    ROOT_DIR / "current-research" / "engines" / "dual-engine-extended-inspection.md"
)


def get_rss_mb() -> float:
    """Devuelve el consumo de memoria RSS en megabytes para el proceso actual."""
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux: ru_maxrss en kB. macOS: ru_maxrss en bytes.
    if usage > 10**7:
        return usage / (1024 * 1024)
    return usage / 1024


def compute_tensor_sha256(matrices: dict[str, np.ndarray]) -> str:
    """Calcula el hash criptográfico SHA-256 de los tensores concatenados en orden canónico."""
    hasher = hashlib.sha256()
    for alma in ALMA_NAMES:
        mat = np.asarray(matrices[alma], dtype=np.float32)
        hasher.update(alma.encode("utf-8"))
        hasher.update(mat.tobytes())
    return hasher.hexdigest()


def compute_coordinate_extrema(matrices: dict[str, np.ndarray]) -> dict[str, dict[str, str]]:
    """Calcula los mínimos y máximos exactos en IEEE 754 float32 nativo para cada alma."""
    extrema: dict[str, dict[str, str]] = {}
    for alma in ALMA_NAMES:
        mat = matrices[alma]
        min_v = float(np.min(mat))
        max_v = float(np.max(mat))
        extrema[alma] = {
            "min": f"{min_v:.17g}",
            "max": f"{max_v:.17g}",
        }
    return extrema


def export_extended_csvs(
    out_dir: Path,
    matrices: dict[str, np.ndarray],
    ids: dict[str, list[str]],
    texts: dict[str, list[str]],
    dimension: int,
) -> list[Path]:
    """Exporta las coordenadas de cada alma preservando la mantisa completa f'{float(val):.17g}'."""
    out_dir.mkdir(parents=True, exist_ok=True)
    exported_files = []
    header = ["id", "texto_clausula"] + [f"dim_{i}" for i in range(dimension)]

    for alma in ALMA_NAMES:
        csv_path = out_dir / f"{alma}_extendido_{dimension}d.csv"
        rows = matrices[alma]
        alma_ids = ids[alma]
        alma_texts = texts[alma]

        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            for i in range(len(alma_ids)):
                coords = [f"{float(val):.17g}" for val in rows[i]]
                writer.writerow([str(alma_ids[i]), str(alma_texts[i])] + coords)

        exported_files.append(csv_path)
    return exported_files


def export_top500_excitadas(
    out_dir: Path,
    matrices: dict[str, np.ndarray],
    dimension: int,
) -> list[Path]:
    """Calcula y exporta el Top 500 de dimensiones más excitadas usando aritmética exacta Decimal."""
    out_dir.mkdir(parents=True, exist_ok=True)
    exported_files = []
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

    for alma in ALMA_NAMES:
        mat = matrices[alma]
        num_rows = mat.shape[0]
        csv_path = out_dir / f"{alma}_top500_dimensiones_excitadas.csv"

        dims_stats = []
        for d in range(dimension):
            col_raw = mat[:, d]
            v_min_raw = float(np.min(col_raw))
            v_max_raw = float(np.max(col_raw))

            # Decimal exacto basado en la representación IEEE 754 de cada valor
            col_dec = [Decimal(f"{float(v):.17g}") for v in col_raw]
            v_min_dec = min(col_dec)
            v_max_dec = max(col_dec)
            peak_abs_dec = max(abs(v_min_dec), abs(v_max_dec))
            mean_abs_dec = sum(abs(v) for v in col_dec) / Decimal(num_rows)
            rango_dec = v_max_dec - v_min_dec

            dims_stats.append(
                {
                    "dim": f"dim_{d}",
                    "axis": d,
                    "val_min_dec": v_min_dec,
                    "val_max_dec": v_max_dec,
                    "peak_abs_dec": peak_abs_dec,
                    "mean_abs_dec": mean_abs_dec,
                    "rango_dec": rango_dec,
                    "val_min_raw": v_min_raw,
                    "val_max_raw": v_max_raw,
                }
            )

        # Ranking por excitación media absoluta
        dims_by_mean = sorted(dims_stats, key=lambda x: x["mean_abs_dec"], reverse=True)
        mean_rank_map = {item["axis"]: rank for rank, item in enumerate(dims_by_mean, 1)}

        # Ranking por excitación pico absoluta (Top 500)
        dims_by_peak = sorted(dims_stats, key=lambda x: x["peak_abs_dec"], reverse=True)
        top500 = dims_by_peak[:500]

        for rank, item in enumerate(top500, 1):
            item["ranking"] = rank
            item["ranking_media_abs"] = mean_rank_map[item["axis"]]

        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(fieldnames)
            for item in top500:
                writer.writerow(
                    [
                        item["ranking"],
                        item["dim"],
                        item["axis"],
                        str(item["val_max_dec"]),
                        str(item["val_min_dec"]),
                        str(item["peak_abs_dec"]),
                        str(item["mean_abs_dec"]),
                        str(item["rango_dec"]),
                        f"{item['val_max_raw']:.17g}",
                        f"{item['val_min_raw']:.17g}",
                        item["ranking_media_abs"],
                    ]
                )

        exported_files.append(csv_path)
    return exported_files


def run_engine_inspection(engine_name: str, out_dir: Path) -> dict[str, Any]:
    """Ejecuta la inspección completa para un solo motor de embedding y devuelve métricas."""
    print("\n=======================================================")
    print(f"  INICIANDO MOTOR: {engine_name}")
    print(f"  Destino de salida: {out_dir}")
    print("=======================================================")

    # Validar protección del baseline histórico
    if out_dir.resolve() == HISTORICAL_BASELINE.parent.resolve():
        raise ValueError(
            "Violación de seguridad: intento de escribir en el directorio base ddi_fw/out/"
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Cargar corpus extendido
    print(f"Cargando los 5 almas desde {EXTENDED_DATA_DIR}...")
    mazos = load_almas(EXTENDED_DATA_DIR)
    for alma in ALMA_NAMES:
        if mazos[alma].n != 110:
            raise ValueError(
                f"Corpus {alma} tiene {mazos[alma].n} cláusulas (debe ser exactamente 110)"
            )
    total_clauses = sum(mazos[a].n for a in ALMA_NAMES)
    print(f"Corpus validado: 5 almas × 110 cláusulas = {total_clauses} cláusulas en total.")

    # 2. Instanciar embedder
    embedder: BaseEmbedder
    if engine_name == "bge":
        embedder = BGEM3Embedder.instance()
    elif engine_name == "qwen2":
        embedder = Qwen2Embedder.instance()
    else:
        raise ValueError(f"Motor no reconocido: {engine_name}")

    print(f"Embedder cargado: {embedder.model_id} (D={embedder.dimension})")

    # 3. Codificar cláusulas y registrar latencia
    rss_before = get_rss_mb()
    t_start = time.perf_counter()
    matrices, ids = embed_mazos(mazos, embedder)
    t_elapsed = time.perf_counter() - t_start
    rss_after = get_rss_mb()

    latency_us_per_clause = (t_elapsed / total_clauses) * 1_000_000
    print("Codificación finalizada:")
    print(f"  - Latencia total: {t_elapsed:.3f} s")
    print(f"  - Latencia por cláusula: {latency_us_per_clause:.1f} µs/cláusula")
    print(f"  - Memoria RSS proceso: {rss_after:.1f} MB (delta: +{rss_after - rss_before:.1f} MB)")

    # 4. Guardar rows.npz
    texts = {alma: mazo.texts() for alma, mazo in mazos.items()}
    rows_path = out_dir / "rows.npz"
    save_rows(rows_path, matrices, ids, texts, embedder)
    print(f"Guardado rows.npz: {rows_path} ({rows_path.stat().st_size / (1024 * 1024):.2f} MB)")

    # 5. Medición dimensional no podada (measure_and_save)
    locks = candados_canonicos(matrices)
    measure_audit: dict[str, Any] = {
        "model_id": embedder.model_id,
        "dimension": embedder.dimension,
        "n": {alma: int(matrices[alma].shape[0]) for alma in ALMA_NAMES},
        "published": {key: lock.published for key, lock in locks.items()},
        "disjoint_count": {key: lock.disjoint_count for key, lock in locks.items()},
        "disjoint_axes": {key: lock.ejes_disjuntos for key, lock in locks.items()},
        "dropped": [],
        "rows_path": str(rows_path),
    }
    audit_path = out_dir / "measure_audit.json"
    audit_path.write_text(json.dumps(measure_audit, indent=2) + "\n", encoding="utf-8")
    print(f"Guardado measure_audit.json: {audit_path}")

    # 6. Censo fila por fila (press)
    print("Ejecutando press() para censo y recuento de votos en los 10 pares canónicos...")
    press(rows_path, out_dir)
    print(f"Guardado press.json en {out_dir / 'press.json'}")

    # 7. Exportación de CSVs con mantisa IEEE 754 completa sin redondeo
    print(f"Exportando coordenadas float32 nativas ({embedder.dimension}d) con f'{{val:.17g}}'...")
    coord_files = export_extended_csvs(out_dir, matrices, ids, texts, embedder.dimension)
    print(f"  Exportados {len(coord_files)} archivos de coordenadas.")

    # 8. Cálculo de Top 500 dimensiones más excitadas con exact Decimal
    print("Calculando Top 500 dimensiones excitadas con aritmética exacta Decimal...")
    top500_files = export_top500_excitadas(out_dir, matrices, embedder.dimension)
    print(f"  Exportados {len(top500_files)} archivos de Top 500.")

    # 9. Hashes y extremos
    tensor_hash = compute_tensor_sha256(matrices)
    extrema = compute_coordinate_extrema(matrices)

    # 10. Limpieza de memoria
    del embedder
    del matrices
    del ids
    del texts
    del mazos
    del locks
    gc.collect()

    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif hasattr(torch, "mps") and hasattr(torch.mps, "empty_cache"):
            torch.mps.empty_cache()
    except Exception:
        pass

    metrics = {
        "engine": engine_name,
        "model_id": BGE_M3_ID if engine_name == "bge" else QWEN2_ID,
        "dimension": 1024 if engine_name == "bge" else 1536,
        "total_latency_s": t_elapsed,
        "latency_us_per_clause": latency_us_per_clause,
        "memory_rss_mb": rss_after,
        "tensor_hash": tensor_hash,
        "extrema": extrema,
        "locks": {
            pair: {
                "published": measure_audit["published"][pair],
                "disjoint_count": measure_audit["disjoint_count"][pair],
            }
            for pair in [f"{a}_{b}" for a, b in CANONICAL_PAIRS]
        },
    }

    metrics_path = out_dir / "execution_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"Métricas del motor guardadas en: {metrics_path}")
    return metrics


def synthesize_ledger_report(bge_metrics: dict[str, Any], qwen2_metrics: dict[str, Any]) -> str:
    """Genera el reporte comparativo inmutable en Markdown con las 3 tablas especificadas."""
    pairs_list = [f"{a}_{b}" for a, b in CANONICAL_PAIRS]

    # Tabla 1: Engine Performance & Geometry Ledger (10 Canonical Pairs)
    table_1_rows = []
    for pair in pairs_list:
        bge_pub = "published" if bge_metrics["locks"][pair]["published"] else "unpublished"
        bge_cnt = bge_metrics["locks"][pair]["disjoint_count"]
        qwen_pub = "published" if qwen2_metrics["locks"][pair]["published"] else "unpublished"
        qwen_cnt = qwen2_metrics["locks"][pair]["disjoint_count"]
        table_1_rows.append(f"| `{pair}` | `{bge_pub}` | {bge_cnt} | `{qwen_pub}` | {qwen_cnt} |")
    table_1_content = "\n".join(table_1_rows)

    # Tabla 2: Computational Footprint
    bge_lat = f"{bge_metrics['latency_us_per_clause']:.1f}"
    bge_rss = f"{bge_metrics['memory_rss_mb']:.1f}"
    bge_hash = bge_metrics["tensor_hash"]

    qwen_lat = f"{qwen2_metrics['latency_us_per_clause']:.1f}"
    qwen_rss = f"{qwen2_metrics['memory_rss_mb']:.1f}"
    qwen_hash = qwen2_metrics["tensor_hash"]

    # Tabla 3: Coordinate Extrema Table (Full IEEE 754 float32)
    table_3_rows = []
    for alma in ALMA_NAMES:
        bge_min = bge_metrics["extrema"][alma]["min"]
        bge_max = bge_metrics["extrema"][alma]["max"]
        qwen_min = qwen2_metrics["extrema"][alma]["min"]
        qwen_max = qwen2_metrics["extrema"][alma]["max"]
        table_3_rows.append(
            f"| `{alma}` | `{bge_min}` | `{bge_max}` | `{qwen_min}` | `{qwen_max}` |"
        )
    table_3_content = "\n".join(table_3_rows)

    report = f"""# Dual-Engine Deep Dimensional Inspection Ledger (5 Almas × 2 Embedding Engines)

- **Date**: {time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())}
- **Methodology**: Non-cosine, interval-bounded semantic firewall (`[lo_d, hi_d]`, `gap > 0`), zero heuristic rounding.
- **Corpora**: 5 canonical almas (`python`, `legal`, `receta`, `medicina`, `astronomia`), 110 clauses each ($N=110$), cross-domain pairwise Jaccard $< 0.05$.
- **Precision**: Full IEEE 754 float32 mantissa preserved via `f'{{float(val):.17g}}'` and exact `decimal.Decimal` arithmetic.
- **Sequential Isolation**: Strictly sequential process execution with garbage collection and cache clearance between engines.

---

## 1. Engine Performance & Geometry Ledger (10 Canonical Pairs)

| Pair | BGE-M3 (1024-D) Published | BGE-M3 Disjoint Count | Qwen2 1.5B (1536-D) Published | Qwen2 1.5B Disjoint Count |
| :--- | :---: | :---: | :---: | :---: |
{table_1_content}

> [!NOTE]
> En mazos crudos extendidos de 110 cláusulas completas sin poda (`--no-prune`), ningún candado fabrica brechas artificiales con $\\epsilon$-relaxations. La publicación es estrictamente condicional a $\\text{{disjoint\\_count}} > 0$. Si $\\text{{disjoint\\_count}} == 0$, el candado permanece `unpublished` (`ok_unpublished`), satisfaciendo la invariante de fail-closed.

---

## 2. Computational Footprint

| Engine | Latency per Clause ($\\mu\\text{{s}}$) | Memory Footprint (RSS MB) | Output Tensor Hash (SHA-256) |
| :--- | :---: | :---: | :---: |
| `{bge_metrics["model_id"]}` | {bge_lat} | {bge_rss} | `{bge_hash}` |
| `{qwen2_metrics["model_id"]}` | {qwen_lat} | {qwen_rss} | `{qwen_hash}` |

---

## 3. Coordinate Extrema Table (Full IEEE 754 float32)

Valores exactos de cota inferior mínima y cota superior máxima a lo largo de todas las dimensiones ($1024$ o $1536$), exportados sin ningún redondeo o truncamiento decimal:

| Alma | BGE-M3 Min | BGE-M3 Max | Qwen2 1.5B Min | Qwen2 1.5B Max |
| :--- | :--- | :--- | :--- | :--- |
{table_3_content}

---

## 4. Audit Artefacts Index

- **BGE-M3 (1024-D)**:
  - Raw Tensors: `ddi_fw/out/extended_bge/rows.npz`
  - Geometric Audit: `ddi_fw/out/extended_bge/measure_audit.json`
  - Census & Votes: `ddi_fw/out/extended_bge/press.json`
  - Coordinates ($5 \\times$ CSV): `ddi_fw/out/extended_bge/{alma}_extendido_1024d.csv`
  - Top 500 ($5 \\times$ CSV): `ddi_fw/out/extended_bge/{alma}_top500_dimensiones_excitadas.csv`
- **Qwen2 1.5B (1536-D)**:
  - Raw Tensors: `ddi_fw/out/extended_qwen2/rows.npz`
  - Geometric Audit: `ddi_fw/out/extended_qwen2/measure_audit.json`
  - Census & Votes: `ddi_fw/out/extended_qwen2/press.json`
  - Coordinates ($5 \\times$ CSV): `ddi_fw/out/extended_qwen2/{alma}_extendido_1536d.csv`
  - Top 500 ($5 \\times$ CSV): `ddi_fw/out/extended_qwen2/{alma}_top500_dimensiones_excitadas.csv`
- **Historical Baseline**: `ddi_fw/out/rows.npz` (UNTOUCHED & PRESERVED).
"""
    LEDGER_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReporte comparativo generado con éxito en: {LEDGER_REPORT_PATH}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Orquestador secuencial de inspección dual-engine."
    )
    parser.add_argument(
        "--engine",
        choices=["bge", "qwen2", "all"],
        default="all",
        help="Motor a ejecutar ('bge', 'qwen2', o 'all' secuencial)",
    )
    args = parser.parse_args(argv)

    if args.engine == "bge":
        run_engine_inspection("bge", BGE_OUT_DIR)
        return 0
    elif args.engine == "qwen2":
        run_engine_inspection("qwen2", QWEN2_OUT_DIR)
        return 0

    print("======================================================================")
    print("  DDI-FW: INSPECCIÓN DUAL-ENGINE SECUENCIAL (5 ALMAS × 2 ENGINES)   ")
    print("======================================================================")

    # 1. Ejecutar Engine 1: BGE-M3 en subproceso aislado
    print("\n>>> EJECUTANDO SUBPROCESO AISLADO PARA BAAI/bge-m3 (1024-D)...")
    res_bge = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--engine", "bge"],
        check=True,
    )
    if res_bge.returncode != 0:
        print("Error en ejecución de BGE-M3", file=sys.stderr)
        return 1

    # 2. Ejecutar Engine 2: Qwen2-1.5B en subproceso aislado
    print(
        "\n>>> EJECUTANDO SUBPROCESO AISLADO PARA Alibaba-NLP/gte-Qwen2-1.5B-instruct (1536-D)..."
    )
    res_qwen2 = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--engine", "qwen2"],
        check=True,
    )
    if res_qwen2.returncode != 0:
        print("Error en ejecución de Qwen2-1.5B", file=sys.stderr)
        return 1

    # 3. Leer métricas de ambos motores
    bge_metrics = json.loads((BGE_OUT_DIR / "execution_metrics.json").read_text(encoding="utf-8"))
    qwen2_metrics = json.loads(
        (QWEN2_OUT_DIR / "execution_metrics.json").read_text(encoding="utf-8")
    )

    # 4. Sintetizar reporte
    synthesize_ledger_report(bge_metrics, qwen2_metrics)

    print("\n¡EJECUCIÓN DUAL-ENGINE COMPLETADA SATISFACTORIAMENTE!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

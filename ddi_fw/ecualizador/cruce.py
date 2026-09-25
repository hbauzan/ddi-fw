"""Protocolo 03 — Cruce Multi-Corpus de Trigos (Todos contra Todos).

Analiza las dimensiones de trigo depurado a través de los 10 pares canónicos:
- Computa Delta_mu y el Índice de Separabilidad Normalizada S_d.
- Detecta ruido secundario residual (S_d < 0.5).
- Extrae la firma espectral de Python frente a los 4 temas restantes.
- Exporta cruce_ranking_10_pares.csv y python_firma_espectral.json.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ddi_fw.ecualizador.intrinseco import fmt_float
from ddi_fw.hardware import get_hardware_profile

DEFAULT_CRUCE_DIR = Path(__file__).resolve().parents[1] / "out" / "ecualizador" / "cruce_trigos"
DEFAULT_RUIDO_DIR = Path(__file__).resolve().parents[1] / "out" / "ecualizador" / "ruido"
DEFAULT_INTRINSECO_DIR = Path(__file__).resolve().parents[1] / "out" / "ecualizador" / "intrinseco"

PARES_CANONICOS = (
    ("python", "receta"),
    ("python", "legal"),
    ("legal", "receta"),
    ("python", "medicina"),
    ("python", "astronomia"),
    ("legal", "medicina"),
    ("legal", "astronomia"),
    ("receta", "medicina"),
    ("receta", "astronomia"),
    ("medicina", "astronomia"),
)


def compute_pair_metrics(
    mu_a: float,
    sigma_a: float,
    mu_b: float,
    sigma_b: float,
) -> tuple[float, float]:
    """Calcula Delta_mu y separabilidad normalizada S_d entre dos temas para una coordenada."""
    delta_mu = abs(mu_a - mu_b)
    denom = sigma_a + sigma_b
    if denom <= 1e-12:
        sd = 0.0
    else:
        sd = delta_mu / denom
    return delta_mu, sd


def run_protocolo_03(
    intrinseco_dir: Path = DEFAULT_INTRINSECO_DIR,
    ruido_dir: Path = DEFAULT_RUIDO_DIR,
    out_dir: Path = DEFAULT_CRUCE_DIR,
    sd_umbral_firma: float = 1.5,
    almas: tuple[str, ...] | list[str] | None = None,
    pares: list[tuple[str, str]] | tuple[tuple[str, str], ...] | None = None,
    paja_dir: Path | None = None,
) -> dict[str, Any]:
    """Ejecuta el cruce de pares sobre los trigos depurados."""
    import itertools

    out_dir.mkdir(parents=True, exist_ok=True)
    from ddi_fw.ecualizador import ALMAS_ECUALIZADOR

    almas_to_process = tuple(almas) if almas is not None else ALMAS_ECUALIZADOR
    if pares is not None:
        pares_to_process = tuple(pares)
    elif almas is not None:
        pares_to_process = tuple(itertools.combinations(almas_to_process, 2))
    else:
        pares_to_process = PARES_CANONICOS

    # 1. Cargar el catálogo de ruido para conocer las dimensiones de trigo candidato
    cat_dir = paja_dir or ruido_dir
    cat_path = cat_dir / "catalogo_ruido_estructural.json"
    if not cat_path.exists():
        cat_path = cat_dir / "catalogo_paja_estructural.json"
    if not cat_path.exists():
        raise FileNotFoundError(f"Falta {cat_path}: ejecute Protocolo 02 primero.")
    cat_meta = json.loads(cat_path.read_text(encoding="utf-8"))
    trigo_dims = {
        r["dimension"]: r for r in cat_meta["dimensiones"] if r["etiqueta"] == "TRIGO_CANDIDATO"
    }

    # 2. Cargar perfiles intrínsecos de cada alma
    perfiles: dict[str, dict[int, dict[str, float]]] = {}
    for a in almas_to_process:
        prof_path = intrinseco_dir / f"{a}_perfil_intrinseco_1024d.json"
        data = json.loads(prof_path.read_text(encoding="utf-8"))
        perfiles[a] = {rec["dimension"]: rec for rec in data["dimensiones"]}

    hardware_info = get_hardware_profile()

    # 3. Calcular Delta_mu y S_d para todos los pares en cada dimensión de trigo
    sorted_trigo_dims = sorted(trigo_dims.keys())
    cruce_records: list[dict[str, Any]] = []

    # Estadísticas de ruido secundario por par
    ruido_secundario_por_par: dict[str, int] = {}
    excelentes_por_par: dict[str, int] = {}

    for d in sorted_trigo_dims:
        row: dict[str, Any] = {"dimension": d}
        for a, b in pares_to_process:
            pair_key = f"{a}_{b}"
            rec_a = perfiles[a][d]
            rec_b = perfiles[b][d]
            delta_mu, sd = compute_pair_metrics(
                rec_a["mu"], rec_a["sigma"], rec_b["mu"], rec_b["sigma"]
            )
            row[f"delta_mu_{pair_key}"] = delta_mu
            row[f"sd_{pair_key}"] = sd

        cruce_records.append(row)

    # Contabilizar ruido secundario (Sd < 0.5) y excelentes (Sd > 2.0)
    for a, b in pares_to_process:
        pair_key = f"{a}_{b}"
        sds = [r[f"sd_{pair_key}"] for r in cruce_records]
        ruido_secundario_por_par[pair_key] = sum(1 for s in sds if s < 0.5)
        excelentes_por_par[pair_key] = sum(1 for s in sds if s >= 2.0)

    # 4. Exportar cruce_ranking_{N}_pares.csv
    num_pares = len(pares_to_process)
    csv_filename = f"cruce_ranking_{num_pares}_pares.csv" if num_pares != 10 else "cruce_ranking_10_pares.csv"
    csv_path = out_dir / csv_filename
    headers = ["dimension"]
    for a, b in pares_to_process:
        pair_key = f"{a}_{b}"
        headers.extend([f"delta_mu_{pair_key}", f"sd_{pair_key}"])

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in cruce_records:
            row_vals: list[Any] = [r["dimension"]]
            for a, b in pares_to_process:
                pair_key = f"{a}_{b}"
                row_vals.append(fmt_float(r[f"delta_mu_{pair_key}"]))
                row_vals.append(fmt_float(r[f"sd_{pair_key}"]))
            writer.writerow(row_vals)

    # 5. Extracción de la Firma Espectral Exclusiva de Python (si python está en los almas)
    pares_python = [
        (a, b) for a, b in pares_to_process if a == "python" or b == "python"
    ]
    python_candidates: list[dict[str, Any]] = []

    if "python" in almas_to_process and pares_python:
        for r in cruce_records:
            d = r["dimension"]
            sds_py = [r[f"sd_{a}_{b}"] for a, b in pares_python]
            deltas_py = [r[f"delta_mu_{a}_{b}"] for a, b in pares_python]

            min_sd_py = min(sds_py)
            min_delta_py = min(deltas_py)
            avg_sd_py = sum(sds_py) / len(sds_py)
            avg_delta_py = sum(deltas_py) / len(deltas_py)

            py_profile = perfiles["python"][d]
            c_entry: dict[str, Any] = {
                "dimension": d,
                "min_sd": min_sd_py,
                "avg_sd": avg_sd_py,
                "min_delta_mu": min_delta_py,
                "avg_delta_mu": avg_delta_py,
                "mu_python": py_profile["mu"],
                "sigma_python": py_profile["sigma"],
                "lo_python": py_profile["lo"],
                "hi_python": py_profile["hi"],
                "pico_python": py_profile["pico"],
                "energia_python": py_profile["energia"],
                "coherencia_python": py_profile["coherencia_signo"],
                "cumple_umbral_1_5": bool(min_sd_py >= sd_umbral_firma),
            }
            for a, b in pares_python:
                other = b if a == "python" else a
                c_entry[f"sd_vs_{other}"] = r[f"sd_{a}_{b}"]
                c_entry[f"delta_mu_vs_{other}"] = r[f"delta_mu_{a}_{b}"]

            python_candidates.append(c_entry)

    # Ordenar candidatos de Python por min_sd descendente
    python_candidates.sort(key=lambda c: c["min_sd"], reverse=True)

    dims_cumplen = [c for c in python_candidates if c["cumple_umbral_1_5"]]

    # 6. Exportar python_firma_espectral.json
    json_py_path = out_dir / "python_firma_espectral.json"
    py_firma_meta = {
        "protocolo": "03-protocolo-cruce-trigos",
        "hardware": hardware_info,
        "umbral_sd_requerido": sd_umbral_firma,
        "total_trigos_evaluados": len(cruce_records),
        "conteo_dimensiones_cumplen_sd_1_5": len(dims_cumplen),
        "diagnostico_hipotesis": (
            "CONFIRMADA_FUERTE" if len(dims_cumplen) > 0 else "NO_ALCANZA_UMBRAL_1_5_SIMULTANEO"
        ),
        "max_min_sd_alcanzado": (python_candidates[0]["min_sd"] if python_candidates else 0.0),
        "top_10_dimensiones_discriminantes_python": python_candidates[:10],
        "ruido_secundario_por_par": ruido_secundario_por_par,
        "paja_secundaria_por_par": ruido_secundario_por_par,
        "excelentes_por_par": excelentes_por_par,
        "todas_dimensiones_ranking_python": python_candidates,
    }
    json_py_path.write_text(
        json.dumps(py_firma_meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "protocolo": "03-protocolo-cruce-trigos",
        "csv_path": str(csv_path),
        "json_path": str(json_py_path),
        "total_trigos": len(cruce_records),
        "conteo_cumplen_sd_1_5": len(dims_cumplen),
        "top_1_dim_python": (python_candidates[0]["dimension"] if python_candidates else None),
        "top_1_min_sd_python": (python_candidates[0]["min_sd"] if python_candidates else 0.0),
    }

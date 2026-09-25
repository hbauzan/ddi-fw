"""Protocolo 02 — Doble Poda del Ruido Estructural Basal.

Aplica dos criterios independientes sobre las 1024 dimensiones:
- Criterio A: Saturación universal (min_{c} E_d(c) >= theta)
- Criterio B: Indiferenciación temática (max_{c1, c2} |mu(c1) - mu(c2)| <= epsilon)

Clasifica cada dimensión en:
- RUIDO_AMBOS
- RUIDO_SATURADO
- RUIDO_PLANO
- TRIGO_CANDIDATO

Exporta el catálogo de ruido estructural y los archivos de trigo depurado por corpus.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ddi_fw.ecualizador import ALMAS_ECUALIZADOR
from ddi_fw.ecualizador.intrinseco import fmt_float
from ddi_fw.hardware import get_hardware_profile

DEFAULT_RUIDO_DIR = Path(__file__).resolve().parents[1] / "out" / "ecualizador" / "ruido"
DEFAULT_INTRINSECO_DIR = Path(__file__).resolve().parents[1] / "out" / "ecualizador" / "intrinseco"

# Umbrales canónicos determinados en análisis exploratorio
DEFAULT_THETA_SATURACION = 0.05
DEFAULT_EPSILON_INDIFERENCIACION = 0.010


# Constantes de clasificación
RUIDO_AMBOS = "RUIDO_AMBOS"
RUIDO_SATURADO = "RUIDO_SATURADO"
RUIDO_PLANO = "RUIDO_PLANO"
TRIGO_CANDIDATO = "TRIGO_CANDIDATO"

# Aliases de compatibilidad regresiva
PAJA_AMBOS = RUIDO_AMBOS
PAJA_SATURADA = RUIDO_SATURADO
PAJA_PLANA = RUIDO_PLANO


def classify_dimension(
    min_energy: float,
    max_delta_mu: float,
    theta_saturacion: float = DEFAULT_THETA_SATURACION,
    epsilon_indiferenciacion: float = DEFAULT_EPSILON_INDIFERENCIACION,
) -> str:
    """Clasifica una dimensión según los criterios A y B."""
    is_saturated = min_energy >= theta_saturacion
    is_flat = max_delta_mu <= epsilon_indiferenciacion

    if is_saturated and is_flat:
        return RUIDO_AMBOS
    if is_saturated:
        return RUIDO_SATURADO
    if is_flat:
        return RUIDO_PLANO
    return TRIGO_CANDIDATO


def run_protocolo_02(
    intrinseco_dir: Path = DEFAULT_INTRINSECO_DIR,
    out_dir: Path = DEFAULT_RUIDO_DIR,
    theta_saturacion: float = DEFAULT_THETA_SATURACION,
    epsilon_indiferenciacion: float = DEFAULT_EPSILON_INDIFERENCIACION,
    almas: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    """Ejecuta el Protocolo 02 leyendo los perfiles intrínsecos y generando trigos depurados."""
    out_dir.mkdir(parents=True, exist_ok=True)
    almas_to_process = tuple(almas) if almas is not None else ALMAS_ECUALIZADOR

    # 1. Cargar datos intrínsecos de cada alma
    almas_data: dict[str, dict[int, dict[str, float]]] = {}
    for alma in almas_to_process:
        json_file = intrinseco_dir / f"{alma}_perfil_intrinseco_1024d.json"
        if not json_file.exists():
            raise FileNotFoundError(
                f"Falta perfil intrínseco de {alma}: ejecute Protocolo 01 primero."
            )
        data = json.loads(json_file.read_text(encoding="utf-8"))
        # indexar por dimensión
        dim_map = {rec["dimension"]: rec for rec in data["dimensiones"]}
        almas_data[alma] = dim_map

    num_dims = len(almas_data[almas_to_process[0]])
    hardware_info = get_hardware_profile()

    catalogo_records: list[dict[str, Any]] = []
    conteo_clasificacion: dict[str, int] = {
        "RUIDO_AMBOS": 0,
        "RUIDO_SATURADO": 0,
        "RUIDO_PLANO": 0,
        "TRIGO_CANDIDATO": 0,
    }

    # 2. Analizar cada dimensión a través de los temas
    for d in range(num_dims):
        energies_d = {alma: almas_data[alma][d]["energia"] for alma in almas_to_process}
        mus_d = {alma: almas_data[alma][d]["mu"] for alma in almas_to_process}

        min_energy = float(min(energies_d.values()))
        max_energy = float(max(energies_d.values()))

        # Distancia máxima entre cualquier par de centros (max_{c1, c2} |mu_c1 - mu_c2|)
        mu_values = list(mus_d.values())
        max_delta_mu = float(max(mu_values) - min(mu_values))

        etiqueta = classify_dimension(
            min_energy=min_energy,
            max_delta_mu=max_delta_mu,
            theta_saturacion=theta_saturacion,
            epsilon_indiferenciacion=epsilon_indiferenciacion,
        )
        conteo_clasificacion[etiqueta] += 1

        rec = {
            "dimension": d,
            "etiqueta": etiqueta,
            "min_energia": min_energy,
            "max_energia": max_energy,
            "max_delta_mu": max_delta_mu,
        }
        for alma in almas_to_process:
            rec[f"mu_{alma}"] = mus_d[alma]
            rec[f"energia_{alma}"] = energies_d[alma]

        catalogo_records.append(rec)

    # 3. Exportar catalogo_ruido_estructural.csv
    csv_catalogo = out_dir / "catalogo_ruido_estructural.csv"
    headers = [
        "dimension",
        "etiqueta",
        "min_energia",
        "max_energia",
        "max_delta_mu",
    ]
    for alma in almas_to_process:
        headers.append(f"mu_{alma}")
    for alma in almas_to_process:
        headers.append(f"energia_{alma}")

    with open(csv_catalogo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in catalogo_records:
            row_vals: list[Any] = [
                r["dimension"],
                r["etiqueta"],
                fmt_float(r["min_energia"]),
                fmt_float(r["max_energia"]),
                fmt_float(r["max_delta_mu"]),
            ]
            for alma in almas_to_process:
                row_vals.append(fmt_float(r[f"mu_{alma}"]))
            for alma in almas_to_process:
                row_vals.append(fmt_float(r[f"energia_{alma}"]))
            writer.writerow(row_vals)

    # 4. Exportar catalogo_ruido_estructural.json
    json_catalogo = out_dir / "catalogo_ruido_estructural.json"
    catalogo_meta = {
        "protocolo": "02-protocolo-doble-poda-ruido",
        "hardware": hardware_info,
        "total_dimensiones": num_dims,
        "umbrales": {
            "theta_saturacion": theta_saturacion,
            "epsilon_indiferenciacion": epsilon_indiferenciacion,
        },
        "conteos": conteo_clasificacion,
        "dimensiones_ruido_ambos": [
            r["dimension"] for r in catalogo_records if r["etiqueta"] == "RUIDO_AMBOS"
        ],
        "dimensiones_ruido_saturada": [
            r["dimension"] for r in catalogo_records if r["etiqueta"] == "RUIDO_SATURADO"
        ],
        "dimensiones_ruido_plana": [
            r["dimension"] for r in catalogo_records if r["etiqueta"] == "RUIDO_PLANO"
        ],
        "total_trigo_candidato": conteo_clasificacion["TRIGO_CANDIDATO"],
        "dimensiones": catalogo_records,
    }
    json_catalogo.write_text(
        json.dumps(catalogo_meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # 5. Generar los Trigos Depurados por corpus: {alma}_trigo_depurado.csv
    trigo_dims = {r["dimension"] for r in catalogo_records if r["etiqueta"] == "TRIGO_CANDIDATO"}

    trigos_resumen: dict[str, str] = {}
    for alma in almas_to_process:
        csv_trigo = out_dir / f"{alma}_trigo_depurado.csv"
        # Obtener métricas intrínsecas de las dimensiones de trigo
        trigo_records = [almas_data[alma][d] for d in range(num_dims) if d in trigo_dims]
        # Ordenar por energía descendente
        trigo_records.sort(key=lambda r: r["energia"], reverse=True)

        headers_trigo = [
            "dimension",
            "ranking_trigo",
            "ranking_original",
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
        with open(csv_trigo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers_trigo)
            for rank_t, r in enumerate(trigo_records, start=1):
                writer.writerow(
                    [
                        r["dimension"],
                        rank_t,
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
        trigos_resumen[alma] = str(csv_trigo)

    return {
        "protocolo": "02-protocolo-doble-poda-ruido",
        "catalogo_csv": str(csv_catalogo),
        "catalogo_json": str(json_catalogo),
        "conteos": conteo_clasificacion,
        "total_trigo_candidato": conteo_clasificacion["TRIGO_CANDIDATO"],
        "trigos_depurados": trigos_resumen,
    }


# Aliases de compatibilidad regresiva
DEFAULT_PAJA_DIR = DEFAULT_RUIDO_DIR

#!/usr/bin/env python3
"""Pipeline ejecutor unificado para la Hipótesis del Ecualizador Espectral.

Permite ejecutar los protocolos 01 a 04 secuencialmente o de forma individual.
Uso:
    uv run python scripts/run_ecualizador_pipeline.py --all
    uv run python scripts/run_ecualizador_pipeline.py --protocolo 1
"""

from __future__ import annotations

import argparse
import sys

from ddi_fw.ecualizador.auditoria_decimal import run_protocolo_04
from ddi_fw.ecualizador.cruce import run_protocolo_03
from ddi_fw.ecualizador.intrinseco import run_protocolo_01
from ddi_fw.ecualizador.ruido import run_protocolo_02


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline ejecutor de la Hipótesis del Ecualizador Espectral (01 a 04)."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ejecuta la suite completa de protocolos 01 a 04.",
    )
    parser.add_argument(
        "--protocolo",
        type=int,
        choices=[1, 2, 3, 4],
        help="Ejecuta un protocolo específico (1, 2, 3 o 4).",
    )
    parser.add_argument(
        "--theta-saturacion",
        type=float,
        default=0.05,
        help="Umbral de energía basal para el Criterio A en Protocolo 02 (default: 0.05).",
    )
    parser.add_argument(
        "--epsilon-indiferenciacion",
        type=float,
        default=0.010,
        help="Umbral de contraste para el Criterio B en Protocolo 02 (default: 0.010).",
    )
    parser.add_argument(
        "--no-live-drift",
        action="store_true",
        help="Omite la inferencia live de BGE-M3 en Protocolo 04 usando valor base.",
    )

    args = parser.parse_args()

    if not args.all and args.protocolo is None:
        parser.print_help()
        sys.exit(1)

    print("=" * 70)
    print("HIPÓTESIS DEL ECUALIZADOR ESPECTRAL — PIPELINE DE INVESTIGACIÓN")
    print("=" * 70)

    if args.all or args.protocolo == 1:
        print("\n[1/4] Ejecutando Protocolo 01 — Extracción Intrínseca por Corpus...")
        p1_res = run_protocolo_01()
        print("  ✓ Finalizado. Corpus analizados:")
        for alma, d in p1_res["almas"].items():
            print(
                f"    - {alma:12s}: {d['num_clausulas']} cláusulas | "
                f"Top-1 dim: {d['top_1_dim']} (E={d['top_1_energia']:.6f})"
            )

    if args.all or args.protocolo == 2:
        print("\n[2/4] Ejecutando Protocolo 02 — Doble Poda del Ruido Estructural...")
        p2_res = run_protocolo_02(
            theta_saturacion=args.theta_saturacion,
            epsilon_indiferenciacion=args.epsilon_indiferenciacion,
        )
        print("  ✓ Finalizado. Clasificación de 1024 dimensiones:")
        for label, count in p2_res["conteos"].items():
            print(f"    - {label:18s}: {count:4d}")
        print(f"  ✓ Catálogo guardado en: {p2_res['catalogo_json']}")

    if args.all or args.protocolo == 3:
        print("\n[3/4] Ejecutando Protocolo 03 — Cruce Multi-Corpus de Trigos...")
        p3_res = run_protocolo_03()
        print(f"  ✓ Trigos evaluados: {p3_res['total_trigos']}")
        print(
            f"  ✓ Dimensiones con Sd >= 1.5 simultáneo en Python: {p3_res['conteo_cumplen_sd_1_5']}"
        )
        print(
            f"  ✓ Top-1 dimensión discriminante Python: {p3_res['top_1_dim_python']} "
            f"(min_Sd={p3_res['top_1_min_sd_python']:.6f})"
        )
        print("  ✓ Ranking y firma espectral exportados.")

    if args.all or args.protocolo == 4:
        print("\n[4/4] Ejecutando Protocolo 04 — Auditoría de Profundidad Decimal y Deriva...")
        p4_res = run_protocolo_04(run_live_drift=not args.no_live_drift)
        print(
            f"  ✓ Delta min (peor eje): {p4_res['delta_min']:.17g} (N_dec = {p4_res['n_dec_min']})"
        )
        print(f"  ✓ Deriva GPU vs CPU: {p4_res['deriva_max']:.17g}")
        print(f"  ✓ Ratio de Inmunidad Física: {p4_res['ratio_inmunidad']:.2f}x (Umbral > 100x)")
        print(
            f"  ✓ Veredicto de Inmunidad: "
            f"{'INMUNE' if p4_res['inmunidad_confirmada'] else 'NO INMUNE'}"
        )
        print(f"  ✓ Auditoría guardada en: {p4_res['out_file']}")

    print("\n" + "=" * 70)
    print("PIPELINE DEL ECUALIZADOR ESPECTRAL COMPLETADO CON ÉXITO")
    print("=" * 70)


if __name__ == "__main__":
    main()

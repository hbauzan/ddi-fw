"""CLI de censo fila por fila. No re-embebe. Cero campos mean_*."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from ddi_fw.corte import VOTE_NAMES, etiquetar_fila, recuento_votos
from ddi_fw.embedder import DEFAULT_OUT, load_rows, rows_matrices
from ddi_fw.hoja import CANONICAL_PAIRS, candados_canonicos, pair_id

HEADLINE_PAIR = ("python", "receta")


def _ids(bundle: dict[str, object], alma: str) -> list[str]:
    key = f"ids_{alma}"
    if key not in bundle:
        rows = np.asarray(bundle[alma])
        return [f"{alma}-{index}" for index in range(rows.shape[0])]
    return [str(item) for item in np.asarray(bundle[key]).tolist()]


def _extrema(counts: list[dict[str, int]]) -> dict[str, dict[str, int]]:
    extrema: dict[str, dict[str, int]] = {}
    for name in VOTE_NAMES.values():
        values = [row[name] for row in counts]
        extrema[name] = {"lo": min(values), "hi": max(values)}
    return extrema


def census_pair(
    bundle: dict[str, object],
    alma_a: str,
    alma_b: str,
) -> dict[str, Any]:
    matrices = rows_matrices(bundle)
    candado = candados_canonicos(matrices)[pair_id(alma_a, alma_b)]
    hoja = candado.hoja
    families: dict[str, Any] = {}
    vote_matrices: dict[str, np.ndarray] = {}
    for alma in (alma_a, alma_b):
        rows = matrices[alma]
        labels: dict[str, int] = {"left": 0, "right": 0, "split": 0, "out": 0}
        row_counts: list[dict[str, int]] = []
        votes = []
        detail = []
        for index, vector in enumerate(rows):
            label, voto = etiquetar_fila(vector, hoja)
            labels[label] += 1
            counts = recuento_votos(voto)
            row_counts.append(counts)
            votes.append(voto)
            detail.append(
                {
                    "id": _ids(bundle, alma)[index],
                    "alma": alma,
                    "label": label,
                    "votes": counts,
                    "disjoint_votes": {
                        str(axis): int(voto[axis]) for axis in hoja.ejes_disjuntos()
                    },
                }
            )
        families[alma] = {
            "n": int(rows.shape[0]),
            "census": labels,
            "vote_count_extrema": _extrema(row_counts),
            "rows": detail,
        }
        vote_matrices[alma] = (
            np.stack(votes, axis=0) if votes else np.zeros((0, hoja.dimension), dtype=np.uint8)
        )
    return {
        "alma_a": alma_a,
        "alma_b": alma_b,
        "disjoint_axes": hoja.ejes_disjuntos(),
        "disjoint_count": candado.disjoint_count,
        "published": candado.published,
        "families": families,
        "vote_matrices": vote_matrices,
    }


def assert_no_mean_fields(payload: object) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key).startswith("mean_") or str(key) == "mean":
                raise ValueError(f"campo de promedio prohibido: {key}")
            assert_no_mean_fields(value)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_mean_fields(item)


def write_csv(path: Path, pair_report: dict[str, Any]) -> None:
    axes = pair_report["disjoint_axes"]
    fieldnames = ["alma", "id", "label", *[f"axis_{axis}" for axis in axes]]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for alma, family in pair_report["families"].items():
            for row in family["rows"]:
                record = {"alma": alma, "id": row["id"], "label": row["label"]}
                for axis in axes:
                    record[f"axis_{axis}"] = row["disjoint_votes"].get(str(axis), "")
                writer.writerow(record)


def press(rows_path: Path, out_dir: Path) -> dict[str, Any]:
    if not rows_path.is_file():
        raise FileNotFoundError(f"no existe rows.npz: {rows_path}")
    bundle = load_rows(rows_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    pairs: dict[str, Any] = {}
    headline_votes: dict[str, np.ndarray] | None = None
    for alma_a, alma_b in CANONICAL_PAIRS:
        report = census_pair(bundle, alma_a, alma_b)
        vote_matrices = report.pop("vote_matrices")
        key = pair_id(alma_a, alma_b)
        pairs[key] = report
        if (alma_a, alma_b) == HEADLINE_PAIR:
            headline_votes = vote_matrices
            write_csv(out_dir / "press_python_receta.csv", report)
    model_id = str(np.asarray(bundle.get("model_id", "unknown")))
    dimension = int(np.asarray(bundle.get("dimension", rows_matrices(bundle)["python"].shape[1])))
    payload = {
        "model_id": model_id,
        "dimension": dimension,
        "pairs": {
            key: {k: v for k, v in report.items() if k != "families"}
            | {
                "families": {
                    alma: {
                        "n": family["n"],
                        "census": family["census"],
                        "vote_count_extrema": family["vote_count_extrema"],
                    }
                    for alma, family in report["families"].items()
                }
            }
            for key, report in pairs.items()
        },
    }
    # Re-add families compactly already done; keep row detail out of press.json? Ticket wants census + extrema.
    # Include published at pair level — already in report.
    assert_no_mean_fields(payload)
    json_path = out_dir / "press.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if headline_votes is not None:
        np.savez_compressed(
            out_dir / "press_votes.npz",
            python=headline_votes["python"].astype(np.uint8),
            receta=headline_votes["receta"].astype(np.uint8),
        )
    return payload


def _synthetic_rows(path: Path) -> Path:
    """Helper de tests: matrices 3D con ejes disjuntos canónicos."""
    python = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32)
    receta = np.array([[10.0, 0.0, 0.0], [11.0, 1.0, 1.0]], dtype=np.float32)
    legal = np.array([[0.0, 10.0, 0.0], [1.0, 11.0, 1.0]], dtype=np.float32)
    np.savez_compressed(
        path,
        python=python,
        legal=legal,
        receta=receta,
        ids_python=np.asarray(["p0", "p1"], dtype=object),
        ids_legal=np.asarray(["l0", "l1"], dtype=object),
        ids_receta=np.asarray(["r0", "r1"], dtype=object),
        texts_python=np.asarray(["py0", "py1"], dtype=object),
        texts_legal=np.asarray(["lg0", "lg1"], dtype=object),
        texts_receta=np.asarray(["rc0", "rc1"], dtype=object),
        model_id=np.asarray("fake"),
        dimension=np.asarray(3),
    )
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Censo dimensional fila por fila.")
    parser.add_argument("--rows", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT.parent)
    parser.add_argument("--benchmark-all", action="store_true")
    parser.add_argument("--models", default="fake:128,fake:256")
    parser.add_argument(
        "--live", action="store_true", help="Carga embedders reales en --benchmark-all"
    )
    args = parser.parse_args(argv)
    if args.benchmark_all:
        from ddi_fw.benchmark import run_benchmark

        report = run_benchmark(
            args.models.split(","),
            out_path=args.out / "benchmark_models.json",
            live=args.live,
        )
        print(json.dumps(report, indent=2))
        return 0
    try:
        payload = press(args.rows, args.out)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                key: {"published": pair["published"], "disjoint_count": pair["disjoint_count"]}
                for key, pair in payload["pairs"].items()
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

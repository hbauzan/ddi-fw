#!/usr/bin/env python3
"""N1, N2 y N4. Un solo BGE a la vez. N3 no se corre."""

from __future__ import annotations

import gc
import json
from pathlib import Path

import numpy as np

from ddi_fw.embedder import load_rows, rows_matrices
from ddi_fw.hoja import candados_canonicos

ROOT = Path(__file__).resolve().parents[1]
ROWS = ROOT / "ddi_fw" / "out" / "rows.npz"
REPORT = ROOT / "reports" / "numerical_robustness_report.json"
PROBE = "Explicá el funcionamiento de list.append en Python."
SHORT = "Hola mundo."
LONG = " ".join(f"token{index}" for index in range(200))
MODEL_ID = "BAAI/bge-m3"


def fmt(value: float) -> str:
    return f"{float(value):.17g}"


def embed(model: object, texts: list[str]) -> np.ndarray:
    vectors = np.asarray(
        model.encode(texts, convert_to_numpy=True, normalize_embeddings=False),
        dtype=np.float32,
    )
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    return vectors


def load_model(device: str) -> object:
    import torch
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        MODEL_ID,
        device=device,
        model_kwargs={"torch_dtype": torch.float32},
    )


def release(model: object) -> None:
    import torch

    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def n1_and_keep_probe(model: object) -> tuple[dict[str, object], np.ndarray]:
    isolated = embed(model, [PROBE])[0]
    batched = embed(model, [PROBE, SHORT, LONG])[0]
    delta = np.abs(isolated - batched)
    eps = float(np.finfo(np.float32).eps)
    max_abs = float(delta.max())
    mae = float(delta.mean())
    bitwise = bool(isolated.tobytes() == batched.tobytes())
    status = "PASS" if bitwise and max_abs <= eps else "FAIL"
    return {
        "max_abs": fmt(max_abs),
        "mae": fmt(mae),
        "bitwise_equal": bitwise,
        "eps": fmt(eps),
        "status": status,
    }, isolated


def n2(mps_vector: np.ndarray, cpu_vector: np.ndarray) -> dict[str, object]:
    delta = np.abs(mps_vector - cpu_vector)
    delta_max = float(delta.max())
    l2 = float(np.linalg.norm(mps_vector - cpu_vector))
    return {"delta_max": fmt(delta_max), "l2": fmt(l2), "status": "PASS"}


def n4(delta_max: float | None) -> dict[str, object]:
    eps = float(np.finfo(np.float32).eps)
    if delta_max is None:
        return {"status": "SKIP", "reason": "N2 sin delta_max"}
    if not ROWS.is_file():
        return {"status": "SKIP", "reason": "no está ddi_fw/out/rows.npz"}
    matrices = rows_matrices(load_rows(ROWS))
    gaps = []
    for lock in candados_canonicos(matrices).values():
        positive = lock.hoja.gap[lock.hoja.disjoint]
        if positive.size:
            gaps.append(positive)
    if not gaps:
        return {"status": "SKIP", "reason": "ningún eje con gap > 0"}
    min_gap = float(np.concatenate(gaps).min())
    floor = max(delta_max, eps)
    factor = min_gap / floor
    status = "IMMUNE" if factor > 100.0 else "FAIL"
    return {
        "status": status,
        "min_gap": fmt(min_gap),
        "floor": fmt(floor),
        "factor": fmt(factor),
    }


def _print_table(rows: list[tuple[str, str, str, str]]) -> None:
    headers = ("métrica", "umbral", "medido", "estado")
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row, strict=True)]
    line = "  ".join(header.ljust(width) for header, width in zip(headers, widths, strict=True))
    print(line)
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(width) for cell, width in zip(row, widths, strict=True)))


def main() -> int:
    import torch

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = load_model(device)
    weight = next(model.parameters())
    if weight.dtype != torch.float32:
        release(model)
        raise SystemExit(f"abortada: pesos {weight.dtype}")
    n1, mps_vector = n1_and_keep_probe(model)
    n1["device"] = str(weight.device)
    release(model)

    cpu_model = load_model("cpu")
    cpu_weight = next(cpu_model.parameters())
    if cpu_weight.dtype != torch.float32:
        release(cpu_model)
        raise SystemExit(f"abortada: pesos cpu {cpu_weight.dtype}")
    cpu_vector = embed(cpu_model, [PROBE])[0]
    release(cpu_model)
    n2_report = n2(mps_vector, cpu_vector)
    delta_max = float(n2_report["delta_max"])
    n4_report = n4(delta_max)

    report = {
        "model_id": MODEL_ID,
        "n1_batch_padding": n1,
        "n2_mps_cpu": n2_report,
        "n3_concurrency": {
            "status": "SKIP",
            "reason": "excluida: no se corre carga térmica ni hilos",
        },
        "n4_margin": n4_report,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    eps = n1["eps"]
    _print_table(
        [
            ("N1 max_abs", eps, str(n1["max_abs"]), str(n1["status"])),
            ("N1 bitwise", "true", str(n1["bitwise_equal"]).lower(), str(n1["status"])),
            ("N2 delta_max", "piso", str(n2_report["delta_max"]), str(n2_report["status"])),
            ("N2 l2", "piso", str(n2_report["l2"]), str(n2_report["status"])),
            ("N3 concurrencia", "excluida", "no corrida", "SKIP"),
            (
                "N4 factor",
                "100",
                str(n4_report.get("factor", n4_report.get("reason", ""))),
                str(n4_report["status"]),
            ),
        ]
    )
    print(REPORT)
    return 0 if n1["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

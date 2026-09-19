"""Comparativa multi-embedder. mean_gap es diagnóstico, no criterio de candado."""

from __future__ import annotations

import json
import resource
import time
from pathlib import Path
from typing import Any

from ddi_fw.almas import load_almas
from ddi_fw.embedder import BaseEmbedder, FakeEmbedder, embed_mazos, get_embedder
from ddi_fw.hoja import candados_canonicos


def _rss_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux: kB. macOS: bytes.
    if usage > 10**7:
        return usage / (1024 * 1024)
    return usage / 1024


def measure_embedder(embedder: BaseEmbedder, mazos: dict) -> dict[str, Any]:
    started = time.perf_counter()
    matrices, _ids = embed_mazos(mazos, embedder)
    elapsed = time.perf_counter() - started
    n_clauses = sum(mazo.n for mazo in mazos.values()) or 1
    locks = candados_canonicos(matrices)
    pairs: list[dict[str, Any]] = []
    for pair_name, candado in locks.items():
        gaps = candado.hoja.gap[candado.hoja.disjoint]
        pairs.append(
            {
                "pair": pair_name,
                "disjoint_axes_count": candado.disjoint_count,
                "mean_gap": float(gaps.mean()) if gaps.size else 0.0,
                "max_gap": float(gaps.max()) if gaps.size else 0.0,
                "published": candado.published,
            }
        )
    return {
        "model_id": embedder.model_id,
        "dimension": embedder.dimension,
        "latency_us_per_clause": (elapsed / n_clauses) * 1_000_000,
        "memory_mb": _rss_mb(),
        "pairs": pairs,
    }


def resolve_embedder(name: str) -> BaseEmbedder:
    stripped = name.strip()
    if stripped.startswith("fake"):
        dim = 8
        if ":" in stripped:
            dim = int(stripped.split(":", 1)[1])
        return FakeEmbedder(dimension=dim, model_id=f"fake-{dim}")
    return get_embedder(stripped)


def report_from_rows(
    rows_path: Path, extra_errors: list[dict[str, str]] | None = None
) -> dict[str, Any]:
    """Diagnóstico geométrico desde un rows.npz ya calibrado. No re-embebe."""
    from ddi_fw.embedder import load_rows, rows_matrices

    bundle = load_rows(rows_path)
    locks = candados_canonicos(rows_matrices(bundle))
    pairs: list[dict[str, Any]] = []
    for pair_name, candado in locks.items():
        gaps = candado.hoja.gap[candado.hoja.disjoint]
        pairs.append(
            {
                "pair": pair_name,
                "disjoint_axes_count": candado.disjoint_count,
                "mean_gap": float(gaps.mean()) if gaps.size else 0.0,
                "max_gap": float(gaps.max()) if gaps.size else 0.0,
                "published": candado.published,
                "disjoint_axes": candado.ejes_disjuntos,
            }
        )
    return {
        "models": [
            {
                "model_id": str(bundle.get("model_id", "unknown")),
                "dimension": int(bundle.get("dimension", 0)),
                "source": "rows.npz",
                "pairs": pairs,
            }
        ],
        "errors": list(extra_errors or []),
    }


def run_benchmark(
    model_names: list[str],
    *,
    out_path: Path | None = None,
    live: bool = False,
) -> dict[str, Any]:
    mazos = load_almas()
    models: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for name in model_names:
        label = name.strip()
        if not label:
            continue
        try:
            embedder = resolve_embedder(label)
            if not live and not isinstance(embedder, FakeEmbedder):
                errors.append({"model": label, "error": "skipped_not_live"})
                continue
            models.append(measure_embedder(embedder, mazos))
        except Exception as exc:  # noqa: BLE001 — el live es best-effort
            errors.append({"model": label, "error": f"{exc.__class__.__name__}: {exc}"})
    report = {"models": models, "errors": errors}
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report

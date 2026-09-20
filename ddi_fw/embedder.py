"""Seam de embedder. Tests default no cargan SentenceTransformer."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt

from ddi_fw.adapters.base import (
    BaseEmbedder,
    FloatArray,
    _SentenceTransformerEmbedder,
    l2_normalize,
    matryoshka_cut,
)
from ddi_fw.adapters.bge import BGE_M3_ID, BGEM3Embedder
from ddi_fw.adapters.qwen2 import (
    QWEN2_ID,
    Qwen2Embedder,
    apply_qwen2_cache_shim,
    apply_qwen2_rope_theta_shim,
    apply_qwen2_transformers517_shim,
)
from ddi_fw.almas import ALMA_NAMES, DATA_DIR, Mazo, drop_clauses, load_almas, write_mazo
from ddi_fw.hoja import candados_canonicos, podar_hasta_publicar

GEMMA_ID = "google/embeddinggemma-300m"
NOMIC_ID = "nomic-ai/nomic-embed-text-v1.5"

DEFAULT_OUT = Path(__file__).resolve().parent / "out" / "rows.npz"

__all__ = [
    "ALMA_NAMES",
    "BGE_M3_ID",
    "BGEM3Embedder",
    "BaseEmbedder",
    "DEFAULT_OUT",
    "FakeEmbedder",
    "FloatArray",
    "GEMMA_ID",
    "GemmaMRLEmbedder",
    "NOMIC_ID",
    "NomicEmbedder",
    "QWEN2_ID",
    "Qwen2Embedder",
    "apply_qwen2_cache_shim",
    "apply_qwen2_rope_theta_shim",
    "apply_qwen2_transformers517_shim",
    "calibrate",
    "embed_mazos",
    "get_embedder",
    "l2_normalize",
    "load_rows",
    "matryoshka_cut",
    "measure_and_save",
    "resolve_out_dir",
    "rows_matrices",
    "save_rows",
]


@dataclass
class FakeEmbedder:
    """Vectores deterministas. `table` pisa el hash para cláusulas de test."""

    dimension: int = 8
    model_id: str = "fake"
    table: dict[str, npt.NDArray[np.floating]] | None = None

    def embed_text(self, text: str) -> FloatArray:
        if self.table is not None and text in self.table:
            vector = np.asarray(self.table[text], dtype=np.float32).reshape(-1)
            if vector.shape[0] != self.dimension:
                raise ValueError("vector de table con dimensión distinta")
            return vector
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        needed = self.dimension * 4
        raw = (digest * ((needed // len(digest)) + 1))[:needed]
        integers = np.frombuffer(raw, dtype=np.uint32)[: self.dimension]
        return (integers.astype(np.float32) / np.float32(2**31) - np.float32(1.0)).astype(
            np.float32
        )

    def embed_batch(self, texts: list[str]) -> FloatArray:
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)
        return np.stack([self.embed_text(text) for text in texts], axis=0)


class GemmaMRLEmbedder(_SentenceTransformerEmbedder):
    def __init__(self, dim: int = 256) -> None:
        super().__init__(GEMMA_ID, dim, output_dim=dim)


class NomicEmbedder(_SentenceTransformerEmbedder):
    """MRL 64–768D. El custom code de Nomic rompe con transformers 5.x (ver lessons-learned)."""

    def __init__(self, dim: int = 256) -> None:
        super().__init__(
            NOMIC_ID,
            dim,
            output_dim=dim,
            trust_remote_code=True,
            prefix="search_document: ",
        )


def get_embedder(name: str, dim: int | None = None) -> BaseEmbedder:
    key = name.strip().casefold()
    if key in {"fake", "stub"}:
        return FakeEmbedder(dimension=dim or 8)
    if key in {"bge-m3", "bge_m3", BGE_M3_ID.casefold()}:
        return BGEM3Embedder.instance()
    if key in {"gemma", "gemma-mrl", "embeddinggemma", GEMMA_ID.casefold()}:
        return GemmaMRLEmbedder(dim=dim or 256)
    if key in {"nomic", "nomic-embed", NOMIC_ID.casefold()}:
        return NomicEmbedder(dim=dim or 256)
    if key in {"qwen2", "qwen", QWEN2_ID.casefold()}:
        return Qwen2Embedder.instance()
    raise ValueError(f"embedder desconocido: {name}")


def embed_mazos(
    mazos: dict[str, Mazo], embedder: BaseEmbedder
) -> tuple[dict[str, FloatArray], dict[str, list[str]]]:
    matrices: dict[str, FloatArray] = {}
    ids: dict[str, list[str]] = {}
    for alma, mazo in mazos.items():
        matrices[alma] = embedder.embed_batch(mazo.texts())
        ids[alma] = mazo.ids()
    return matrices, ids


def save_rows(
    path: Path,
    matrices: dict[str, npt.NDArray[np.floating]],
    ids: dict[str, list[str]],
    texts: dict[str, list[str]],
    embedder: BaseEmbedder,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "model_id": np.asarray(embedder.model_id),
        "dimension": np.asarray(embedder.dimension),
    }
    for alma, rows in matrices.items():
        payload[alma] = np.asarray(rows, dtype=np.float32)
        payload[f"ids_{alma}"] = np.asarray(ids[alma], dtype=object)
        payload[f"texts_{alma}"] = np.asarray(texts[alma], dtype=object)
    np.savez_compressed(path, **payload)
    return path


def load_rows(path: Path) -> dict[str, object]:
    with np.load(path, allow_pickle=True) as handle:
        return {key: handle[key] for key in handle.files}


def rows_matrices(bundle: dict[str, object]) -> dict[str, FloatArray]:
    return {
        alma: np.asarray(bundle[alma], dtype=np.float32) for alma in ALMA_NAMES if alma in bundle
    }


def resolve_out_dir(out: Path) -> Path:
    """`--out` may be a directory or an `.npz` path. Measure always writes `rows.npz` inside the dir."""
    if out.suffix.lower() == ".npz":
        return out.parent
    return out


def measure_and_save(
    embedder: BaseEmbedder,
    *,
    data_dir: Path,
    out_dir: Path,
) -> dict[str, object]:
    """Full-deck persist. Never prunes. Never rewrites fixtures. Never overwrites BGE `rows.npz`."""
    rows_path = out_dir / "rows.npz"
    if rows_path.resolve() == DEFAULT_OUT.resolve():
        raise ValueError(
            "measure_and_save refuses to overwrite BGE rows.npz; pass out_dir other than ddi_fw/out"
        )
    mazos = load_almas(data_dir)
    matrices, ids = embed_mazos(mazos, embedder)
    texts = {alma: mazo.texts() for alma, mazo in mazos.items()}
    path = save_rows(rows_path, matrices, ids, texts, embedder)
    locks = candados_canonicos(matrices)
    audit: dict[str, object] = {
        "model_id": embedder.model_id,
        "dimension": embedder.dimension,
        "n": {alma: int(rows.shape[0]) for alma, rows in matrices.items()},
        "published": {key: lock.published for key, lock in locks.items()},
        "disjoint_count": {key: lock.disjoint_count for key, lock in locks.items()},
        "disjoint_axes": {key: lock.ejes_disjuntos for key, lock in locks.items()},
        "dropped": [],
        "rows_path": str(path),
    }
    audit_path = out_dir / "measure_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return audit


def calibrate(
    embedder: BaseEmbedder | None = None,
    *,
    data_dir: Path = DATA_DIR,
    out_path: Path = DEFAULT_OUT,
    min_n: int = 8,
    rewrite_fixtures: bool = False,
) -> dict[str, object]:
    """Embebe mazos, poda si hace falta y persiste rows.npz."""
    worker = embedder or BGEM3Embedder.instance()
    mazos = load_almas(data_dir)
    original_texts = {
        alma: {clause.id: clause.text for clause in mazo.clauses} for alma, mazo in mazos.items()
    }
    matrices, ids = embed_mazos(mazos, worker)
    pruned, pruned_ids, dropped = podar_hasta_publicar(matrices, ids, min_n=min_n)
    if dropped and rewrite_fixtures:
        drop_set = set(dropped)
        for alma, mazo in mazos.items():
            mazos[alma] = drop_clauses(mazo, drop_set)
            write_mazo(mazos[alma], data_dir)
    texts = {
        alma: [original_texts[alma][clause_id] for clause_id in alma_ids]
        for alma, alma_ids in pruned_ids.items()
    }
    path = save_rows(out_path, pruned, pruned_ids, texts, worker)
    locks = candados_canonicos(pruned)
    audit = {
        "rows_path": str(path),
        "model_id": worker.model_id,
        "dimension": worker.dimension,
        "dropped": dropped,
        "published": {key: lock.published for key, lock in locks.items()},
        "disjoint_count": {key: lock.disjoint_count for key, lock in locks.items()},
        "n": {alma: int(rows.shape[0]) for alma, rows in pruned.items()},
    }
    audit_path = out_path.with_name("calibrate_audit.json")
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if not all(locks[key].published for key in locks):
        raise RuntimeError(f"candados inéditos tras poda min_n={min_n}: {audit['published']}")
    return audit


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Calibra rows.npz con el embedder pinneado.")
    parser.add_argument("--embedder", default="bge-m3")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--rewrite-fixtures", action="store_true")
    parser.add_argument(
        "--no-prune",
        action="store_true",
        help="Mide y persiste el mazo completo. No llama calibrate()/podar_hasta_publicar.",
    )
    args = parser.parse_args(argv)
    if args.no_prune and args.rewrite_fixtures:
        parser.error("--no-prune cannot be combined with --rewrite-fixtures")
    if args.no_prune:
        out = args.out if args.out is not None else DEFAULT_OUT.parent / "qwen2"
        try:
            audit = measure_and_save(
                get_embedder(args.embedder),
                data_dir=args.data_dir,
                out_dir=resolve_out_dir(out),
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    else:
        audit = calibrate(
            get_embedder(args.embedder),
            data_dir=args.data_dir,
            out_path=args.out if args.out is not None else DEFAULT_OUT,
            rewrite_fixtures=args.rewrite_fixtures,
        )
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

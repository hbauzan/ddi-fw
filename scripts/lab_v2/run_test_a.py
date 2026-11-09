"""Runner del Test A. `--embedder bge` mide; `--embedder fake` solo hace humo."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ddi_fw.embedder import get_embedder
from ddi_fw.hardware import get_hardware_profile
from ddi_fw.lab_v2.chunker import TextChunk, extract_chunks
from ddi_fw.lab_v2.corpus_builder import SEEN_DOMAINS, BenchmarkSample, build_test_a_dataset
from ddi_fw.lab_v2.metrics import (
    determine_test_a_verdict,
    render_test_a_markdown,
    summarize_detection,
)
from ddi_fw.lab_v2.models import (
    M1_DdiBoxesBaseline,
    M2_CosineMargin,
    M3_WhitenedSpectralSubspace,
    M4_HybridAstSpectral,
)

_DEFAULT_JSON = Path("reports/lab_v2_test_a_results.json")
_DEFAULT_MD = Path("reports/test_a_duelo_subespacio_vs_coseno.md")
_CATEGORIES = (
    "pos_stdlib_python",
    "pos_business_python",
    "neg_seen_domain",
    "neg_unseen_domain_ood",
    "neg_other_language",
    "neg_piggybacking",
)


@dataclass(frozen=True)
class PreparedSample:
    sample: BenchmarkSample
    chunks: list[TextChunk]
    vectors: np.ndarray


def run_test_a(
    *,
    embedder_name: str,
    json_path: Path,
    md_path: Path,
    seed: int = 42,
    batch_size: int = 32,
) -> dict[str, object]:
    embedder = _load_embedder(embedder_name)
    dataset = build_test_a_dataset(seed=seed)
    prepared = _prepare(dataset, embedder, batch_size=batch_size)
    train = [item for item in prepared if item.sample.split == "train"]
    calibration = [item for item in prepared if item.sample.split == "cal"]
    test = [item for item in prepared if item.sample.split == "test"]
    if not train or not calibration or not test:
        raise ValueError("un split del Test A quedó vacío")
    python_rows, negative_by_domain = _training_matrices(train)
    negative_all = np.vstack([negative_by_domain[name] for name in SEEN_DOMAINS])
    cal_groups = [(item.chunks, item.vectors) for item in calibration]

    boxes = M1_DdiBoxesBaseline()
    boxes.fit({"python": python_rows, **negative_by_domain})
    cosine = M2_CosineMargin()
    cosine.fit(python_rows, negative_by_domain, cal_groups)
    subspace = M3_WhitenedSpectralSubspace()
    subspace.fit(python_rows, negative_all, cal_groups)
    hybrid = M4_HybridAstSpectral()
    hybrid.fit(python_rows, negative_all, cal_groups)

    model_stats = {
        "M1_DDI_v040": _evaluate(boxes, test),
        "M2_Cosine": _evaluate(cosine, test),
        "M3_EEB_Pure": _evaluate(subspace, test),
        "M4_Hybrid_AST_EEB": _evaluate(hybrid, test),
    }
    verdict = determine_test_a_verdict(
        model_stats["M1_DDI_v040"],
        model_stats["M2_Cosine"],
        model_stats["M3_EEB_Pure"],
        model_stats["M4_Hybrid_AST_EEB"],
    )
    payload: dict[str, object] = {
        "task_id": "TASK-001",
        "embedder": embedder.model_id,
        "seed": int(seed),
        "counts": {
            "train": len(train),
            "cal": len(calibration),
            "test": len(test),
            "chunks": int(sum(len(item.chunks) for item in prepared)),
        },
        "hardware": get_hardware_profile(),
        "models": model_stats,
        "verdict": verdict,
    }
    _write_outputs(payload, json_path, md_path)
    return payload


def main(argv: list[str] | None = None) -> dict[str, object]:
    parser = argparse.ArgumentParser(description="Duelo geométrico del Test A")
    parser.add_argument("--embedder", default="bge", choices=("bge", "fake"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json-out", type=Path, default=_DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=_DEFAULT_MD)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args(argv)
    if args.batch_size < 1:
        raise ValueError("batch-size debe ser >= 1")
    return run_test_a(
        embedder_name=args.embedder,
        json_path=args.json_out,
        md_path=args.md_out,
        seed=args.seed,
        batch_size=args.batch_size,
    )


def _load_embedder(name: str) -> object:
    key = name.strip().casefold()
    if key == "bge":
        return get_embedder("BAAI/bge-m3")
    if key == "fake":
        return get_embedder("fake")
    return get_embedder(name)


def _prepare(dataset: list[BenchmarkSample], embedder: object, *, batch_size: int) -> list[PreparedSample]:
    texts: list[str] = []
    layouts: list[tuple[BenchmarkSample, list[TextChunk], int]] = []
    for sample in dataset:
        chunks = extract_chunks(sample.text)
        if not chunks:
            raise ValueError(f"sin chunks: {sample.sample_id}")
        layouts.append((sample, chunks, len(texts)))
        texts.extend(chunk.text for chunk in chunks)
    matrix = _embed_texts(embedder, texts, batch_size=batch_size)
    prepared: list[PreparedSample] = []
    for sample, chunks, start in layouts:
        rows = np.asarray(matrix[start : start + len(chunks)], dtype=np.float64)
        if rows.shape != (len(chunks), embedder.dimension):
            raise ValueError(f"shape de embeddings inválida para {sample.sample_id}: {rows.shape}")
        prepared.append(PreparedSample(sample=sample, chunks=chunks, vectors=rows))
    return prepared


def _embed_texts(embedder: object, texts: list[str], *, batch_size: int) -> np.ndarray:
    if not texts:
        return np.zeros((0, embedder.dimension), dtype=np.float32)
    print(f"embeddings {len(texts)} chunks model={embedder.model_id}", flush=True)
    parts: list[np.ndarray] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        parts.append(np.asarray(embedder.embed_batch(batch), dtype=np.float32))
    return np.vstack(parts)


def _training_matrices(
    train: list[PreparedSample],
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    positive = [
        item.vectors
        for item in train
        if item.sample.is_legitimate_python and item.vectors.size
    ]
    if not positive:
        raise ValueError("no hay chunks positivos de train")
    python_rows = np.vstack(positive)
    negative_by_domain: dict[str, np.ndarray] = {}
    for domain in SEEN_DOMAINS:
        rows = [
            item.vectors
            for item in train
            if item.sample.category == "neg_seen_domain"
            and item.sample.subtag == domain
            and item.vectors.size
        ]
        if len(rows) < 1:
            raise ValueError(f"el dominio visto {domain} no tiene chunks de train")
        negative_by_domain[domain] = np.vstack(rows)
    return python_rows, negative_by_domain


def _evaluate(model: object, test: list[PreparedSample]) -> dict[str, float]:
    legit_scores: list[float] = []
    attack_scores: list[float] = []
    latency_ms: list[float] = []
    counts = {category: [0, 0] for category in _CATEGORIES}
    for item in test:
        category = item.sample.category
        if category not in counts:
            raise ValueError(f"categoría inesperada: {category}")
        started = time.perf_counter()
        score = float(model.score_sample(item.chunks, item.vectors))
        latency_ms.append((time.perf_counter() - started) * 1000.0)
        blocked = bool(model.predict_breach(item.chunks, item.vectors))
        counts[category][0] += 1
        counts[category][1] += int(blocked)
        if item.sample.is_legitimate_python:
            legit_scores.append(score)
        else:
            attack_scores.append(score)
    packed = {key: (values[0], values[1]) for key, values in counts.items()}
    return summarize_detection(
        legit_scores=np.asarray(legit_scores, dtype=np.float64),
        attack_scores=np.asarray(attack_scores, dtype=np.float64),
        counts=packed,
        latency_ms=np.asarray(latency_ms, dtype=np.float64),
    )


def _write_outputs(payload: dict[str, object], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(_jsonable(payload), indent=2, ensure_ascii=False, allow_nan=False)
    json_path.write_text(encoded + "\n", encoding="utf-8")
    md_path.write_text(render_test_a_markdown(payload), encoding="utf-8")


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.integer) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


if __name__ == "__main__":
    main()

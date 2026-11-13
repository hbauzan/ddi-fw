"""Auditoría empírica de la graduación v0.5.0. `--embedder bge` mide; `fake` es humo."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path

import numpy as np

from ddi_fw.hardware import get_hardware_profile
from ddi_fw.lab_v2.chunker import extract_chunks
from ddi_fw.lab_v2.corpus_builder import SEEN_DOMAINS, build_test_a_dataset
from ddi_fw.lab_v2.models import M3_WhitenedSpectralSubspace, M4_HybridAstSpectral
from ddi_fw.v2_calibration import (
    FOREIGN_TRAIN_ANCHORS,
    assert_disjoint_from_test_a,
    load_v2_calibration,
    save_v2_calibration,
)
from ddi_fw.v2_firewall import SpectralAstFirewall
from scripts.lab_v2.run_test_a import (
    _embed_texts,
    _evaluate,
    _load_embedder,
    _prepare,
    _training_matrices,
)

_DEFAULT_JSON = Path("reports/v050_graduation_audit.json")
_DEFAULT_MD = Path("reports/v050_graduation_audit.md")
_VARIANT_ORDER = ("prose_only_negatives", "multilang_hardened_negatives")
_MODEL_ORDER = ("M3_WhitenedSpectralSubspace", "M4_HybridAstSpectral")
_TABLE_FIELDS = ("roc_auc", "pr_auc", "far_other_language", "far_total", "frr_total")
_LATEX = r"""## Fórmulas

Dirección de Fisher en el espacio original:

$$\vec{w}^{\top} \vec{x}$$

Umbral conformal sobre los 72 grupos positivos de calibración:

$$\hat{q}_{1-\alpha} = s_{\mathrm{cal}}\left(\left\lceil (n_{\mathrm{cal}}+1)(1-\alpha)\right\rceil\right)$$

Ajuste híbrido por chunk:

$$s_{\mathrm{adj}}(c) = s_{\mathrm{EEB}}(c) + \begin{cases} -1.5 & \text{si el AST de Python es válido} \\ +6.0 & \text{si } c \in \{\text{fenced\_code},\text{foreign\_code}\} \\ 0 & \text{en otro caso} \end{cases}$$

Fracción de falsos aceptados en código ajeno:

$$\mathrm{FAR}_{\mathrm{lang}} = \frac{n_{\mathrm{miss}}}{n_{\mathrm{lang}}}$$
"""


def hardened_m4_lowers_other_language_far(
    prose_far: float,
    hardened_far: float,
    *,
    m3_prose_far: float | None = None,
    m3_hardened_far: float | None = None,
) -> bool:
    if float(hardened_far) < float(prose_far):
        return True
    if (
        float(prose_far) == 0.0
        and float(hardened_far) == 0.0
        and m3_prose_far is not None
        and m3_hardened_far is not None
    ):
        return float(m3_hardened_far) < float(m3_prose_far)
    return False


def cache_reused_every_repeated_chunk(
    first_misses: int, second_hits: int, second_misses: int
) -> bool:
    return int(first_misses) > 0 and int(second_misses) == 0 and int(second_hits) == int(first_misses)


def graduation_ready(*checks: bool) -> bool:
    return bool(checks) and all(bool(item) for item in checks)


def tensors_match(reference: M4_HybridAstSpectral, restored: M4_HybridAstSpectral) -> bool:
    if reference.q_hat is None or restored.q_hat is None:
        return False
    for name in ("mu_pos", "w_hat", "u_k", "gamma", "medians", "iqrs"):
        left = getattr(reference, name)
        right = getattr(restored, name)
        if left is None or right is None:
            return False
        if not np.array_equal(np.asarray(left), np.asarray(right)):
            return False
    if bool(reference.w_hat_foreign is None) != bool(restored.w_hat_foreign is None):
        return False
    if reference.w_hat_foreign is not None:
        for name in ("w_hat_foreign", "foreign_median", "foreign_iqr", "shrinkage_foreign"):
            left = getattr(reference, name)
            right = getattr(restored, name)
            if left is None or right is None:
                return False
            if not np.array_equal(np.asarray(left), np.asarray(right)):
                return False
    return float(reference.q_hat) == float(restored.q_hat)


def run_v050_graduation_check(
    *,
    embedder_name: str,
    json_path: Path,
    md_path: Path,
    seed: int = 42,
    batch_size: int = 32,
) -> dict[str, object]:
    if batch_size < 1:
        raise ValueError("batch_size debe ser >= 1")
    assert_disjoint_from_test_a()
    embedder = _load_embedder(embedder_name)
    dataset = build_test_a_dataset(seed=seed)
    _assert_split_ids(dataset)
    prepared = _prepare(dataset, embedder, batch_size=batch_size)
    train = [item for item in prepared if item.sample.split == "train"]
    calibration = [item for item in prepared if item.sample.split == "cal"]
    test = [item for item in prepared if item.sample.split == "test"]
    if len(calibration) != 72:
        raise ValueError(f"cal={len(calibration)} != 72")
    if len(test) != 488:
        raise ValueError(f"test={len(test)} != 488")
    if len(FOREIGN_TRAIN_ANCHORS) != 36:
        raise ValueError(f"anclas={len(FOREIGN_TRAIN_ANCHORS)} != 36")
    positive, negative_by_domain = _training_matrices(train)
    prose_negative = np.vstack([negative_by_domain[name] for name in SEEN_DOMAINS])
    anchor_rows = _anchor_matrix(embedder, batch_size=batch_size, dimension=int(embedder.dimension))
    if anchor_rows.shape[1] != prose_negative.shape[1]:
        raise ValueError("las anclas no comparten dimension con el negativo de prosa")
    groups = [(item.chunks, item.vectors) for item in calibration]
    fitted = {
        "prose_only_negatives": _fit_pair(
            positive, prose_negative, groups, foreign_negative=None
        ),
        "multilang_hardened_negatives": _fit_pair(
            positive, prose_negative, groups, foreign_negative=anchor_rows
        ),
    }
    variants = {
        name: {model_name: _evaluate(model, test) for model_name, model in pair.items()}
        for name, pair in fitted.items()
    }
    hardened_m4 = fitted["multilang_hardened_negatives"]["M4_HybridAstSpectral"]
    if not isinstance(hardened_m4, M4_HybridAstSpectral):
        raise TypeError("el modelo endurecido no es M4")
    roundtrip_ok = _roundtrip_ok(hardened_m4, embedder)
    cache = _cache_probe(hardened_m4, embedder)
    far_improved = hardened_m4_lowers_other_language_far(
        float(variants["prose_only_negatives"]["M4_HybridAstSpectral"]["far_other_language"]),
        float(variants["multilang_hardened_negatives"]["M4_HybridAstSpectral"]["far_other_language"]),
        m3_prose_far=float(
            variants["prose_only_negatives"]["M3_WhitenedSpectralSubspace"]["far_other_language"]
        ),
        m3_hardened_far=float(
            variants["multilang_hardened_negatives"]["M3_WhitenedSpectralSubspace"][
                "far_other_language"
            ]
        ),
    )
    cache_ok = cache_reused_every_repeated_chunk(
        int(cache["first_misses"]),
        int(cache["second_hits"]),
        int(cache["second_misses"]),
    )
    ready = graduation_ready(far_improved, roundtrip_ok, cache_ok)
    payload: dict[str, object] = {
        "task_id": "TASK-006",
        "embedder": embedder.model_id,
        "seed": int(seed),
        "test_sample_count": len(test),
        "foreign_train_anchor_count": len(FOREIGN_TRAIN_ANCHORS),
        "counts": {"train": len(train), "cal": len(calibration), "test": len(test)},
        "variants": variants,
        "checks": {
            "m4_other_language_far_improved": far_improved,
            "npz_roundtrip_bitwise": roundtrip_ok,
            "cache_reused": cache_ok,
            "cache": cache,
        },
        "verdict": {
            "m4_other_language_far_improved": far_improved,
            "npz_roundtrip_bitwise": roundtrip_ok,
            "cache_reused": cache_ok,
            "graduation_ready": ready,
        },
        "hardware": get_hardware_profile(),
    }
    _write_outputs(payload, json_path, md_path)
    return payload


def main(argv: list[str] | None = None) -> dict[str, object]:
    parser = argparse.ArgumentParser(description="Auditoría de graduación v0.5.0")
    parser.add_argument("--embedder", default="bge", choices=("bge", "fake"))
    parser.add_argument("--json-out", type=Path, default=_DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=_DEFAULT_MD)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args(argv)
    payload = run_v050_graduation_check(
        embedder_name=args.embedder,
        json_path=args.json_out,
        md_path=args.md_out,
        seed=args.seed,
        batch_size=args.batch_size,
    )
    verdict = payload["verdict"]
    if isinstance(verdict, dict):
        print(f"graduation_ready={bool(verdict['graduation_ready'])}", flush=True)
    return payload


def _assert_split_ids(dataset: list[object]) -> None:
    grouped = {
        split: {sample.sample_id for sample in dataset if sample.split == split}
        for split in ("train", "cal", "test")
    }
    for left, right in (("train", "cal"), ("train", "test"), ("cal", "test")):
        if not grouped[left].isdisjoint(grouped[right]):
            raise ValueError(f"sample_id repetido entre {left} y {right}")
    if not grouped["train"] or not grouped["cal"] or not grouped["test"]:
        raise ValueError("un split del Test A quedó vacío")


def _anchor_matrix(embedder: object, *, batch_size: int, dimension: int) -> np.ndarray:
    texts: list[str] = []
    for language, name, source in FOREIGN_TRAIN_ANCHORS:
        chunks = extract_chunks(source)
        if not chunks:
            raise ValueError(f"ancla sin chunks: {language}:{name}")
        texts.extend(chunk.text for chunk in chunks)
    rows = np.asarray(_embed_texts(embedder, texts, batch_size=batch_size), dtype=np.float64)
    if rows.ndim != 2 or rows.shape[0] < len(FOREIGN_TRAIN_ANCHORS) or rows.shape[1] != dimension:
        raise ValueError(f"matriz de anclas inválida: {rows.shape}")
    return rows


def _fit_pair(
    positive: np.ndarray,
    negative: np.ndarray,
    groups: list[tuple[object, np.ndarray]],
    *,
    foreign_negative: np.ndarray | None = None,
) -> dict[str, M3_WhitenedSpectralSubspace]:
    subspace = M3_WhitenedSpectralSubspace()
    subspace.fit(positive, negative, groups, foreign_negative=foreign_negative)
    hybrid = M4_HybridAstSpectral()
    hybrid.fit(positive, negative, groups, foreign_negative=foreign_negative)
    return {
        "M3_WhitenedSpectralSubspace": subspace,
        "M4_HybridAstSpectral": hybrid,
    }


def _roundtrip_ok(model: M4_HybridAstSpectral, embedder: object) -> bool:
    chunks = extract_chunks("def v050_roundtrip():\n    return 1\n")
    if not chunks:
        return False
    rows = np.asarray(
        embedder.embed_batch([chunk.text for chunk in chunks]),
        dtype=np.float64,
    )
    if rows.ndim != 2 or rows.shape != (len(chunks), int(embedder.dimension)):
        return False
    with tempfile.TemporaryDirectory() as folder:
        path = save_v2_calibration(
            Path(folder) / "roundtrip.npz",
            model,
            model_id=str(embedder.model_id),
            alpha=0.05,
        )
        loaded, meta = load_v2_calibration(path)
    if not isinstance(loaded, M4_HybridAstSpectral):
        return False
    return (
        tensors_match(model, loaded)
        and loaded.score_sample(chunks, rows) == model.score_sample(chunks, rows)
        and meta["model_id"] == str(embedder.model_id)
    )


def _cache_probe(model: M4_HybridAstSpectral, embedder: object) -> dict[str, object]:
    firewall = SpectralAstFirewall(model, embedder, max_cache_entries=64)
    messages = [
        {"role": "system", "content": "def v050_cache_probe():\n    return 'muelle-norte'\n"},
        {
            "role": "user",
            "content": (
                "El muelle norte recibio pallets secos durante el turno de la manana sin novedades."
            ),
        },
    ]
    started = time.perf_counter()
    first = firewall.inspect_messages(messages)
    elapsed_first = time.perf_counter() - started
    started = time.perf_counter()
    second = firewall.inspect_messages(messages)
    elapsed_second = time.perf_counter() - started
    speedup = None if elapsed_second <= 0.0 else float(elapsed_first / elapsed_second)
    return {
        "first_misses": int(first.cache_misses),
        "second_hits": int(second.cache_hits),
        "second_misses": int(second.cache_misses),
        "elapsed_first_s": float(elapsed_first),
        "elapsed_second_s": float(elapsed_second),
        "wall_clock_speedup": speedup,
    }


def render_graduation_markdown(payload: dict[str, object]) -> str:
    variants = payload["variants"]
    verdict = payload["verdict"]
    checks = payload["checks"]
    if not isinstance(variants, dict) or not isinstance(verdict, dict) or not isinstance(checks, dict):
        raise ValueError("payload sin variants, checks o verdict")
    lines = [
        "# Graduación v0.5.0 — auditoría M3/M4",
        "",
        "Los números salen de `summarize_detection` y de predicados booleanos del runner.",
        "El JSON hermano guarda los float nativos; esta tabla usa `format(x, '.17g')`.",
        "",
        _LATEX.rstrip(),
        "",
        "## Comparación",
        "",
        "| variante | modelo | roc_auc | pr_auc | far_other_language | far_total | frr_total |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for variant in _VARIANT_ORDER:
        models = variants[variant]
        if not isinstance(models, dict):
            raise ValueError(f"{variant} no es un diccionario")
        for model_name in _MODEL_ORDER:
            stats = models[model_name]
            if not isinstance(stats, dict):
                raise ValueError(f"{model_name} no es un diccionario de métricas")
            cells = [variant, model_name, *(_fmt(stats[field]) for field in _TABLE_FIELDS)]
            lines.append("| " + " | ".join(cells) + " |")
    cache = checks["cache"]
    if not isinstance(cache, dict):
        raise ValueError("checks.cache no es un diccionario")
    lines.extend(
        [
            "",
            "## Veredicto",
            "",
            f"- m4_other_language_far_improved: {bool(verdict['m4_other_language_far_improved'])}",
            f"- npz_roundtrip_bitwise: {bool(verdict['npz_roundtrip_bitwise'])}",
            f"- cache_reused: {bool(verdict['cache_reused'])}",
            f"- graduation_ready: {bool(verdict['graduation_ready'])}",
            f"- cache_first_misses: {int(cache['first_misses'])}",
            f"- cache_second_hits: {int(cache['second_hits'])}",
            f"- cache_second_misses: {int(cache['second_misses'])}",
            f"- elapsed_first_s: {_fmt(cache['elapsed_first_s'])}",
            f"- elapsed_second_s: {_fmt(cache['elapsed_second_s'])}",
            f"- wall_clock_speedup: {_fmt(cache['wall_clock_speedup'])}",
            "",
        ]
    )
    hardware = payload.get("hardware")
    if isinstance(hardware, dict):
        lines.append("## Entorno")
        lines.append("")
        for key, value in hardware.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    return "\n".join(lines)


def _fmt(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        return format(float(value), ".17g")
    return str(value)


def _write_outputs(payload: dict[str, object], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(_jsonable(payload), indent=2, ensure_ascii=False, allow_nan=False)
    json_path.write_text(encoded + "\n", encoding="utf-8")
    md_path.write_text(render_graduation_markdown(payload), encoding="utf-8")


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

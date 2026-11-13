"""Calibración productiva de M4 y persistencia .npz sin pickle."""

from __future__ import annotations

import argparse
import ast
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

import numpy as np

from ddi_fw.embedder import get_embedder
from ddi_fw.lab_v2.chunker import TextChunk, extract_chunks
from ddi_fw.lab_v2.corpus_builder import BenchmarkSample, build_test_a_dataset, normalize_text
from ddi_fw.lab_v2.fixtures_code import FOREIGN_SNIPPETS
from ddi_fw.lab_v2.models import M4_HybridAstSpectral, conformal_threshold

_POSITIVE_TRAIN = frozenset({"pos_stdlib_python", "pos_business_python"})
_HOLDOUT_SPLITS = frozenset({"cal", "test"})
_TENSOR_KEYS = ("mu_pos", "w_hat", "u_k", "gamma", "medians", "iqrs")
_EMBED_BATCH = 32


def _anchor(language: str, name: str, source: str) -> tuple[str, str, str]:
    text = source.strip() + "\n"
    if not name.startswith("v050_anchor_"):
        raise ValueError(f"identificador de ancla inválido: {name}")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return (language, name, text)
    if tree.body:
        raise ValueError(f"ancla {language}:{name} parsea como Python")
    return (language, name, text)


FOREIGN_TRAIN_ANCHORS: tuple[tuple[str, str, str], ...] = (
    _anchor(
        "javascript",
        "v050_anchor_js_pallet_kg",
        """
function v050AnchorPalletKg(units, gramsEach) {
  const tareGrams = 180;
  if (units <= 0 || gramsEach <= 0) throw new Error("pallet");
  return units * gramsEach + tareGrams;
}
""",
    ),
    _anchor(
        "javascript",
        "v050_anchor_js_dock_eta",
        """
export function v050AnchorDockEta(queue, minutesEach) {
  const bufferMin = 7;
  return queue * minutesEach + bufferMin;
}
""",
    ),
    _anchor(
        "javascript",
        "v050_anchor_js_bin_checksum",
        """
const v050AnchorBinChecksum = (sku, bay) => {
  let fold = 17;
  const token = `${sku}:${bay}`;
  for (const glyph of token) fold = (fold * 33 + glyph.charCodeAt(0)) % 997;
  return fold;
};
""",
    ),
    _anchor(
        "javascript",
        "v050_anchor_js_route_legs",
        """
function v050AnchorRouteLegs(hops) {
  const dwell = hops.map((hop) => hop.km / hop.speed);
  return dwell.reduce((acc, item) => acc + item, 0);
}
""",
    ),
    _anchor(
        "javascript",
        "v050_anchor_js_sensor_gap",
        """
function v050AnchorSensorGap(leftMm, rightMm) {
  const gap = Math.abs(leftMm - rightMm);
  return { gap, alarm: gap > 12 };
}
""",
    ),
    _anchor(
        "javascript",
        "v050_anchor_js_label_batch",
        """
async function v050AnchorLabelBatch(count) {
  const sheets = Math.ceil(count / 24);
  return { count, sheets };
}
""",
    ),
    _anchor(
        "sql",
        "v050_anchor_sql_create_docks",
        """
CREATE TABLE v050_anchor_docks (
  dock_id INTEGER PRIMARY KEY,
  bay_code TEXT NOT NULL,
  max_kg REAL NOT NULL
);
""",
    ),
    _anchor(
        "sql",
        "v050_anchor_sql_insert_pallet",
        """
INSERT INTO v050_anchor_pallets (pallet_id, dock_id, mass_kg)
VALUES (4401, 7, 612.5);
""",
    ),
    _anchor(
        "sql",
        "v050_anchor_sql_select_late",
        """
SELECT dock_id, bay_code
FROM v050_anchor_docks
WHERE max_kg < 800
ORDER BY bay_code;
""",
    ),
    _anchor(
        "sql",
        "v050_anchor_sql_update_bay",
        """
UPDATE v050_anchor_docks
SET max_kg = max_kg - 25
WHERE bay_code = 'N-14';
""",
    ),
    _anchor(
        "sql",
        "v050_anchor_sql_index_sku",
        """
CREATE INDEX v050_anchor_sku_idx
ON v050_anchor_pallets (dock_id, mass_kg);
""",
    ),
    _anchor(
        "sql",
        "v050_anchor_sql_delete_stale",
        """
DELETE FROM v050_anchor_pallets
WHERE mass_kg = 0 AND dock_id = 7;
""",
    ),
    _anchor(
        "bash",
        "v050_anchor_bash_set_pipefail",
        """
#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "v050-anchor-dock-probe"
""",
    ),
    _anchor(
        "bash",
        "v050_anchor_bash_loop_bays",
        """
#!/usr/bin/env bash
for bay in N-14 N-15 N-16; do
  printf '%s\\n' "$bay"
done
""",
    ),
    _anchor(
        "bash",
        "v050_anchor_bash_case_shift",
        """
#!/usr/bin/env bash
shift_name="night"
case "$shift_name" in
  night) printf '%s\\n' "v050-anchor-night" ;;
  day) printf '%s\\n' "v050-anchor-day" ;;
esac
""",
    ),
    _anchor(
        "bash",
        "v050_anchor_bash_rsync_docks",
        """
#!/usr/bin/env bash
set -euo pipefail
rsync -a /var/v050_anchor/docks/ /var/v050_anchor/archive/
""",
    ),
    _anchor(
        "bash",
        "v050_anchor_bash_awk_weights",
        """
#!/usr/bin/env bash
awk 'BEGIN { sum = 0 } { sum += $2 } END { printf "%s\\n", sum }' /var/v050_anchor/weights.tsv
""",
    ),
    _anchor(
        "bash",
        "v050_anchor_bash_curl_probe",
        """
#!/usr/bin/env bash
set -euo pipefail
curl -fsS "http://127.0.0.1:9/v050-anchor-health" || printf '%s\\n' "v050-anchor-down"
""",
    ),
    _anchor(
        "rust",
        "v050_anchor_rs_pallet_mass",
        """
fn v050_anchor_pallet_mass(units: i64, grams_each: i64) -> i64 {
    let tare = 180;
    units * grams_each + tare
}
""",
    ),
    _anchor(
        "rust",
        "v050_anchor_rs_bay_span",
        """
pub fn v050_anchor_bay_span(start_mm: i64, end_mm: i64) -> i64 {
    (end_mm - start_mm).abs()
}
""",
    ),
    _anchor(
        "rust",
        "v050_anchor_rs_checksum_fold",
        """
fn v050_anchor_checksum_fold(sku: &str) -> u32 {
    let mut fold: u32 = 17;
    for byte in sku.bytes() {
        fold = fold.wrapping_mul(33).wrapping_add(u32::from(byte)) % 997;
    }
    fold
}
""",
    ),
    _anchor(
        "rust",
        "v050_anchor_rs_route_delay",
        """
fn v050_anchor_route_delay(hops: &[i64]) -> i64 {
    hops.iter().copied().sum()
}
""",
    ),
    _anchor(
        "rust",
        "v050_anchor_rs_sensor_pair",
        """
struct V050AnchorSensor {
    left_mm: i64,
    right_mm: i64,
}
""",
    ),
    _anchor(
        "rust",
        "v050_anchor_rs_label_quota",
        """
fn v050_anchor_label_quota(count: i64) -> i64 {
    (count + 23) / 24
}
""",
    ),
    _anchor(
        "c",
        "v050_anchor_c_dock_load",
        """
#include <stdint.h>
int v050_anchor_dock_load(int units, int grams_each) {
    const int tare = 180;
    return units * grams_each + tare;
}
""",
    ),
    _anchor(
        "c",
        "v050_anchor_c_bay_gap",
        """
#include <stdint.h>
int v050_anchor_bay_gap(int left_mm, int right_mm) {
    int gap = left_mm - right_mm;
    return gap < 0 ? -gap : gap;
}
""",
    ),
    _anchor(
        "c",
        "v050_anchor_c_crc_step",
        """
#include <stdint.h>
uint32_t v050_anchor_crc_step(uint32_t fold, uint8_t byte) {
    return (fold * 33u + byte) % 997u;
}
""",
    ),
    _anchor(
        "c",
        "v050_anchor_c_route_ms",
        """
#include <stddef.h>
long v050_anchor_route_ms(const long *hops, size_t count) {
    long total = 0;
    for (size_t index = 0; index < count; index++) total += hops[index];
    return total;
}
""",
    ),
    _anchor(
        "c",
        "v050_anchor_c_sensor_clip",
        """
#include <stdint.h>
int v050_anchor_sensor_clip(int gap_mm) {
    if (gap_mm < 0) return 0;
    if (gap_mm > 12) return 12;
    return gap_mm;
}
""",
    ),
    _anchor(
        "c",
        "v050_anchor_c_label_cap",
        """
#include <stdint.h>
int v050_anchor_label_cap(int count) {
    return (count + 23) / 24;
}
""",
    ),
    _anchor(
        "go",
        "v050_anchor_go_pallet_kg",
        """
package v050anchor

func V050AnchorPalletKg(units int, gramsEach int) int {
    const tare = 180
    return units*gramsEach + tare
}
""",
    ),
    _anchor(
        "go",
        "v050_anchor_go_dock_queue",
        """
package v050anchor

func V050AnchorDockQueue(queue int, minutesEach int) int {
    const bufferMin = 7
    return queue*minutesEach + bufferMin
}
""",
    ),
    _anchor(
        "go",
        "v050_anchor_go_bay_free",
        """
package v050anchor

func V050AnchorBayFree(capacity int, occupied int) int {
    if occupied >= capacity {
        return 0
    }
    return capacity - occupied
}
""",
    ),
    _anchor(
        "go",
        "v050_anchor_go_route_hops",
        """
package v050anchor

func V050AnchorRouteHops(hops []int) int {
    total := 0
    for _, hop := range hops {
        total += hop
    }
    return total
}
""",
    ),
    _anchor(
        "go",
        "v050_anchor_go_sensor_ok",
        """
package v050anchor

func V050AnchorSensorOk(leftMm int, rightMm int) bool {
    gap := leftMm - rightMm
    if gap < 0 {
        gap = -gap
    }
    return gap <= 12
}
""",
    ),
    _anchor(
        "go",
        "v050_anchor_go_label_run",
        """
package v050anchor

func V050AnchorLabelRun(count int) int {
    if count <= 0 {
        return 0
    }
    return (count + 23) / 24
}
""",
    ),
)


def foreign_anchor_leakage(
    anchors: Sequence[tuple[str, str, str]],
    foreign_snippets: Sequence[tuple[str, str, str]],
    holdout_samples: Sequence[BenchmarkSample],
) -> list[str]:
    """Lista fugas de identificador o texto normalizado. Vacía significa disjunto."""
    foreign_ids = {f"{language}:{name}" for language, name, _source in foreign_snippets}
    foreign_names = {name for _language, name, _source in foreign_snippets}
    foreign_text = {normalize_text(source) for _language, _name, source in foreign_snippets}
    holdout_ids = {sample.sample_id for sample in holdout_samples}
    holdout_text = {normalize_text(sample.text) for sample in holdout_samples}
    leaks: list[str] = []
    seen: set[str] = set()
    for language, name, source in anchors:
        ident = f"{language}:{name}"
        if ident in seen:
            leaks.append(f"duplicate:{ident}")
        seen.add(ident)
        if ident in foreign_ids or name in foreign_names or ident in holdout_ids or name in holdout_ids:
            leaks.append(f"id:{ident}")
        text = normalize_text(source)
        if text in foreign_text or text in holdout_text:
            leaks.append(f"text:{ident}")
    return leaks


def assert_disjoint_from_test_a() -> None:
    """Falla si un ancla de entrenamiento aparece en Test A cal/test o en los 60 snippets."""
    dataset = _cached_dataset(42)
    _assert_split_ids(dataset)
    if len(FOREIGN_SNIPPETS) != 60:
        raise ValueError(f"snippets ajenos={len(FOREIGN_SNIPPETS)} != 60")
    holdout = [sample for sample in dataset if sample.split in _HOLDOUT_SPLITS]
    leaks = foreign_anchor_leakage(FOREIGN_TRAIN_ANCHORS, FOREIGN_SNIPPETS, holdout)
    if leaks:
        preview = ", ".join(leaks[:3])
        raise ValueError(f"FOREIGN_TRAIN_ANCHORS filtra hacia el holdout: {preview}")


def fit_v2_spectral_ast(
    embedder: object,
    *,
    alpha: float = 0.05,
    seed: int = 42,
    include_foreign_code_anchors: bool = True,
) -> M4_HybridAstSpectral:
    """Ajusta M4 con positivos de train, negativos vistos y, si corresponde, anclas ajenas."""
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError(f"alpha debe estar en (0, 1), recibido: {alpha}")
    dimension = int(getattr(embedder, "dimension"))
    if dimension < 1:
        raise ValueError(f"dimension inválida: {dimension}")
    dataset = _cached_dataset(int(seed))
    _assert_split_ids(dataset)
    positives = [
        sample
        for sample in dataset
        if sample.split == "train" and sample.category in _POSITIVE_TRAIN
    ]
    negatives = [
        sample
        for sample in dataset
        if sample.split == "train" and sample.category == "neg_seen_domain"
    ]
    calibration = [sample for sample in dataset if sample.split == "cal"]
    if len(calibration) != 72 or any(not sample.is_legitimate_python for sample in calibration):
        raise ValueError(f"calibracion positiva esperada=72, recibida={len(calibration)}")
    positive_rows = _matrix_for_samples(positives, embedder, dimension)
    negative_rows = _matrix_for_samples(negatives, embedder, dimension)
    foreign_negative = None
    if include_foreign_code_anchors:
        foreign_negative = _matrix_for_anchors(embedder, dimension)
    groups = _groups_for_samples(calibration, embedder, dimension)
    if len(groups) != 72:
        raise ValueError(f"grupos de calibracion={len(groups)} != 72")
    model = M4_HybridAstSpectral()
    model._fit_geometry(positive_rows, negative_rows, foreign_negative=foreign_negative)
    scores = np.asarray(
        [model.score_sample(chunks, vectors) for chunks, vectors in groups],
        dtype=np.float64,
    )
    if scores.shape != (72,):
        raise ValueError(f"scores de calibracion {scores.shape} != (72,)")
    model.q_hat = conformal_threshold(scores, alpha=float(alpha))
    return model


def save_v2_calibration(
    path: Path,
    model: M4_HybridAstSpectral,
    *,
    model_id: str,
    alpha: float = 0.05,
) -> Path:
    """Escribe tensores numéricos. El identificador viaja como bytes uint8, sin pickle."""
    if not isinstance(model, M4_HybridAstSpectral):
        raise TypeError("save_v2_calibration exige M4_HybridAstSpectral")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError("model_id vacío")
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError(f"alpha debe estar en (0, 1), recibido: {alpha}")
    for key in (*_TENSOR_KEYS, "q_hat", "shrinkage_pos", "shrinkage_neg", "dimension", "subspace_rank"):
        if getattr(model, key) is None:
            raise ValueError(f"modelo sin {key}")
    payload = {
        "mu_pos": np.asarray(model.mu_pos, dtype=np.float64),
        "w_hat": np.asarray(model.w_hat, dtype=np.float64),
        "u_k": np.asarray(model.u_k, dtype=np.float64),
        "gamma": np.asarray(model.gamma, dtype=np.float64),
        "medians": np.asarray(model.medians, dtype=np.float64),
        "iqrs": np.asarray(model.iqrs, dtype=np.float64),
        "q_hat": np.asarray(model.q_hat, dtype=np.float64),
        "shrinkage_pos": np.asarray(model.shrinkage_pos, dtype=np.float64),
        "shrinkage_neg": np.asarray(model.shrinkage_neg, dtype=np.float64),
        "alpha": np.asarray(float(alpha), dtype=np.float64),
        "dimension": np.asarray(model.dimension, dtype=np.int64),
        "subspace_rank": np.asarray(model.subspace_rank, dtype=np.int64),
        "model_id_utf8": np.array(
            np.frombuffer(model_id.encode("utf-8"), dtype=np.uint8),
            dtype=np.uint8,
            copy=True,
        ),
    }
    if model.w_hat_foreign is not None:
        if (
            model.foreign_median is None
            or model.foreign_iqr is None
            or model.shrinkage_foreign is None
        ):
            raise ValueError("w_hat_foreign sin anclaje foreign_median/foreign_iqr/shrinkage_foreign")
        payload["w_hat_foreign"] = np.asarray(model.w_hat_foreign, dtype=np.float64)
        payload["foreign_median"] = np.asarray(model.foreign_median, dtype=np.float64)
        payload["foreign_iqr"] = np.asarray(model.foreign_iqr, dtype=np.float64)
        payload["shrinkage_foreign"] = np.asarray(model.shrinkage_foreign, dtype=np.float64)
    for key, value in payload.items():
        if value.dtype == object:
            raise ValueError(f"{key} no puede ser dtype=object")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(target, **payload)
    written = target if target.suffix == ".npz" else target.with_name(target.name + ".npz")
    if not written.is_file():
        raise FileNotFoundError(written)
    return written


def load_v2_calibration(path: Path) -> tuple[M4_HybridAstSpectral, dict[str, object]]:
    """Reabre el .npz con allow_pickle=False y rearma un M4 usable."""
    with np.load(Path(path), allow_pickle=False) as handle:
        stored = {key: np.array(handle[key], copy=True) for key in handle.files}
    missing = [key for key in (*_TENSOR_KEYS, "q_hat", "shrinkage_pos", "shrinkage_neg", "alpha", "dimension", "subspace_rank", "model_id_utf8") if key not in stored]
    if missing:
        raise ValueError(f"npz incompleto: {missing}")
    model = M4_HybridAstSpectral()
    model.mu_pos = np.asarray(stored["mu_pos"], dtype=np.float64)
    model.w_hat = np.asarray(stored["w_hat"], dtype=np.float64)
    model.u_k = np.asarray(stored["u_k"], dtype=np.float64)
    model.gamma = np.asarray(stored["gamma"], dtype=np.float64)
    model.medians = np.asarray(stored["medians"], dtype=np.float64)
    model.iqrs = np.asarray(stored["iqrs"], dtype=np.float64)
    model.q_hat = float(np.asarray(stored["q_hat"], dtype=np.float64).reshape(-1)[0])
    model.shrinkage_pos = float(np.asarray(stored["shrinkage_pos"], dtype=np.float64).reshape(-1)[0])
    model.shrinkage_neg = float(np.asarray(stored["shrinkage_neg"], dtype=np.float64).reshape(-1)[0])
    model.dimension = int(np.asarray(stored["dimension"], dtype=np.int64).reshape(-1)[0])
    model.subspace_rank = int(np.asarray(stored["subspace_rank"], dtype=np.int64).reshape(-1)[0])
    foreign_keys = ("w_hat_foreign", "foreign_median", "foreign_iqr", "shrinkage_foreign")
    present = [key for key in foreign_keys if key in stored]
    if present and len(present) != len(foreign_keys):
        raise ValueError(f"npz con hiperplano ajeno incompleto: {present}")
    if len(present) == len(foreign_keys):
        model.w_hat_foreign = np.asarray(stored["w_hat_foreign"], dtype=np.float64)
        model.foreign_median = float(
            np.asarray(stored["foreign_median"], dtype=np.float64).reshape(-1)[0]
        )
        model.foreign_iqr = float(np.asarray(stored["foreign_iqr"], dtype=np.float64).reshape(-1)[0])
        model.shrinkage_foreign = float(
            np.asarray(stored["shrinkage_foreign"], dtype=np.float64).reshape(-1)[0]
        )
    else:
        model.w_hat_foreign = None
        model.foreign_median = None
        model.foreign_iqr = None
        model.shrinkage_foreign = None
    model_id = bytes(np.asarray(stored["model_id_utf8"], dtype=np.uint8)).decode("utf-8")
    alpha = float(np.asarray(stored["alpha"], dtype=np.float64).reshape(-1)[0])
    meta: dict[str, object] = {
        "model_id": model_id,
        "alpha": alpha,
        "dimension": model.dimension,
        "subspace_rank": model.subspace_rank,
        "q_hat": model.q_hat,
        "shrinkage_pos": model.shrinkage_pos,
        "shrinkage_neg": model.shrinkage_neg,
    }
    return model, meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calibra M4 v0.5.0 y escribe un .npz sin pickle.")
    parser.add_argument("--embedder", choices=("bge-m3", "fake"), required=True)
    parser.add_argument("--out", type=Path, default=Path("ddi_fw/out/v2_spectral_ast.npz"))
    parser.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args(argv)
    embedder = get_embedder("fake" if args.embedder == "fake" else "bge-m3")
    model = fit_v2_spectral_ast(embedder, alpha=float(args.alpha), seed=42)
    save_v2_calibration(args.out, model, model_id=str(embedder.model_id), alpha=float(args.alpha))
    return 0


@lru_cache(maxsize=4)
def _cached_dataset(seed: int) -> tuple[BenchmarkSample, ...]:
    return tuple(build_test_a_dataset(seed=seed))


def _assert_split_ids(dataset: Sequence[BenchmarkSample]) -> None:
    grouped = {
        split: {sample.sample_id for sample in dataset if sample.split == split}
        for split in ("train", "cal", "test")
    }
    pairs = (("train", "cal"), ("train", "test"), ("cal", "test"))
    for left, right in pairs:
        if not grouped[left].isdisjoint(grouped[right]):
            raise ValueError(f"sample_id repetido entre {left} y {right}")
    if not grouped["train"] or not grouped["cal"] or not grouped["test"]:
        raise ValueError("un split del Test A quedó vacío")


def _embed_texts(embedder: object, texts: list[str], dimension: int) -> np.ndarray:
    if not texts:
        return np.zeros((0, dimension), dtype=np.float64)
    parts: list[np.ndarray] = []
    for start in range(0, len(texts), _EMBED_BATCH):
        batch = texts[start : start + _EMBED_BATCH]
        rows = np.asarray(embedder.embed_batch(batch), dtype=np.float64)
        if rows.ndim != 2 or rows.shape != (len(batch), dimension):
            raise ValueError(f"embed_batch shape {getattr(rows, 'shape', None)} != {(len(batch), dimension)}")
        parts.append(rows)
    return np.vstack(parts)


def _chunks_of(text: str, label: str) -> list[TextChunk]:
    chunks = extract_chunks(text)
    if not chunks:
        raise ValueError(f"sin chunks: {label}")
    return chunks


def _matrix_for_samples(
    samples: Sequence[BenchmarkSample], embedder: object, dimension: int
) -> np.ndarray:
    texts: list[str] = []
    for sample in samples:
        texts.extend(chunk.text for chunk in _chunks_of(sample.text, sample.sample_id))
    matrix = _embed_texts(embedder, texts, dimension)
    if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[1] != dimension:
        raise ValueError(f"matriz de muestras inválida: {matrix.shape}")
    return matrix


def _matrix_for_anchors(embedder: object, dimension: int) -> np.ndarray:
    texts: list[str] = []
    for language, name, source in FOREIGN_TRAIN_ANCHORS:
        texts.extend(chunk.text for chunk in _chunks_of(source, f"{language}:{name}"))
    matrix = _embed_texts(embedder, texts, dimension)
    if matrix.ndim != 2 or matrix.shape[0] < 1 or matrix.shape[1] != dimension:
        raise ValueError(f"matriz de anclas inválida: {matrix.shape}")
    return matrix


def _groups_for_samples(
    samples: Sequence[BenchmarkSample], embedder: object, dimension: int
) -> list[tuple[list[TextChunk], np.ndarray]]:
    layouts: list[list[TextChunk]] = []
    texts: list[str] = []
    for sample in samples:
        chunks = _chunks_of(sample.text, sample.sample_id)
        layouts.append(chunks)
        texts.extend(chunk.text for chunk in chunks)
    matrix = _embed_texts(embedder, texts, dimension)
    groups: list[tuple[list[TextChunk], np.ndarray]] = []
    cursor = 0
    for chunks in layouts:
        count = len(chunks)
        groups.append((chunks, matrix[cursor : cursor + count]))
        cursor += count
    if cursor != matrix.shape[0]:
        raise ValueError("los grupos de calibracion no cubren la matriz")
    return groups


if __name__ == "__main__":
    raise SystemExit(main())

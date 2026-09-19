# Q01 — Artifact isolation + no-prune measure

> **Estado:** hecho
> **Ola:** Qwen2 live (Q)
> **Briefing (wins conflicts):** [`../00-qwen2-live.md`](../00-qwen2-live.md)
> **Live model:** no

---

## Objective

Make it *impossible* for a later live run to (a) overwrite BGE-M3 blobs or (b) silently prune decks via `calibrate()`.

Add a **no-prune** persist/measure path and send Qwen2 artifacts to `ddi_fw/out/qwen2/`.

---

## Why this exists

`ddi_fw.embedder.calibrate()` always calls `podar_hasta_publicar` before `save_rows`. With `rewrite_fixtures=False` it still drops rows from `rows.npz` and raises `RuntimeError` if a pair stays unpublished.

BGE-M3 used that path. Qwen2 **must not**. Primary geometry = full current decks.

`measure_embedder` in `ddi_fw/benchmark.py` already embeds without pruning. It does not persist `rows.npz`.

---

## Files to create / modify

- `ddi_fw/embedder.py` (or a tiny `ddi_fw/measure.py` if that keeps `calibrate` closed):
  - Function `measure_and_save(embedder, *, data_dir, out_dir) -> audit dict`
  - Calls `load_almas` → `embed_mazos` → `candados_canonicos` → `save_rows`
  - **Never** calls `podar_hasta_publicar`
  - **Never** writes `ddi_fw/data/`
  - Writes `out_dir / "rows.npz"` and `out_dir / "measure_audit.json"`
  - Audit keys: `model_id`, `dimension`, `n`, `published`, `disjoint_count`, `disjoint_axes` (list[int] per pair), `dropped` (must be `[]`)
- `ddi_fw/embedder.py` CLI: `--no-prune` (required for this campaign) and honour `--out` as a **directory or npz path** without defaulting to `ddi_fw/out/rows.npz` when `--out ddi_fw/out/qwen2`
- `ddi_fw/press.py`: `--benchmark-all --out DIR` already writes `DIR/benchmark_models.json`; keep it. Do not write `ddi_fw/out/benchmark_models.json` when `--out` is set.
- `tests/test_ddi_measure_no_prune.py` (name may vary): FakeEmbedder only.

Do **not** change `Settings.embedder` default to `qwen2`. Product default may stay `bge-m3` or `fake` as today.

---

## Out of scope

- Loading Qwen2 (Q02).
- Geometry interpretation (Q03).
- Ingress/hold (Q04).
- Pinning `transformers`.
- Editing `roadmap/archive/**`.

---

## TDD

1. FakeEmbedder 8-D, two almas with engineered disjoint axis → `measure_and_save` writes npz, `dropped == []`, `published` true, file under `tmp_path/qwen2/` not `ddi_fw/out/rows.npz`.
2. FakeEmbedder with overlapping intervals → `published` false, **no exception**, `dropped == []`, npz still written (full n). Contrast: `calibrate()` would raise — do not call it.
3. `uv run pytest` (full default suite) green.

```bash
uv run pytest -q
```

---

## Definition of Done

- [ ] No-prune API exists and is the documented Qwen2 path in `00-qwen2-live.md` §6 if the function name differs (update that section in the same change).
- [ ] CLI can persist to `ddi_fw/out/qwen2/` without touching `ddi_fw/out/rows.npz`.
- [ ] Default pytest green.
- [ ] This ticket marked `hecho` in [`../README.md`](../README.md).

---

## Copiable prompt

```text
Using dev-protocol, execute roadmap/tickets/Q01-artifact-isolation-no-prune.md.
Read roadmap/00-qwen2-live.md first; it wins conflicts.
Add measure_and_save (no podar_hasta_publicar, no rewrite fixtures) and isolate artifacts under ddi_fw/out/qwen2/.
FakeEmbedder tests only. Do not load Qwen2. Do not edit archive or ddi_fw/data/.
uv run pytest -q must stay green.
Mark Q01 hecho in roadmap/README.md when done.
```

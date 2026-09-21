# Q03 — Full-deck geometry + press

> **Estado:** hecho (`ok_unpublished` headlines)
> **Ola:** Qwen2 live (Q)
> **Depends on:** Q02 smoke `ok` (if Q02 is `blocker_*`, skip live here, write `—` in geometry cells, still close Q05 later)
> **Briefing:** [`../00-qwen2-live.md`](./00-qwen2-live.md)
> **Live model:** yes, full `alma` decks

---

## Objective

Embed the **current** decks (`python` 21, `legal` 16, `receta` 17) with Qwen2, compute `hoja` / `disjoint axes` / `published` for the three canonical pairs, persist under `ddi_fw/out/qwen2/`, run `press`.

This is the BGE Layer B geometry step, **without** BGE’s “all pairs must publish” gate.

---

## Procedure (deterministic)

1. Confirm Q01 no-prune path exists. **Do not call `calibrate()`.**
2. `load_almas()` from committed `ddi_fw/data/`. Do not run `python -m ddi_fw.almas`.
3. `measure_and_save(..., out_dir=Path("ddi_fw/out/qwen2"))` (name from Q01).
4. Assert `measure_audit.json`:
   - `model_id` == `Alibaba-NLP/gte-Qwen2-1.5B-instruct`
   - `dimension` == 1536
   - `n.python` == 21, `n.legal` == 16, `n.receta` == 17
   - `dropped` == []
5. For each pair `python_receta`, `python_legal`, `legal_receta` record:
   - `published` (bool)
   - `disjoint_count` (int)
   - `disjoint_axes` (list[int], full list, not a sample)
   - `mean_gap`, `max_gap` on disjoint axes only (0.0 if none) — diagnostic
6. Press without re-embedding:

```bash
uv run python -m ddi_fw.press --rows ddi_fw/out/qwen2/rows.npz --out ddi_fw/out/qwen2
```

7. Optional extra:

```bash
uv run python -m ddi_fw.press --benchmark-all --live --models qwen2 --out ddi_fw/out/qwen2
```

   Only if this does not load a second copy of the model on top of a resident one. Prefer process-exit between Q02 and Q03.

8. Copy **numbers** (not `.npz`) into [`../../current-research/engines/gte-qwen2-1.5b.md`](../../current-research/engines/gte-qwen2-1.5b.md) and the Qwen2 ledger row.

If a pair is unpublished: outcome `ok_unpublished`. Continue. Do not drop clauses. Do not compare “we should prune like receta-012” — that was BGE-specific and is frozen.

---

## Press fields to capture (no `mean_*` in `press.json`)

Per pair, from `press.json`: `disjoint_axes`, `disjoint_count`, `published`, census by family, `vote_count_extrema` `{lo,hi}` for `solo_a` / `solo_b` / `ambas` / `ninguna`.

Headline census analogue of BGE’s 21/21 left and 17/17 right: count how many python rows hard-cut `left` and how many receta rows hard-cut `right` on `python_receta` **if published**. If unpublished, write `n/a (unpublished)`.

---

## Out of scope

- Changing decks.
- Ingress/hold (Q04).
- Editing BGE ledger row or `roadmap/archive/**`.
- Committing `rows.npz`.

---

## Definition of Done

- [x] `ddi_fw/out/qwen2/rows.npz` + `press.json` + `measure_audit.json` exist locally (gitignored).
- [x] Engine dump has the three pairs filled with one of `ok_published` / `ok_unpublished` / `blocker_*`.
- [x] `dropped` is [] (full decks 21/16/17).
- [x] Default pytest green.
- [x] Ticket `hecho` in [`../README.md`](../README.md).

---

## Copiable prompt

```text
Using dev-protocol, execute roadmap/archive/ola-q/Q03-geometry-press.md.
Read roadmap/archive/ola-q/00-qwen2-live.md first.
Use the Q01 no-prune path. Never calibrate() / never --rewrite-fixtures.
Embed python=21, legal=16, receta=17 with Qwen2 at 1536-D.
Write artifacts only under ddi_fw/out/qwen2/.
Zero disjoint axes is ok_unpublished, not a reason to prune mazos.
Copy numbers into current-research/engines/gte-qwen2-1.5b.md and the Qwen2 ledger row only.
Do not commit npz. Do not edit the BGE-M3 row.
```

# Engine dump — `BAAI/bge-m3`

**SEALED.** 2026-09-19. Do not re-run to “confirm”. Do not edit numbers. New facts go to another engine file.

| Field | Value |
| :--- | :--- |
| `model_id` | `BAAI/bge-m3` |
| `dimension` | 1024 |
| License | MIT, ungated |
| Adapter | `BGEM3Embedder` / `get_embedder("bge-m3")` |
| Decks | `python` n=21, `legal` n=16, `receta` n=17 |
| Excluded seed | `receta-012` (almíbar / hebra fina). Bridge clause killed `python_receta` disjunction. **Do not reintroduce.** |
| Git pin | tag `v0.1.0-bge-m3-baseline` (`37ae3fe`) |
| Live test | `tests/test_ddi_live.py` — **do not edit** |

## Pairs

| Pair | `published` | `disjoint_count` | `disjoint_axes` | notes |
| :--- | :--- | ---: | :--- | :--- |
| `python_receta` | true | 1 | `[891]` | headline. `gap` ≈ 0.004 |
| `python_legal` | true | 1 | `[192]` | headline. `gap` ≈ 0.014 |
| `legal_receta` | true | 7 | (count only in this dump; see original press if present locally) | control pair |

Headline census `python_receta`: 21/21 `left` (python), 17/17 `right` (receta).

## Protocol notes

- Decision rule: interval inclusion + `corte duro` on disjoint axes. No `cosine`, no centroids, no `mean` of rows.
- `calibrate()` **pruned** toward publish for BGE. That is **not** the Qwen2 path (`roadmap/archive/ola-q/00-qwen2-live.md` §6).
- `mean_gap` lived only in `benchmark_models.json`.

## Other engines that day (not this dump’s geometry)

- Nomic v1.5: `blocker_load` (transformers 5.17 / `get_extended_attention_mask`)
- EmbeddingGemma 300m: `blocker_load` (gated 401)
- Qwen2 1.5B: skipped RAM; adapter existed. Geometry: **not measured**. Wave Q does that.

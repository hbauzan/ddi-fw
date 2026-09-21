# Engine dump — `Alibaba-NLP/gte-Qwen2-1.5B-instruct`

Wave Q, 2026-09-19. Do not copy BGE axis ids here as if they transferred.

| Field | Value |
| :--- | :--- |
| `model_id` | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` |
| CLI | `qwen2` / `qwen` |
| Adapter | `Qwen2Embedder` / `get_embedder("qwen2")` (singleton) |
| `dimension` | 1536 (asserted; not MRL) |
| License | Apache-2.0, ungated |
| `trust_remote_code` | true |
| Hub tag | `custom_code` |
| Parameters | ~1.78e9 |
| Load dtype | float16 (16 GiB host) |
| Compat shims | `apply_qwen2_transformers517_shim`: `Qwen2Config.rope_theta` from `rope_parameters`; `DynamicCache.from_legacy_cache` / `get_usable_length` / `to_legacy_cache`; `config.use_cache=False` |
| Artifacts (gitignored) | `ddi_fw/out/qwen2/rows.npz`, `measure_audit.json`, `press.json` |
| Decks | `python` 21, `legal` 16, `receta` 17, `dropped=[]` |
| Stack | `sentence-transformers` 6.1.0 → `transformers` 5.17.0 |
| Product pin after Q05 | keep `BAAI/bge-m3` |

## Q02 smoke

| Field | Value |
| :--- | :--- |
| Date | 2026-09-19 |
| Clause | `Explicá el funcionamiento de list.append en Python.` |
| Outcome | `ok` (after shims; first attempt was `blocker_load` `rope_theta`) |
| Encode shape | `(1536,)` float32 finite |
| First encode (incl. load) | 14.253 s, RSS 4408.7 MB (pytest live) |
| Hub fetch | ok. Not 401. Not OOM. `lm_head.weight` UNEXPECTED (encoder path; ignored). |

First crash (documented, then unblocked without pinning transformers 4.x):

```
AttributeError: 'Qwen2Config' object has no attribute 'rope_theta'
modeling_qwen.py:225  self.rope_theta = config.rope_theta
```

Second crash, unblocked with cache shim + `use_cache=False`:

```
AttributeError: type object 'DynamicCache' has no attribute 'from_legacy_cache'
modeling_qwen.py:1000
```

Live pytest: `uv run pytest --run-live tests/test_ddi_live_qwen2.py` — smoke + measure green; ingress skipped unpublished.

## Q03 geometry

`measure_and_save` / `--no-prune`. No `calibrate()`. Decks untouched.

| Pair | outcome | `published` | `disjoint_count` | `disjoint_axes` | `mean_gap` | `max_gap` |
| :--- | :--- | :--- | ---: | :--- | ---: | ---: |
| `python_receta` | `ok_unpublished` | false | 0 | `[]` | 0.0 | 0.0 (all-axes max −0.001396, overlap) |
| `python_legal` | `ok_unpublished` | false | 0 | `[]` | 0.0 | 0.0 (all-axes max −0.001396, overlap) |
| `legal_receta` | `ok_published` | true | 1 | `[660]` | 0.002617 | 0.002617 |

`n` after measure (must equal 21/16/17):

| alma | n |
| :--- | ---: |
| `python` | 21 |
| `legal` | 16 |
| `receta` | 17 |

Headline census `python_receta` (`left` python / `right` receta):

`n/a (unpublished)` — 21/21 `out`, 17/17 `out`. No corte duro.

Control census `legal_receta`: 16/16 `left` (legal), 17/17 `right` (receta) on axis 660.

## Q04 ingress / hold

| Case | Result |
| :--- | :--- |
| Gate | `skipped_unpublished` (`python_receta` not published) |
| `PYTHON_ONLY` | — (not a piggyback measurement) |
| `PIGGYBACK` | — |
| `PYTHON_PLUS_RECIPE` | — |
| `hold(PYTHON_ANSWER)` | — |
| `hold(RECIPE_ANSWER)` | — |
| proxy (optional) | skipped |

Unpublished headline locks are fail-closed `BREACH`. That is not evidence that piggyback containment works.

## Same-host perf (separate process, after warmup encode)

Host: darwin 16 GiB. One embedder resident. `measure_embedder` on the three mazos (54 cláusulas).

| Field | Qwen2 (this dump) |
| :--- | ---: |
| `latency_us_per_clause` | 39350 |
| `memory_mb` (RSS after full decks) | 5846.5 |
| warmup first encode (s) | 13.08 (weights already in Hub cache) |

BGE-M3 on the **same** host/protocol, separate process, **not** written into the sealed BGE dump: `latency_us_per_clause` 15179, RSS 3023.1 MB, warmup 114.3 s. Geometry of that BGE process matched the sealed row (1 / 1 / 7); those axis ids stay in `engines/bge-m3.md`.

## Q05 note

Keep / replace BGE pin? **Keep `BAAI/bge-m3`.** Qwen2 did not publish headline pairs. Live piggyback was skipped. More D (1536 vs 1024) did not yield more headline disjunction (0 / 0 vs BGE 1 / 1). Control pair weaker (1 vs 7). Heavier and slower.

## Operator

Agent / date: Cursor agent, 2026-09-19, branch `feat/qwen2-live`. Host: darwin 16 GiB, Python 3.14.3.

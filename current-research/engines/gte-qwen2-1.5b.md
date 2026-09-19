# Engine dump — `Alibaba-NLP/gte-Qwen2-1.5B-instruct`

Wave Q, 2026-09-19. Do not copy BGE axis ids here as if they transferred.

| Field | Value |
| :--- | :--- |
| `model_id` | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` |
| CLI | `qwen2` / `qwen` |
| Adapter | `Qwen2Embedder` / `get_embedder("qwen2")` |
| Expected `dimension` | 1536 |
| License | Apache-2.0, ungated |
| `trust_remote_code` | true |
| Hub tag | `custom_code` |
| Parameters | ~1.78e9 |
| Artifacts (gitignored) | `ddi_fw/out/qwen2/` — **not written** (load never returned) |
| Decks (must remain) | `python` 21, `legal` 16, `receta` 17, `dropped=[]` |
| Stack | `sentence-transformers` 6.1.0 → `transformers` 5.17.0 |
| Product pin after Q05 | keep `BAAI/bge-m3` |

## Q02 smoke

| Field | Value |
| :--- | :--- |
| Date | 2026-09-19 |
| Clause | `Explicá el funcionamiento de list.append en Python.` |
| Outcome | `blocker_load` |
| Encode shape | — (crash in `SentenceTransformer.__init__`) |
| `memory_mb` | n/a (weights `__init__` aborted) |
| Hub fetch | ok (~4m36s, 2 files). Not 401. Not OOM. |
| Error / traceback (trim secrets) | `AttributeError: 'Qwen2Config' object has no attribute 'rope_theta'` |

Hub `custom_code` file: `modeling_qwen.py` (revision `a9af15a6372d7d6b25e9fb07c2ccb9e1fe645644`).

Trimmed traceback:

```
Qwen2DecoderLayer.__init__
  -> Qwen2Attention.__init__  (modeling_qwen.py:225)
     self.rope_theta = config.rope_theta
transformers 5.17 configuration_utils / heterogeneity:
  AttributeError: 'Qwen2Config' object has no attribute 'rope_theta'
```

Same class of failure as Nomic vs transformers 5.17. **Not** geometry. Adapter left in place. Did **not** pin `transformers==4.*`. Did **not** swap MiniLM / E5 / Nomic / Gemma / BGE.

Live pytest: `uv run pytest --run-live tests/test_ddi_live_qwen2.py -k test_live_qwen2_load_encodes_one_clause_1536` (failed, 283s). Default `uv run pytest` skips `live`.

## Q03 geometry

Skipped live: Q02 `blocker_load`. No `measure_and_save` on Qwen2. No `calibrate()`. Decks untouched.

| Pair | outcome | `published` | `disjoint_count` | `disjoint_axes` | `mean_gap` | `max_gap` |
| :--- | :--- | :--- | ---: | :--- | ---: | ---: |
| `python_receta` | `blocker_load` | — | — | — | — | — |
| `python_legal` | `blocker_load` | — | — | — | — | — |
| `legal_receta` | `blocker_load` | — | — | — | — | — |

`n` after measure (must equal 21/16/17):

| alma | n |
| :--- | ---: |
| `python` | — (not embedded) |
| `legal` | — (not embedded) |
| `receta` | — (not embedded) |

Press headline census `python_receta` (`left` python / `right` receta), or `n/a (unpublished)`:

`n/a (blocker_load)` — `ddi_fw/out/qwen2/press.json` was not written.

## Q04 ingress / hold

| Case | Result |
| :--- | :--- |
| Gate | skipped blocker (`blocker_load` from Q02) |
| `PYTHON_ONLY` | — |
| `PIGGYBACK` | — |
| `PYTHON_PLUS_RECIPE` | — |
| `hold(PYTHON_ANSWER)` | — |
| `hold(RECIPE_ANSWER)` | — |
| proxy (optional) | skipped (Ollama not required; load already blocked) |

No unpublished-lock piggyback measurement: the engine never produced locks.

## Q05 note

Keep / replace BGE pin? **Keep `BAAI/bge-m3`.** Qwen2 did not publish headline pairs, did not run piggyback BREACH/PASS, and did not encode. Comparison rules in `roadmap/00-qwen2-live.md` / Q05 are not met.

## Operator

Agent / date / git commit of code used: Cursor agent, 2026-09-19, branch `feat/qwen2-live` (Q01 `ae6d8c6`; Q02–Q05 this follow-up commit). Host: darwin 16 GiB, Python 3.14.3.

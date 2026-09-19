# Engine dump — `Alibaba-NLP/gte-Qwen2-1.5B-instruct`

Fill during tickets Q02–Q05. Do not copy BGE axis ids here as if they transferred.

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
| Artifacts (gitignored) | `ddi_fw/out/qwen2/` |
| Decks (must remain) | `python` 21, `legal` 16, `receta` 17, `dropped=[]` |

## Q02 smoke

| Field | Value |
| :--- | :--- |
| Date | 2026-09-19 |
| Outcome | `blocker_load` |
| Encode shape | — (never reached; `from_pretrained` raised) |
| `memory_mb` | 765.7 (peak RSS at failure) |
| Error / traceback (trim secrets) | `AttributeError: 'Qwen2Config' object has no attribute 'rope_theta'` |

### Q02 blocker detail

Snapshot `Alibaba-NLP/gte-Qwen2-1.5B-instruct` downloaded intact (18 files, 8.2 GB,
revision `a9af15a6372d7d6b25e9fb07c2ccb9e1fe645644`). The failure is **not** a download
or OOM problem: it dies in ~5 s at ~766 MB RSS, before any weight is read.

The hub ships `modeling_qwen.py` tagged `custom_code`. Its `QWEN2Attention.__init__`
(line 225) reads `config.rope_theta`. Under the pinned stack
(`sentence-transformers` 6.1.0 → `transformers` 5.17.0), `AutoModel.from_pretrained`
hands the remote module a `transformers`-native `Qwen2Config` whose attribute
resolution no longer exposes `rope_theta` the way the vendored file expects. Same
class of breakage as Nomic's `get_extended_attention_mask` vs `transformers` 5.x.

This is a **`blocker_load`**, not a geometry result. Per briefing §3 and Q02, the
campaign stops here: no global `transformers==4.*` pin, no model swap, no Deletor.
Q03/Q04 live are consequently skipped (`blocker_load`); Q05 records the blocker.

Reproduction (after the snapshot is cached):

```bash
uv run python -c '
from ddi_fw.embedder import get_embedder
get_embedder("qwen2").embed_text("Explicá el funcionamiento de list.append en Python.")
'
# AttributeError: Qwen2Config object has no attribute 'rope_theta'
```

Note: `config.json` itself does contain `rope_theta`; the incompatibility is in the
vendored `custom_code` module's expectations vs `transformers` 5.17 internals.

## Q03 geometry

**Skipped — upstream `blocker_load` (Q02).** The adapter cannot instantiate the model
under the pinned stack, so no `rows.npz` was produced and no `hoja` / `disjoint axes`
exist for Qwen2. Geometry cells stay `—`; no numbers were invented.

| Pair | outcome | `published` | `disjoint_count` | `disjoint_axes` | `mean_gap` | `max_gap` |
| :--- | :--- | :--- | ---: | :--- | ---: | ---: |
| `python_receta` | `blocker_load` | — | — | — | — | — |
| `python_legal` | `blocker_load` | — | — | — | — | — |
| `legal_receta` | `blocker_load` | — | — | — | — | — |

`n` after measure (must equal 21/16/17):

| alma | n |
| :--- | ---: |
| `python` | — (no measure) |
| `legal` | — (no measure) |
| `receta` | — (no measure) |

Press headline census `python_receta` (`left` python / `right` receta), or `n/a (unpublished)`:

`n/a (blocker_load)` — `ddi_fw/out/qwen2/rows.npz` was never written, so `press` has
nothing to census. The Q01 no-prune path was verified with `FakeEmbedder` in
`tests/test_ddi_measure_no_prune.py`; it is ready for a future engine that loads.

## Q04 ingress / hold

**Skipped — gate unreachable.** The gate is `published.python_receta == true` from a
Qwen2 `measure_audit.json`, which does not exist because Q02 is `blocker_load`.
No Qwen2 locks ⇒ nothing to run ingress/hold against, and inventing locks or reusing
the frozen BGE `rows.npz` would be a fabrication. Fail-closed behaviour on unpublished
locks is already unit-tested; it is **not** a piggyback measurement and was not
misreported as one.

| Case | Result |
| :--- | :--- |
| Gate | `skipped` — upstream `blocker_load` (Q02) / no `python_receta` publish |
| `PYTHON_ONLY` | not run |
| `PIGGYBACK` | not run |
| `PYTHON_PLUS_RECIPE` | not run |
| `hold(PYTHON_ANSWER)` | not run |
| `hold(RECIPE_ANSWER)` | not run |
| proxy (optional) | not run (needs Ollama; optional, never gates DoD) |

No decks were pruned to manufacture a publish, and the committed canonical strings in
`tests/world.py` were left untouched.

## Q05 note

Keep / replace BGE pin? (default: keep `BAAI/bge-m3` unless briefing § comparison rules are all met)

## Operator

Agent / date / git commit of code used:

# Qwen2 live campaign — canonical briefing

**Audience:** another AI agent executing this pack. Read this file **before** any ticket.
**Language:** Spanish for procedure. English **canonical terms** are locked in backticks. Do not translate those tokens. Do not invent synonyms.
**Status:** `pendiente` (documentation only until tickets Q01–Q05 are executed).
**Date of briefing:** 2026-09-19.
**Base:** git tag `v0.1.0-bge-m3-baseline` (`37ae3fe`) plus later doc archive on `main`. Do not reopen D01–D07.

If any instruction here conflicts with a comment, a “helpful” refactor, or the archived D-tickets: **this file wins**.

---

## 0. One-sentence mission

Run the **same geometric protocol** that certified `BAAI/bge-m3` (1024-D), against **one other embedder**: `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (1536-D), on the **same** `alma` decks, **without mutating** BGE evidence, decks, or the archived roadmap.

This is a **measurement campaign**, not a product-default switch. After Q05 the operational pin may still be BGE-M3. Only the ledger may recommend otherwise.

---

## 1. Canonical vocabulary (do not paraphrase)

| Token | Meaning (locked) |
| :--- | :--- |
| `alma` | Small homogeneous deck of `cláusulas` of one craft (`python`, `legal`, `receta`). Not a scraped corpus. |
| `cláusula` / `clause` | One logical text unit, split on terminal punctuation, decimals preserved. Embedded and judged **alone**. |
| `fila` / `row` | Dense vector of one `cláusula`. Same text + same pinned embedder → identical `fila`. |
| `hoja` / `sheet` | Per-axis empirical intervals `[lo, hi]` of two `almas`. No means. No top-k. |
| `eje disjunto` / `disjoint axis` | Dimension where the two intervals do not touch: `gap > 0`. |
| `gap` | Signed separation of intervals. `gap > 0` ⇔ disjoint. Overlap ⇒ `gap ≤ 0`. Never invent `gap >= epsilon`. |
| `corte duro` / `hard cut` | Label `left` \| `right` \| `split` \| `out` decided **only** on disjoint axes. |
| `voto` / `vote` | Per axis: `solo_a` \| `solo_b` \| `ambas` \| `ninguna`. All `dimension` axes vote for the audit log; only disjoint axes decide the cut. |
| `candado` / `lock` | `hoja` + disjoint axes of one pair. `published == true` iff `disjoint_count > 0`. |
| `publicar` / `publish` | Persist a `candado` as usable. Zero disjoint axes ⇒ **unpublished**. Do **not** prune shared decks to force publish. |
| `fail-closed` | Empty clause, empty splitter, unpublished lock, dead embedder, `split`/`out`, or forbidden `alma` ⇒ whole prompt/response dies. |
| `ingress` | Split prompt into clauses; one `BREACH` kills the whole prompt. |
| `egreso hold` / `hold` | Retain the full LLM generation. Zero tokens to the client until the verdict. `hold()` does not `yield`. |
| `piggyback` | Attack mixing crafts in one prompt. Isolated clauses cannot hide in a cosine average. |
| `press` | Row-by-row census of an already calibrated `rows.npz`. Does not re-embed. No `mean_*` fields. |
| `BaseEmbedder` | Sole seam: `model_id`, `dimension`, `embed_text`, `embed_batch`. |
| `FakeEmbedder` | Deterministic hash vectors. Default `pytest` path. Never loads `SentenceTransformer`. |
| `live` | A pytest marker / CLI flag that loads a real model. Off unless `--run-live` / `--live`. |
| `mean_gap` | Diagnostic only. Lives in `benchmark_models.json` and the ledger. **Never** in `press.json` or `decide()`. |
| `cosine` | Forbidden as a decision criterion. Also forbidden: centroids, `mean` of rows, top-k, INLP, whitening. |
| `trust_remote_code` | Hugging Face flag. Qwen2 adapter already sets it `True`. |
| `custom_code` | Repo ships its own Python. May break on `transformers` 5.x (Nomic already did). Treat a load crash as a **blocker**, not a geometry result. |
| `MRL` / Matryoshka | Dimensional slicing + L2 re-norm. **Qwen2 1.5B is not an MRL cut.** Full width is **1536**. Do not slice it. |
| `BGE-M3` | Frozen baseline embedder `BAAI/bge-m3`, 1024-D, MIT, ungated. |
| `Qwen2` | This campaign’s embedder. Exact id below. |

Domain glossary: [`../CONTEXT.md`](../CONTEXT.md). Contracts: [`../architecture_spec.md`](../architecture_spec.md). Invariants: [`../.agents/skills/dev-protocol/lessons-learned.md`](../.agents/skills/dev-protocol/lessons-learned.md).

---

## 2. What BGE-M3 already proved (frozen — do not re-measure to “confirm”)

Evidence dump: [`../current-research/engines/bge-m3.md`](../current-research/engines/bge-m3.md).
Ledger row: [`../current-research/embedder-ledger.md`](../current-research/embedder-ledger.md).

| Field | Value |
| :--- | :--- |
| `model_id` | `BAAI/bge-m3` |
| `dimension` | 1024 |
| `live` | yes (2026-09-19) |
| `python` n | 21 |
| `legal` n | 16 |
| `receta` n | 17 |
| `python_receta` | `published`, `disjoint_count=1`, axis **891** |
| `python_legal` | `published`, `disjoint_count=1`, axis **192** |
| `legal_receta` | `published`, `disjoint_count=7` |
| headline census | 21/21 `left` (python) and 17/17 `right` (receta) on `python_receta` |
| excluded seed | `receta-012` (syrup / *almíbar* / *hebra fina*). **Do not reintroduce.** |

Nomic / Gemma / Qwen were **not** live-measured. Their D07 table cells are blockers (transformers 5.17 / gated 401 / RAM skip), not geometry.

Do **not** edit `roadmap/archive/**`. Do **not** edit `tests/test_ddi_live.py` (it pins BGE on purpose).

---

## 3. Target embedder (exact)

| Field | Value |
| :--- | :--- |
| Hugging Face `repo_id` | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` |
| CLI aliases already in code | `qwen2`, `qwen`, full id (case-insensitive) |
| Python class | `ddi_fw.embedder.Qwen2Embedder` |
| Factory | `get_embedder("qwen2")` |
| `dimension` | **1536** (assert this; do not silently accept another width) |
| License | Apache-2.0 |
| Gated? | **No.** No Gemma license. No `HF_TOKEN` required for download. |
| Parameters | ~1.78e9 (heavy). RAM/VRAM can OOM. |
| Hub tag | `custom_code` — load may explode on `transformers` 5.17 the same way Nomic did. |
| Adapter flags today | `trust_remote_code=True`, **no** MRL `output_dim`, **no** text prefix |

Pinned stack (do not downgrade globally to “fix” Qwen): `sentence-transformers` 6.1.x → `transformers` 5.17.x.

**If load fails:** write the traceback into the Qwen engine dump + ledger `error` field. Stop the live campaign. Do **not** pin `transformers==4.*` in the root env. Do **not** swap in MiniLM / E5 / another model. Do **not** implement Deletor.

**If OOM:** same: document `memory_mb` / OSError, stop. One live embedder at a time. Never leave BGE-M3 and Qwen2 resident together.

---

## 4. Same decks, same pairs, same policy

Decks on disk (committed):

- `ddi_fw/data/python.json` — 21 clauses
- `ddi_fw/data/legal.json` — 16 clauses
- `ddi_fw/data/receta.json` — 17 clauses

Load via `load_almas()`. Spec: [`almas.md`](./almas.md).

Canonical pairs (`ddi_fw.hoja.CANONICAL_PAIRS`), `pair_id` = `{left}_{right}`:

1. `python_receta` — **headline containment pair**
2. `python_legal` — second headline
3. `legal_receta` — control pair (both forbidden under demo policy)

Demo `Policy`: `allowed=python`, `forbidden={receta,legal}`.
PASS only if **every published lock involving `python`** hard-cuts the clause to the python side.

### Absolute prohibitions on decks

- Do not `--rewrite-fixtures`.
- Do not edit `ddi_fw/almas.py` seeds.
- Do not edit `ddi_fw/data/*.json`.
- Do not reintroduce `receta-012`.
- Do not drop other clause ids to manufacture `gap > 0`.
- Zero disjoint axes on a pair is a **finding** (`published: false`), not a bug ticket against the decks.

`python -m ddi_fw.almas` rewrites fixtures from seeds. **Do not run it** in this campaign.

---

## 5. What “the same tests as BGE-M3” means

Two layers. Do not confuse them.

### Layer A — Default pytest (already green, engine-agnostic)

```bash
uv run pytest
```

Uses `FakeEmbedder` / synthetic matrices. **Do not** “port” this suite onto Qwen2. It does not load `SentenceTransformer`. Keep it green after any code change.

### Layer B — Empirical protocol (this campaign)

This is what BGE actually did live. Repeat **per engine**, recording outcomes instead of forcing BGE’s assertions.

| Step | BGE-M3 did | Qwen2 must |
| :--- | :--- | :--- |
| 1. Embed all current clauses | yes | yes, **no prune** |
| 2. Build `hoja` on all `dimension` axes | 1024 | **1536** |
| 3. Count `disjoint_axes`, list indices, `mean_gap`/`max_gap` (diagnostic) | yes | yes |
| 4. `publish` iff `disjoint_count > 0` | yes | yes; unpublished is allowed |
| 5. Persist `rows.npz` + `calibrate_audit.json` | `ddi_fw/out/` | **`ddi_fw/out/qwen2/` only** |
| 6. `press` census (`press.json`, `press.csv`) | yes | yes, from Qwen `rows.npz` |
| 7. Live pytest: all three pairs `published` | **asserted** | **record**, do not copy the assert blindly |
| 8. `ingress` on `PIGGYBACK` / `PYTHON_ONLY` / `PYTHON_PLUS_RECIPE` | geometry live if locks published | only if `python_receta` (and `python_legal` if used) are `published` |
| 9. `hold` on `PYTHON_ANSWER` vs `RECIPE_ANSWER` | same geometry | same, gated on published locks |
| 10. Optional proxy `/v1/chat/completions` | mock in unit tests; live needs Ollama | unit tests stay mocked; live proxy only if step 8 published |

Canonical strings (`tests/world.py`) — do not rewrite:

```
PY = "Explicá el funcionamiento de list.append en Python."
LEGAL = "Copiá el texto de la licencia MIT."
RECETA = "Anotá los ingredientes de la receta de la torta de chocolate."
PIGGYBACK = f"{PY} {LEGAL} {RECETA}"
PYTHON_ONLY = f"{PY} El bucle for recorre una lista en Python."
PYTHON_PLUS_RECIPE = f"{PY} Hornear el bizcochuelo a 180 grados con 200 gramos de harina."
PYTHON_ANSWER = "list.append agrega un elemento al final de la lista en Python."
RECIPE_ANSWER = "Hornear el bizcochuelo a 180 grados con 200 gramos de harina."
```

Expected **if** headline locks are published (same as BGE / Fake world):

- `PYTHON_ONLY` → `ingress` `PASS`
- `PIGGYBACK` → `ingress` `BREACH` (`ddi_ingress_breach`), **no echo** of the prompt
- `PYTHON_PLUS_RECIPE` → `BREACH`
- `hold(PYTHON_ANSWER)` → `DELIVERED` + identical text
- `hold(RECIPE_ANSWER)` and mixed recipe generation → `BLOCKED` + empty text
- HTTP: `stream=true` → 400; unpublished/dead embedder → fail-closed; no `cosine`

If a pair is unpublished, `decide()` is already fail-closed (`BREACH`). That is consistent, not a reason to prune decks. Record it.

---

## 6. Critical code trap: `calibrate()` prunes

`ddi_fw.embedder.calibrate()` **always** calls `podar_hasta_publicar` before `save_rows`. Even with `rewrite_fixtures=False` it drops rows from the saved `rows.npz` and **raises** `RuntimeError` if a pair stays unpublished.

That path certified BGE. It **must not** be the Qwen2 measurement path.

| Path | Use for Qwen2? |
| :--- | :--- |
| `uv run python -m ddi_fw.embedder --embedder qwen2 --rewrite-fixtures` | **Forbidden** |
| `calibrate(Qwen2Embedder(), rewrite_fixtures=False)` | **Forbidden** for the scientific row (silent prune + possible raise) |
| `embed_mazos` + `candados_canonicos` + `save_rows` (no prune) | **Required** primary measurement |
| `measure_embedder` in `ddi_fw/benchmark.py` | Allowed; does not prune. Extend it to also persist `rows.npz` under `out/qwen2/` if needed (Q01) |
| `uv run python -m ddi_fw.press --benchmark-all --live --models qwen2 --out ddi_fw/out/qwen2` | Allowed after Q01 isolates `--out` |

Ticket **Q01** adds an explicit no-prune persist (`measure` / `--no-prune`). Until that exists, do not call `calibrate()` on Qwen2.

---

## 7. Artifact isolation

`ddi_fw/out/` is gitignored. Still: never overwrite a BGE blob with Qwen2.

| Engine | Directory | Files |
| :--- | :--- | :--- |
| BGE-M3 (historical, if present locally) | `ddi_fw/out/` or `ddi_fw/out/bge-m3/` | `rows.npz`, `press.json`, `benchmark_models.json` |
| Qwen2 (this campaign) | `ddi_fw/out/qwen2/` | `rows.npz`, `calibrate_audit.json` (or `measure_audit.json`), `press.json`, `press.csv`, `benchmark_models.json` |
| Committed evidence | `current-research/` | ledger + engine markdown. **Not** `.npz` |

`rows.npz` keys (unchanged contract): `python`, `legal`, `receta`, `ids_*`, `texts_*`, `model_id`, `dimension`.
`model_id` must be the string `Alibaba-NLP/gte-Qwen2-1.5B-instruct`.
`dimension` must be 1536.

Do not commit `ddi_fw/out/**` or `*.npz`.

---

## 8. Geometry formulas (engine-agnostic)

For each axis `d` in `0 .. dimension-1`:

- `lo_a[d] = min(rows_a[:, d])`, `hi_a[d] = max(rows_a[:, d])` (same for `b`)
- `gap[d] > 0` iff intervals disjoint (`hi_a < lo_b` or `hi_b < lo_a`)
- `disjoint[d] = gap[d] > 0`
- `published = any(disjoint)`
- `hard cut`: empty disjoint set → `out`; any `ninguna`/`ambas` on a disjoint axis → `out`; all `solo_a` → `left`; all `solo_b` → `right`; mix → `split`

`dimension` comes from the matrix width. **Do not hardcode 1024.** Qwen2 is 1536.

---

## 9. Outcome taxonomy (use these words in the ledger)

| Outcome | Meaning | Next action |
| :--- | :--- | :--- |
| `ok_published` | Pair has `disjoint_count > 0` | Continue press + ingress/hold for headline pairs |
| `ok_unpublished` | Pair has zero disjoint axes on the **full** deck | Record axes count 0. Do **not** prune. Continue other pairs |
| `blocker_load` | Cannot instantiate/encode (`custom_code`, missing kernel, 401, etc.) | Stop live. Fill `error`. Leave geometry cells as `—` |
| `blocker_oom` | Process killed / CUDA/CPU OOM | Stop live. Record `memory_mb` if known |
| `blocker_dim` | Encoded width ≠ 1536 | Stop. Do not slice/pad to fake 1536 |
| `regression` | Default `uv run pytest` red after a code change | Fix before any more live |

BGE asserting “all three pairs published” is **not** a Qwen2 DoD. Qwen2 DoD is: Layer A green + Layer B executed + ledger row filled with one of the outcomes above.

---

## 10. Ticket order (one at a time)

| ID | Title | Live model? |
| :--- | :--- | :--- |
| [Q01](./tickets/Q01-artifact-isolation-no-prune.md) | Isolate `out/qwen2/` + no-prune measure/persist | no |
| [Q02](./tickets/Q02-qwen2-load.md) | Prove the adapter loads and encodes one string at 1536-D | yes, smoke |
| [Q03](./tickets/Q03-geometry-press.md) | Full-deck geometry + press census | yes |
| [Q04](./tickets/Q04-ingress-hold-live.md) | Ingress/hold (and optional proxy) on Qwen2 locks | yes, gated on publish |
| [Q05](./tickets/Q05-ledger-synthesis.md) | Ledger + comparison vs frozen BGE | no |

Do not start Q02 until Q01 is `hecho`.
Do not start Q04 if Q03 recorded `blocker_*` or if headline pairs are unpublished (then Q04 becomes a documented skip, still `hecho` with evidence).
Do not implement Nomic, Gemma, or Deletor (`feat/hipotesis-deletor`) in this wave.

Protocol: `.agents/skills/dev-protocol/SKILL.md`. Branch `feat/qwen2-live` (or per-ticket `feat/q01-…`). TDD. Approval gate before push/merge.

---

## 11. Copy-paste prompt for the executing agent (English)

```text
SYSTEM / TASK — ddi-fw Qwen2 live campaign
Repo: ddi-fw. Working tree: current main + this briefing.
Read first, in order:
  1. .agents/skills/dev-protocol/SKILL.md
  2. .agents/skills/dev-protocol/lessons-learned.md
  3. roadmap/00-qwen2-live.md          ← this file; it wins conflicts
  4. the single ticket you are executing (Q01 then Q02 then Q03 then Q04 then Q05)
  5. CONTEXT.md and architecture_spec.md if you touch contracts

Mission: repeat the BGE-M3 geometric protocol on Alibaba-NLP/gte-Qwen2-1.5B-instruct
(1536-D) using the existing alma decks. This is a measurement campaign.

Hard locks:
- Canonical English tokens stay in backticks; do not rename published, disjoint axis,
  fail-closed, piggyback, hold, gap, BaseEmbedder, cosine.
- Do not edit roadmap/archive/**, tests/test_ddi_live.py, ddi_fw/data/*, ddi_fw/almas.py seeds.
- Do not reintroduce receta-012. Do not run python -m ddi_fw.almas.
- Do not pass --rewrite-fixtures. Do not call calibrate() for Qwen2 (it prunes and may raise).
- Do not globally pin transformers 4.x. Do not swap in another embedder.
- Do not implement Deletor. Do not merge feat/hipotesis-deletor.
- Do not overwrite ddi_fw/out/rows.npz; Qwen2 artifacts go to ddi_fw/out/qwen2/.
- Do not commit .npz or ddi_fw/out/**.
- Default pytest (FakeEmbedder) must stay green. Live uses marker live / --run-live.
- mean_gap is diagnostic only. cosine is forbidden as a decision rule.
- Zero disjoint axes ⇒ unpublished finding, not a reason to prune mazos.
- One live embedder in process at a time.

After each ticket: fill current-research/engines/gte-qwen2-1.5b.md and append/update
ONLY the Qwen2 row in current-research/embedder-ledger.md. Never edit the BGE-M3 row.

Copyable start for Q01:
  Usando dev-protocol, ejecutá roadmap/tickets/Q01-artifact-isolation-no-prune.md
```

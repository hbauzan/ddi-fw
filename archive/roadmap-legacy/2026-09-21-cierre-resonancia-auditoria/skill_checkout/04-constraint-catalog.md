# 04 — Constraint catalog

Each ID is stable. Tickets refer to IDs, not to vibes.

Columns:

- **Layer:** A process / B product / C persona / X external (IDE catalog)
- **Bind:** what the constraint is *for*
- **MUST (in-scope):** enforce here
- **MUST NOT over-apply:** do not enforce here
- **Remediation:** what SC tickets do

---

## Product axioms (Layer B) — keep, then scope

### C-AXIOM-01 — Membership is not cosine

- **Sources:** `lessons-learned.md` (“Pertenencia = intervalos + votos, nunca Coseno”); `architecture_spec.md` `decide()`; `roadmap/00-alcance.md` “Qué no entra”.
- **Bind:** shipping verdict and lock publication.
- **MUST:** `decide()` MUST NOT take cosine, centroids, mean-of-rows, top-k, or gap-epsilon as the publication or PASS/BREACH rule. `press.json` MUST NOT grow `mean_*` fields. Publication MUST remain `disjoint_count > 0`.
- **MUST NOT over-apply:** MUST NOT refuse to edit `tools/rompepepe/` solely because it records cosine telemetry. MUST NOT refuse a `current-research/` counterfactual table labeled `diagnostic_only: cosine` that is not wired into `decide()`. MUST NOT delete existing rompepepe cosine fields “to comply with the axiom”.
- **Remediation:** SC05 adds the in-scope / out-of-scope sentences to `lessons-learned.md`.

### C-AXIOM-02 — Zero disjoint axes ⇒ do not publish; do not invent epsilon

- **Sources:** `lessons-learned.md`; `architecture_spec.md` publication; ola Q briefing.
- **Bind:** candado publication.
- **MUST:** unpublished lock stays unpublished. No `gap >= epsilon` holgura.
- **MUST NOT over-apply:** on the Qwen2 **measure** path, zero disjoint is `ok_unpublished`. MUST NOT prune shared mazos to force publication unless the human explicitly opens a mazo-curation task. `calibrate()` (which prunes) MUST NOT be the Qwen2 measurement path.
- **Remediation:** wording already in lessons; SC01 research mode must repeat this so TDD-green does not “fix” unpublished by pruning.

### C-AXIOM-03 — Hard cut vs bitácora

- **Sources:** `lessons-learned.md`; `CONTEXT.md` corte duro.
- **Bind:** label `left|right|split|out`.
- **MUST:** label is computed only on axes with `gap > 0`. All dimensions may vote for audit logs.
- **MUST NOT over-apply:** MUST NOT drop non-disjoint dimensions from stored hojas.

### C-AXIOM-04 — Fail-closed

- **Sources:** `lessons-learned.md`; proxy behavior.
- **Bind:** empty clause, empty splitter, unpublished lock, dead embedder, `split`/`out`, forbidden alma.
- **MUST:** those conditions MUST BREACH / fail the whole prompt or whole held response.
- **MUST NOT over-apply:** `/healthz` MAY report `degraded`. Research scripts MAY record unpublished without raising. Tests with `FakeEmbedder` are not “dead embedder”.

### C-AXIOM-05 — Egreso hold, no speculative streaming

- **Sources:** `lessons-learned.md`; `architecture_spec.md`; `ddi_fw/proxy.py` (`stream=true` → 400).
- **Bind:** product proxy and `hold()`.
- **MUST:** `hold()` MUST NOT yield. `stream=true` on the product proxy MUST remain 400. No token reaches the client before the verdict.
- **MUST NOT over-apply:** MUST NOT refuse a **research branch** or a **clearly named prototype** that measures latency of hold vs a hypothetical stream, if the human asked for that experiment **and** the product `hold()` / proxy contract is unchanged on `main`. MUST NOT silently add streaming to production `hold()`.
- **Remediation:** SC05 scope sentence.

### C-AXIOM-06 — 403 without echo

- **Bind:** HTTP error bodies on ingress/egreso BREACH.
- **MUST:** do not echo the blocked prompt or blocked generation.
- **MUST NOT over-apply:** tests MAY use fixture prompts. Research notes MAY quote **short** canonical piggyback text that is already in `README.md`.

### C-AXIOM-07 — Native numeric precision (cero redondeos)

- **Sources:** `cero-redondeos.md`; `SKILL.md` §2.7; `lessons-learned.md`; `CONTEXT.md`.
- **Bind:** tensors, coordinates, intervals, metrics that feed science or the lock.
- **MUST:** no `round()`, no `f"{x:.6f}"` / `:.2f` as the **stored or exported scientific value**. Use native float32/float64 representation (`:.9g` / `:.17g` / `Decimal` / `str(float)` as specified in `cero-redondeos.md`). If a dump would threaten machine stability, **stop and ask**; do not silently truncate.
- **MUST NOT over-apply:** a **display-only** plot or markdown table MAY round **display digits** if and only if (a) the source artifact keeps full precision, and (b) the caption/header says `display-only rounding; source unrounded`. Integer axis **indices** (891, 192, 660) are integers, not truncated floats. Percent in a **human** sentence about Jaccard MAY be written `Jaccard < 0.05` because that **is** the threshold contract, not a rounded measurement dump.
- **Remediation:** SC05; collapse duplicate essays to a pointer.

### C-AXIOM-08 — Embedder seam and test determinism

- **Sources:** `SKILL.md` §3.2; `lessons-learned.md`; `architecture_spec.md`.
- **MUST:** all vectors through `BaseEmbedder`. Default tests use `FakeEmbedder` or synthetic matrices. Live tests carry an explicit `live` marker. Default pytest MUST NOT load SentenceTransformer.
- **MUST NOT over-apply:** MUST NOT refuse `--run-live` or a documented live measurement when the human asked. MUST NOT treat Hugging Face Hub download of a **pinned** model id as “forbidden live LLM call”. Embeddings are not chat sampling; pin model id + weights.

### C-AXIOM-09 — `mean_gap` is diagnostic only

- **MUST:** `mean_gap` lives in `benchmark_models.json` (D07). Not in `press.json`. Not in `decide()`.
- **MUST NOT over-apply:** other **named diagnostic** scalars MAY exist in `current-research/` markdown. They MUST NOT enter `decide()`.

### C-AXIOM-10 — Mazos, Jaccard, vetos, canonical pairs

- **MUST:** keep decks small; Jaccard < 0.05 on canonical pairs is the isolation target; vetos in `classify.py` are surgical; pair ids are the documented 10 pairs; functions tolerate missing almas in a bundle.
- **MUST NOT over-apply:** a new alma that **fails** Jaccard is a **curation task**, not a reason to refuse the alma forever. MUST NOT add a veto that collides with another alma’s legitimate lexicon.

### C-AXIOM-11 — Secrets, artifacts, uv

- **MUST:** secrets only in `.env` (gitignored); `.env.example` is the committed template. `ddi_fw/out/` gitignored; textual fixtures in `ddi_fw/data/` are committed. Python via `uv`, not ad-hoc `pip` + random venv. On macOS host, `UV_CACHE_DIR=/tmp/uv-cache` when cache permission locks appear.
- **MUST NOT over-apply:** MUST NOT refuse a one-off `uv add` of a documented dependency. MUST NOT commit `.npz` under `ddi_fw/out/`.

### C-AXIOM-12 — One live embedder resident at a time

- **MUST:** load, measure, release. Do not leave BGE-M3 and Qwen2 1.5B in RAM together.
- **MUST NOT over-apply:** sequential A/B in one session is allowed. Parallel process isolation is allowed if RAM is proven.

### C-AXIOM-13 — BGE-M3 product pin; Qwen2 is measured, not the default

- **MUST:** product pin stays `BAAI/bge-m3` unless a later human-approved campaign changes it. Qwen2 live 2026-09-19: encode OK; headline pairs `ok_unpublished`; do not pin `transformers==4.*`; do not use `calibrate()` for Qwen2 measure path; do not write Qwen2 into `ddi_fw/out/rows.npz`.
- **MUST NOT over-apply:** MUST NOT refuse to **run** Qwen2 measurement. MUST NOT rewrite the frozen BGE ledger row.

### C-AXIOM-14 — Deletor branch is parked

- **MUST NOT** merge `feat/hipotesis-deletor` onto `main` as a side effect of skill work or Q-wave work.
- **MUST NOT over-apply:** reading that branch when the human names it is allowed.

### C-AXIOM-15 — `python -m ddi_fw.almas` rewrites fixtures

- **MUST:** seeds must match the pruned deck. A bridge seed (`receta-012` almíbar) MUST NOT be reintroduced.
- **MUST NOT over-apply:** research copies of decks under `ddi_fw/out/` or a dedicated research dir MAY experiment; committed `ddi_fw/data/` MUST stay clean.

---

## Process constraints (Layer A) — keep for release mode, scope for research mode

### C-PROC-01 — Canonical protocol phrase starts full delivery

- **Source:** `SKILL.md` §0.
- **MUST:** when the user uses `Usando dev-protocol` / `Using dev-protocol` **or** explicitly executes a ticket that says to follow the protocol, run the cycle including tests and the approval gate.
- **MUST NOT:** run push/merge without explicit human go-ahead. MUST NOT assume the phrase from a vague “please look at”.

### C-PROC-02 — Ask when ambiguous; do not guess contracts

- **MUST:** if a **product contract** is ambiguous (HTTP shape, publication rule, allowed alma), ask before coding.
- **MUST NOT over-apply:** in research mode, forming a **falsifiable hypothesis** is required work, not “guessing the architecture”. Do not block measurement because the result is unknown.

### C-PROC-03 — Branch before product-code edits

- **SHOULD:** dedicated branch `type/short-name` before editing `ddi_fw/**`.
- **MUST NOT over-apply:** adding markdown under `roadmap/skill_checkout/` (this pack) did not require a protocol-owned git delivery. Successor agent: follow SC06.

### C-PROC-04 — TDD vertical slices

- **Source:** `code-design.md`.
- **MUST (release mode):** behavior change to `decide` / `hold` / proxy / splitter / publication: one failing test through the public seam, then minimal code, then green, then refactor.
- **MUST NOT (research mode):** require red-green before writing a ledger paragraph, running `--no-prune`, or adding a measurement script that does not change product verdict code.
- **Remediation:** SC02.

### C-PROC-05 — Debug: no code reading until red-capable command

- **Source:** `debugging.md` Phase 1 last bullet. Quote: “Do not jump to hypotheses or read code to build a theory before this command exists. No red-capable command, no Phase 2.”
- **MUST (release mode, ordinary product bug with HTTP/CLI symptom):** still build a tight loop.
- **MUST NOT (research / geometry / embedder-load / unpublished lock):** forbid reading `decide()`, adapters, mazos, `lessons-learned.md`, and the ledger **first**. Those files **are** the loop.
- **Remediation:** SC02 adds an explicit exception list.

### C-PROC-06 — Debug Phase 3: show hypotheses to the user before testing

- **SHOULD:** when the user is present and the bug is product-side.
- **MUST NOT over-apply:** if the user is AFK, `debugging.md` already allows testing the top hypothesis. Research mode MAY test hypotheses without a theatrical pause.

### C-PROC-07 — Documentation sync is conditional

- **MUST:** follow `documentation.md` tables. Do not touch every doc on every micro-fix.
- **MUST NOT:** dump measurement tables into `lessons-learned.md`. Numbers go to `current-research/`.

### C-PROC-08 — Two-axis review via parallel sub-agents

- **SHOULD:** for merge-sized product diffs.
- **MUST NOT over-apply:** not required for this markdown pack or for a one-line lessons pointer.

### C-PROC-09 — Issues describe behavior, not line numbers

- **SHOULD:** for durable tracker issues.
- **MUST NOT over-apply:** this pack and SC tickets MUST contain file paths. Paths are the point.

### C-PROC-10 — Approval gate for push and merge

- **MUST:** keep. Silence is not approval.
- **Remediation:** SC06 does not remove this.

### C-PROC-11 — Local commits “free at any time”

- **Source:** `git-workflow.md` §3.1 “freely create branches, stage, commit locally”.
- **Conflict:** many Cursor user rules say commit only when the human asked.
- **Remediation:** SC06 — commits happen only if (a) the human asked to commit, or (b) the human invoked the canonical protocol phrase **and** the ticket says the agent owns local commits. Default for skill_checkout implementation: **do not commit unless asked**.

### C-PROC-12 — Default delivery is merge to `main`

- **Source:** `git-workflow.md` §3.2 step 5.
- **Conflict:** other instructions prefer `gh pr create`.
- **Remediation:** SC06 — default to PR if `origin` is GitHub and the human did not say “merge to main”. Always wait for approval before push. Never force-push `main`.

### C-PROC-13 — Toolchain `uv` / ruff

- **MUST:** keep for Python in this repo.
- **MUST NOT over-apply:** MUST NOT run `pip install` “because an HF skill said so”.

---

## Persona constraints (Layer C) — demote

### C-PERSONA-01 — Mandatory Murray identity

- **Sources:** `SKILL.md` §1; `estilo-comunicacion.md`; `murray.md`.
- **Current bind:** every response.
- **Target bind:** only when the human asks for Murray, or when a future non-default rule is enabled.
- **MUST after remediation:** technical density, no chatbot filler, no `# TODO`, rioplatense **if the user writes Spanish**.
- **MUST NOT:** require sandwich, quote quotas, or “Tiembla ante Murray” on research or implementation answers.
- **Remediation:** SC03.

### C-PERSONA-02 — 50/30/20 Monkey Island quote mix + 14-insult matrix

- **Tax:** large. `murray.md` is ~144 lines of lore.
- **Remediation:** keep the file as optional flavor. Do not load it in the always-on router.

### C-PERSONA-03 — Theatrical Conventional Commits

- **Remediation:** SC06. Message format `type(scope): factual summary`. Theater optional, never required.

### C-PERSONA-04 — “If it is closed, do not reopen”

- **Source:** `estilo-comunicacion.md` interlocutor profile.
- **Defect:** fuses closed **verdict architecture** with closed **measurement**.
- **Remediation:** SC03 + SC01. Replace with the two-sentence split in [00-glossary.md](./00-glossary.md) “Closed architecture vs closed measurement”.

---

## External catalog (Layer X)

### C-EXT-01 — Hugging Face plugin skills in Cursor

- **Bind:** none, for ddi-fw default work.
- **MUST:** first reads are spec + lessons + ticket + `uv`.
- **MUST NOT:** start HF Jobs/Spaces/TRL because the task mentions embeddings.
- **Remediation:** one paragraph in `SKILL.md` §3. Not a new skill.

### C-EXT-01 note — Canvas / visualize Cursor skills

- MAY use if the human asked for a chart.
- MUST NOT delay geometry work to build a canvas unless asked.

---

## Drift (not a constraint, a bug)

### C-DRIFT-01 — Phantom files in USAGE.md

- **Remediation:** SC04.

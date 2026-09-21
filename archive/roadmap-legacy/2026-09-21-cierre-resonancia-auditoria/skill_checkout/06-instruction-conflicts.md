# 06 — Instruction conflicts

When two documents disagree, a successor agent MUST use this file’s **resolution**, not a coin flip.

---

## 06.1 Git: three constitutions

| Source | What it says |
| :--- | :--- |
| `git-workflow.md` §3 | Agent owns lifecycle. Local commit is free. Push/merge after explicit ok. Default: merge to `main`. |
| `SKILL.md` §0 steps 7–8 | Wait for approval; then commit → push branch → merge base → push base. |
| Typical Cursor user rule (not in this repo) | Do not commit unless the human asked. Do not push unless asked. Prefer `gh pr create`. Never `--no-verify`. |

**Resolution (SC06, become repo law):**

1. **Push and merge** MUST wait for explicit human go-ahead. Words like `ok`, `dale`, `andá`, `mergealo`, `push`, `create the PR` count. Silence does not.
2. **Commit** MUST wait for (a) explicit `commit` / `commiteá` / `hace el commit`, **or** (b) the canonical protocol phrase **and** a ticket that states “local commits are in scope”. Creating this analysis folder was (neither); do not commit it unless asked.
3. **Default remote integration** is `gh pr create` when `origin` is GitHub. Direct merge to `main` only if the human says so.
4. Destructive git (reset --hard, clean -fd, force-push, rewrite pushed history) still requires a separate explicit yes.
5. Commit message: Conventional Commit, fact-first. Murray flavor MUST NOT be required.

Until SC06 is applied, a successor agent implementing **this pack’s tickets** MUST follow (1)–(5) anyway, because [09-execution-spec.md](./09-execution-spec.md) says so.

---

## 06.2 Communication: Murray vs IDE vs this pack

| Source | What it says |
| :--- | :--- |
| `SKILL.md` §2 + `estilo-comunicacion.md` | Mandatory sandwich, quote rotation, close with supremacy. |
| Cursor system communication | Complete sentences, lead with the answer, spare formatting, no theatrical opener. |
| This pack | English, RFC 2119, no persona. |

**Resolution:** documents in `roadmap/skill_checkout/` are written in the pack register (English, cold). After SC03, agent chat follows the **user’s language** (Spanish rioplatense if they write Spanish) with density rules, **without** mandatory Murray. If the user says “hablá como Murray”, Layer C turns on for that thread.

Do not spend tokens reconciling pirate quotes with RFC 2119 while editing skills.

---

## 06.3 Cosine: product vs rompepepe vs research

| Source | What it says |
| :--- | :--- |
| Layer B axioms | Cosine is not membership. |
| `tools/rompepepe/` | Cosine appears as telemetry / search dimension. |
| Humans comparing piggyback | Want a counterfactual: averaged cosine misses mixed-oficio; clauses + intervals do not. |

**Resolution:** C-AXIOM-01 in [04-constraint-catalog.md](./04-constraint-catalog.md). `decide()` stays cosine-free. Telemetry and labeled diagnostics may exist **outside** `decide()` / `press.json` publication fields.

A successor agent MUST NOT “cleanse” rompepepe of cosine as part of skill_checkout.

---

## 06.4 `calibrate()` vs `--no-prune`

| Source | What it says |
| :--- | :--- |
| Generic TDD instinct | Make the lock publish (green). |
| `lessons-learned.md` ola Q | `calibrate()` prunes; Qwen2 path is `measure_and_save`; zero disjoint is `ok_unpublished`. |

**Resolution:** product-code tickets that **intend** publication on the BGE path MAY use `calibrate()`. Measurement of a candidate embedder MUST NOT. Research mode exists to make this mechanical.

---

## 06.5 Default tests vs live models

| Source | What it says |
| :--- | :--- |
| `SKILL.md` §3.2 / architecture_spec | Default tests never call live models. |
| README | `uv run pytest --run-live tests/test_ddi_live.py` exists. |

**Resolution:** default `uv run pytest` stays fake. Live is opt-in. Research mode **may and should** run live when the ticket says live. Skipping live because “the skill forbids models” is over-application of C-AXIOM-08.

---

## 06.6 Progressive disclosure vs always-Murray vs always-lessons

| Source | What it says |
| :--- | :--- |
| `SKILL.md` §4 | Load modules only when needed. |
| `SKILL.md` §1–2 | Always be Murray (large). |
| `lessons-learned.md` §4 | Always read this file before code. |

**Resolution:** keep “always read `lessons-learned.md`” for any task that can break geometry or security. Stop always-loading `murray.md`. SKILL.md router stays small. SC03.

---

## 06.7 USAGE.md vs disk

**Resolution:** disk wins. SC04. Do not recreate a theater of missing files.

---

## 06.8 qa-review “no file paths in issues” vs this pack

**Resolution:** tracker issues for **product bugs** SHOULD avoid brittle line numbers. Agent-protocol tickets in this folder MUST use paths. This pack is not a GitHub issue.

---

## 06.9 Hugging Face skills vs `uv`

**Resolution:** C-EXT-01. Downloading a pinned model from the Hub as the adapter already does is allowed. Starting a training job or Space is out of scope unless the human named that product.

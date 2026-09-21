# 09 — Execution spec for the successor agent

This file is the **contract** if the human says: implement skill_checkout tickets.

If the human has **not** said that, you MUST NOT edit `.agents/` even if you have read this file. Writing this folder was a documentation task. Implementing SC01–SC06 is a later task.

---

## 9.1 Preconditions

1. Read [README.md](./README.md) hard non-goals.
2. Read [08-recommended-remediation.md](./08-recommended-remediation.md) file-ownership table.
3. Classify **this** implementation work as **release-mode process change**, not research-mode geometry, and not product-code. You are editing agent instructions only.
4. TDD is **not** applicable (no `ddi_fw/` behavior). Verification is the checklist in §9.5.
5. Do not run Hugging Face trainer/spaces skills.

---

## 9.2 Git (applies even before SC06 lands)

MUST NOT `git commit` unless the human explicitly asks to commit.

MUST NOT `git push` or merge unless the human explicitly asks.

MUST NOT `--no-verify`, force-push, or rewrite pushed history.

SHOULD work on a branch `docs/skill-checkout-remediation` (or `chore/skill-checkout-sc01` per ticket) **if** you edit `.agents/`. Creating the analysis markdown may already be on the human’s current branch; do not juggle branches unless asked.

If you find unrelated dirty files, leave them unstaged.

---

## 9.3 How to execute tickets

- One ticket per diff unless the human says “do SC01–SC06 together”.
- Copy the “Copiable prompt” from the ticket into your own working notes; follow it literally.
- When 08 and a ticket conflict, **ticket + 08 together**: the ticket is the slice; 08 is the wording. Do not invent extra files.
- Match the **existing language** of the file you edit (Spanish vs English). Inserted MUST/MUST NOT in English is allowed inside an otherwise Spanish file only for the tokens `release` and `research`.
- Do not add `# TODO`.
- Do not leave duplicate contradictory sentences (e.g. “Murray is mandatory” and “Murray is optional” in the same file). After SC03, grep for `Obligatoria` / `mandatory` next to Murray and sandwich.

---

## 9.4 Commands that count as verification

From repo root:

```bash
# 1. Phantom names must not be claimed as existing unless the file exists.
# After SC04, these greps on USAGE.md should not assert existence of missing paths.
rg -n 'grilling|_archive|UBIQUITOUS_LANGUAGE|docs/dev-protocol' .agents/skills/dev-protocol/USAGE.md

# 2. Mode tokens exist in the router after SC01.
rg -n 'research mode|Modos de agente|`research`' .agents/skills/dev-protocol/SKILL.md

# 3. Debug exception exists after SC02.
rg -n 'Exception: research' .agents/skills/dev-protocol/debugging.md

# 4. TDD scope exists after SC02.
rg -n 'When TDD is mandatory' .agents/skills/dev-protocol/code-design.md

# 5. Cosine scope sentence exists after SC05.
rg -n 'rompepepe|contrafactual|counterfactual' .agents/skills/dev-protocol/lessons-learned.md

# 6. Git commits not free after SC06.
rg -n 'freely' .agents/skills/dev-protocol/git-workflow.md
# The word "freely" MUST NOT still describe local commits.

# 7. Product code untouched
git diff --stat -- ddi_fw/
# MUST be empty for skill_checkout work.

# 8. Default tests still green (you did not touch them, but run once if the environment allows)
UV_CACHE_DIR=/tmp/uv-cache uv run pytest
```

Do not fail the task if pytest cannot run for unrelated environment reasons; report it. Do fail the task if `ddi_fw/` diff is non-empty.

---

## 9.5 Acceptance checklist (all tickets)

- [ ] `ddi_fw/**` diff empty
- [ ] `roadmap/archive/**` untouched
- [ ] BGE ledger row untouched
- [ ] Product axioms still present (cosine-not-verdict, fail-closed, hold no yield, native precision, BGE pin, Deletor parked)
- [ ] Each axiom that was over-applicable now has an **in-scope / out-of-scope** sentence where SC05 required it
- [ ] `SKILL.md` classifies `release` vs `research` before TDD/debug
- [ ] `debugging.md` Phase 1 prohibition is scoped; research exception present
- [ ] `code-design.md` states TDD not mandatory for ledger/measure
- [ ] Murray not mandatory; `murray.md` header says optional
- [ ] “do not reopen” split into verdict vs measurement
- [ ] USAGE.md does not claim phantom files; Cursor path is `.agents/skills/dev-protocol/SKILL.md`
- [ ] git-workflow does not say local commits are free
- [ ] approval gate for push/merge still present
- [ ] `lessons-learned.md` did not gain measurement tables
- [ ] OA-01…OA-20 in [07-overapplication-risks.md](./07-overapplication-risks.md) would not still fire from a literal reading

---

## 9.6 What to say to the human when a ticket is done

Report:

1. Files changed (paths)
2. Files deliberately not changed
3. Grep results from §9.4
4. Residual risk (e.g. Cursor may still index HF plugin skills; that is outside the repo)
5. Wait. Do not push.

---

## 9.7 Residual risks this pack cannot fix inside `.agents/`

1. Cursor `available_skills` still lists Hugging Face plugins. Operator action: do not attach that plugin to this workspace, or ignore those skills unless named.
2. User-level Cursor rules may still mandate Murray or git behavior. Repo files cannot override a user rule that is always injected. If conflict remains after SC06, tell the human which user rule is winning.
3. Load path without `AGENTS.md` remains inconsistent across IDEs. That is acceptable under SC04 default.

---

## 9.8 Forbidden “helpful extras”

MUST NOT, while implementing tickets:

- Rewrite `roadmap/00-alcance.md` or Q-tickets
- Add a new skill directory
- Translate the entire `dev-protocol` into English
- Delete `murray.md`
- Merge SC tickets with an unrelated formatter pass on the whole repo
- “Improve” `lessons-learned.md` Qwen2 numbers
- Run live embedders

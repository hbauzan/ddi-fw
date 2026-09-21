# SC01 — Add release vs research mode router to SKILL.md

> **Estado:** aplicado (2026-09-19)
> **Kind:** agent-protocol (not a product wave)
> **Depends on:** `roadmap/skill_checkout/` analysis
> **Touches:** `.agents/skills/dev-protocol/SKILL.md` only
> **Live model:** no

---

## Objective

Make the skill classify work as `release` or `research` **before** TDD or the six-phase debug loop. Preserve all product axioms as “always”.

## Why

`SKILL.md` currently implies every implementation task is a closed product ticket. ddi-fw also does geometry measurement (`--no-prune`, unpublished locks, ledgers). Without a mode router, a literalist agent prunes mazos or refuses to read code.

Normative design: [`../08-recommended-remediation.md`](../08-recommended-remediation.md) §8.1 and [`../05-research-vs-release-mismatch.md`](../05-research-vs-release-mismatch.md) §5.4–§5.6.

## Allowed edits

**File:** `.agents/skills/dev-protocol/SKILL.md`

- Insert the Spanish section `## Modos de agente (release vs research)` from 08 §8.1 immediately after the module index and before `# 0. Flujo principal`.
- Keep `release` and `research` as English tokens.
- Point to `roadmap/skill_checkout/05-research-vs-release-mismatch.md` for the detection table. Do not paste the entire table if it bloats the router; the section in 08 is the required payload.
- Add under §3.2 (LLM integrations) one sentence: Hub may supply a **pinned** adapter model; HF Jobs/Spaces/TRL/ZeroGPU are not the default toolchain; do not open those skills first for ddi-fw work.

## Forbidden edits

- Do not demote Murray in this ticket (that is SC03).
- Do not edit `debugging.md` or `code-design.md` (SC02).
- Do not delete lessons, fail-closed, `uv`, or the approval gate in §0.
- Do not create a second skill directory.
- Do not edit `ddi_fw/**`.

## Definition of Done

- [ ] `SKILL.md` contains both tokens `` `release` `` and `` `research` `` in a mode section.
- [ ] “Siempre (ambos modos)” lists: `uv`, secrets, no cosine-as-verdict, native precision pointer, product hold/fail-closed, fake default tests, no sneaky Deletor merge, no push without OK.
- [ ] `research` paragraph forbids greening unpublished via shared-mazo prune or epsilon, and forbids `calibrate()` as the Qwen2 measure path.
- [ ] `release` paragraph still points at TDD + debug modules.
- [ ] Ambiguous case: ask once, release or research.
- [ ] Mixed case: split the work.
- [ ] `git diff -- ddi_fw/` empty

## Copiable prompt

```text
Execute roadmap/skill_checkout/tickets/SC01-mode-router.md.
Read roadmap/skill_checkout/09-execution-spec.md and 08-recommended-remediation.md §8.1 first.
Edit only .agents/skills/dev-protocol/SKILL.md.
Insert the agent-modes section (tokens release and research) as specified.
Do not demote Murray (SC03). Do not touch ddi_fw/. Do not commit unless I ask.
```

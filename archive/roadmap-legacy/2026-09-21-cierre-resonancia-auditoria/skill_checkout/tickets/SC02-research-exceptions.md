# SC02 — Research exceptions in debugging.md and code-design.md

> **Estado:** aplicado (2026-09-19)
> **Depends on:** SC01 (mode names must already exist in SKILL.md)
> **Touches:** `.agents/skills/dev-protocol/debugging.md`, `.agents/skills/dev-protocol/code-design.md`
> **Live model:** no

---

## Objective

Keep the six-phase debug loop and TDD for **release** product bugs. Stop them from forbidding code-reading and red-green ritual on **research** geometry work.

Normative text: [`../08-recommended-remediation.md`](../08-recommended-remediation.md) §8.2 and §8.3.

IDs: C-PROC-04, C-PROC-05 in [`../04-constraint-catalog.md`](../04-constraint-catalog.md). Acceptance: OA-03, OA-04, OA-05, OA-11 in [`../07-overapplication-risks.md`](../07-overapplication-risks.md).

## Allowed edits

### `debugging.md`

- Keep Phase 1 including the original prohibited-action bullet.
- Add subsection `### 1.3 Exception: research / geometry / embedder-load (research mode)` using the English payload in 08 §8.2 (this file is already English).
- The exception MUST name: unpublished / zero disjoint; live load/shims/401/custom_code; Jaccard/veto; ledger; “why did model Y not publish?”.
- The exception MUST say measurement commands **are** the loop.
- The exception MUST NOT apply to proxy 500 / wrong HTTP code.

### `code-design.md`

- Keep deep modules, deletion test, two-adapters-real-seam, vertical slices.
- Insert `## When TDD is mandatory vs not` from 08 §8.3 near the top.
- Explicit: if research starts editing `decide()`, that diff is release mode.

## Forbidden edits

- Do not delete the six phases.
- Do not say “never use TDD in this repo”.
- Do not edit `SKILL.md` in this ticket.
- Do not edit `ddi_fw/**`.

## Definition of Done

- [ ] `rg 'Exception: research' .agents/skills/dev-protocol/debugging.md` matches
- [ ] `rg 'When TDD is mandatory' .agents/skills/dev-protocol/code-design.md` matches
- [ ] Original “No red-capable command, no Phase 2” sentence still exists (scoped, not deleted)
- [ ] `git diff -- ddi_fw/` empty

## Copiable prompt

```text
Execute roadmap/skill_checkout/tickets/SC02-research-exceptions.md.
Read roadmap/skill_checkout/08-recommended-remediation.md §8.2 and §8.3.
Edit only debugging.md and code-design.md under .agents/skills/dev-protocol/.
Scope TDD and the debug Phase 1 code-reading ban to release mode; add the research exception lists verbatim in meaning.
Do not touch SKILL.md, ddi_fw/, or git commit unless I ask.
```

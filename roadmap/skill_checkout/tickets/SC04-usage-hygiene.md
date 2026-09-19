# SC04 — USAGE.md hygiene (stop claiming phantom files)

> **Estado:** aplicado (2026-09-19)
> **Depends on:** none
> **Touches:** `.agents/skills/dev-protocol/USAGE.md` only
> **Live model:** no

---

## Objective

USAGE.md MUST describe the disk. Phantom files cause agents to recreate empty theater (`grilling`, `_archive`, `AGENTS.md`, `UBIQUITOUS_LANGUAGE.md`, `docs/dev-protocol/`).

Evidence: [`../02-inventory-and-load-path.md`](../02-inventory-and-load-path.md). Wording: [`../08-recommended-remediation.md`](../08-recommended-remediation.md) §8.6.

ID: C-DRIFT-01.

## Allowed edits

In `USAGE.md`:

1. Do not state that `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` **exist** in this repo unless you have just created them. Default: **do not create them**. Say they are optional pointers some IDEs use, and that this clone’s source of truth is `.agents/skills/dev-protocol/SKILL.md`.
2. Remove `grilling` as a present skill. Say it is not in this clone; do not `ln -s` a missing path.
3. Remove `_archive/` as a present directory.
4. Replace `UBIQUITOUS_LANGUAGE.md` with `CONTEXT.md`.
5. Cursor example path MUST be `.agents/skills/dev-protocol/SKILL.md`, not `docs/dev-protocol/SKILL.md`.
6. Keep the warning about Cursor indexing a huge global `~/.agents/skills` catalog (true and useful).
7. Keep `./scripts/setup-skills.sh` only if that script **exists** on disk. If it does not exist, stop telling agents to run it.

## Forbidden edits

- Do not create `grilling`, `_archive`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `UBIQUITOUS_LANGUAGE.md`, or `docs/dev-protocol/` in this ticket.
- Do not edit `SKILL.md`.
- Do not edit `ddi_fw/**`.

## Definition of Done

- [ ] `USAGE.md` does not claim missing files as present
- [ ] Cursor path uses `.agents/skills/dev-protocol/SKILL.md`
- [ ] Domain glossary named `CONTEXT.md`
- [ ] No instruction to symlink `.agents/skills/grilling` unless that directory exists
- [ ] `git diff -- ddi_fw/` empty

## Copiable prompt

```text
Execute roadmap/skill_checkout/tickets/SC04-usage-hygiene.md.
Read roadmap/skill_checkout/02-inventory-and-load-path.md.
Edit only .agents/skills/dev-protocol/USAGE.md so it matches the disk.
Do not create phantom files. Do not symlink missing skills. Do not touch ddi_fw/. Do not commit unless I ask.
```

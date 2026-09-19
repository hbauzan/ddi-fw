# SC06 — One git constitution

> **Estado:** aplicado (2026-09-19)
> **Depends on:** none
> **Touches:** `.agents/skills/dev-protocol/git-workflow.md` only
> **Live model:** no

---

## Objective

Stop the agent from committing unasked and from merging `main` by default, while **keeping** the push/merge approval gate and the destructive-command list.

Conflict evidence: [`../06-instruction-conflicts.md`](../06-instruction-conflicts.md) §06.1. Wording: [`../08-recommended-remediation.md`](../08-recommended-remediation.md) §8.7.

IDs: C-PROC-10, C-PROC-11, C-PROC-12, C-PERSONA-03. Acceptance: OA-15.

## Allowed edits

In `git-workflow.md`:

1. **§3.1** MUST NOT say the agent may “freely” commit locally. New rule:
   - Create a feature branch when editing product or protocol code, unless the human said to stay on the current branch.
   - `git commit` only if the human asked to commit **or** used the canonical protocol phrase **and** the current ticket says local commits are in scope.
   - `git push` and merge to base still require a **separate** explicit go-ahead. Silence is not approval.
2. **§3.2** default remote integration: `git push -u origin HEAD` then `gh pr create` when `origin` is GitHub. Direct `merge` to `main` only if the human said to merge `main`.
3. **§1** commit messages: Conventional Commits, factual summary of **why**. Murray/sarcasm is **optional**, never required. Do not require a YAML metadata block at the end of every chat response.
4. Keep §3.3 stop-and-ask and §3.4 destructive list unchanged in meaning.
5. Keep Co-Authored-By trailer only if the surrounding project already uses it; do not invent a new trailer policy. If the file currently requires it, you MAY keep it for commits the human requested.

## Forbidden edits

- Do not remove the approval gate.
- Do not authorize `--no-verify`, force-push, or `reset --hard` without explicit yes.
- Do not edit global git config.
- Do not commit this ticket’s diff unless asked.
- Do not edit `ddi_fw/**`.

## Definition of Done

- [ ] `rg -n 'freely' .agents/skills/dev-protocol/git-workflow.md` does **not** describe local commits as free
- [ ] push/merge still blocked on explicit user go-ahead
- [ ] PR-default vs merge-to-main is explicit
- [ ] theatrical commits not required
- [ ] destructive list still present
- [ ] `git diff -- ddi_fw/` empty

## Copiable prompt

```text
Execute roadmap/skill_checkout/tickets/SC06-git-constitution.md.
Read roadmap/skill_checkout/06-instruction-conflicts.md §06.1 and 08-recommended-remediation.md §8.7.
Edit only git-workflow.md. Commits are not free by default. Keep the push/merge approval gate. Prefer gh pr create unless I asked to merge main. Factual Conventional Commits; Murray flavor optional.
Do not touch ddi_fw/. Do not commit unless I ask.
```

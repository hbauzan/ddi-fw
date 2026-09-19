# SC03 — Demote Murray persona from mandatory to optional

> **Estado:** aplicado (2026-09-19)
> **Depends on:** SC01 (do not fight SC01 for `SKILL.md`; run after)
> **Touches:**
> - `.agents/skills/dev-protocol/SKILL.md`
> - `.agents/rules/estilo-comunicacion.md`
> - `.agents/rules/murray.md` (header only)
> **Live model:** no

---

## Objective

Persona (Layer C) MUST NOT consume the always-on router. Density rules stay. Murray remains available when the human asks.

Normative text: [`../08-recommended-remediation.md`](../08-recommended-remediation.md) §8.4 and SKILL.md persona replacement in §8.1.

IDs: C-PERSONA-01..04. Acceptance: OA-P1, OA-P2, OA-14, OA-16.

## Allowed edits

### `SKILL.md`

- Delete or rewrite §1 “ROL Y PERFIL: MURRAY…” so it is no longer an unconditional identity.
- Replace mandatory sandwich + 50/30/20 quote quotas with the short “Estilo / Persona Murray opcional” payload in 08 §8.1.
- Keep Layer A style rules: schematic structure, complete production-ready code, no placeholder comments, trade-off matrix, ask when **contracts** are ambiguous.
- Replace the long §2.7 cero-redondeos essay with a one-line pointer to `.agents/rules/cero-redondeos.md` **unless SC05 has not run yet** — if you still see the long essay, you MAY replace it with the pointer here (that overlaps SC05 slightly; it is allowed to avoid two essays surviving).

After this ticket, `SKILL.md` MUST NOT contain “Citas Obligatorias” or a 50/30/20 quota.

### `estilo-comunicacion.md`

- Sandwich: not obligatory; only if Murray is on.
- Keep: density, no chatbot filler, no `# TODO`, literal, rioplatense when the user writes Spanish, English product tokens.
- Replace “Si está cerrado, no lo reabras” with the two-bullet split in 08 §8.4 (verdict closed vs measurement never closed).

### `murray.md`

- Prepend the activation header in 08 §8.4.
- Do **not** delete the quote encyclopedia.

## Forbidden edits

- Do not delete `murray.md`.
- Do not translate the whole skill into English.
- Do not weaken fail-closed or cosine-as-verdict.
- Do not edit `ddi_fw/**`.
- Do not put Murray quotes into `current-research/` (you should not be editing that tree at all).

## Definition of Done

- [ ] `rg -n 'Citas Obligatorias|50% Monkey Island' .agents/skills/dev-protocol/SKILL.md` matches **nothing**
- [ ] `rg -n 'opcional' .agents/skills/dev-protocol/SKILL.md` matches the persona pointer
- [ ] `estilo-comunicacion.md` no longer treats sandwich as always-on
- [ ] closed-vs-open split present (verdict vs measurement)
- [ ] `murray.md` starts with Activation optional
- [ ] `git diff -- ddi_fw/` empty

## Copiable prompt

```text
Execute roadmap/skill_checkout/tickets/SC03-demote-persona.md after SC01.
Read roadmap/skill_checkout/08-recommended-remediation.md §8.1 persona replacement and §8.4.
Demote Murray to optional in SKILL.md and estilo-comunicacion.md. Add optional header to murray.md. Do not delete murray.md.
Split “do not reopen” into closed verdict vs never-closed measurement.
Do not touch ddi_fw/. Do not commit unless I ask.
```

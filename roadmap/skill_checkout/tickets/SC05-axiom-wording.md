# SC05 — Narrow axiom wording (cosine, hold, rounding) without weakening the product

> **Estado:** aplicado (2026-09-19)
> **Depends on:** SC01 recommended (modes exist so lessons can point at them)
> **Touches:**
> - `.agents/skills/dev-protocol/lessons-learned.md`
> - `.agents/rules/cero-redondeos.md`
> - `.agents/skills/dev-protocol/SKILL.md` only if the long cero-redondeos essay is still in §2.7
> **Live model:** no

---

## Objective

Product axioms stay **true**. Literalist over-application (OA-01, OA-02, OA-08, OA-09, OA-17) must stop.

Normative text: [`../08-recommended-remediation.md`](../08-recommended-remediation.md) §8.5. Catalog: C-AXIOM-01, C-AXIOM-05, C-AXIOM-07, C-AXIOM-09.

## Allowed edits

### `lessons-learned.md`

- **Do not delete** existing bullets (cosine-not-verdict, zero disjoint, fail-closed, hold, 403, seam, BGE pin, Qwen2 notes, Deletor parked, uv, etc.).
- Add the **Alcance** sentence to the cosine bullet: verdict + publication only; out of scope: `tools/rompepepe/` telemetry, `current-research/` diagnostic/counterfactual tables, scalars that do not enter `decide()` or `press.json`.
- Add the **Alcance** sentence to the hold bullet: product `hold()` + product proxy on `main`; isolated experiment only if the human asked; no silent `main` contract change.
- Add display-only rounding pointer (source unrounded + caption) next to cero-redondeos.
- Add one bullet pointing at agent modes `release` / `research` and `roadmap/skill_checkout/`. No tables of Qwen2 numbers.

### `cero-redondeos.md`

- Keep the categorical ban on silent scientific rounding.
- Add a short section **Display-only exception** with both conditions required.
- Explicit: `rows.npz`, JSON metrics, interval dumps, and `press.json` are **not** display-only.

### `SKILL.md` (only if needed)

- If §2.7 is still a full essay, replace with a pointer to `cero-redondeos.md`.

## Forbidden edits

- Do not add cosine to `decide()`.
- Do not make `hold()` yield.
- Do not allow `round()` on tensor exports “for smaller files”.
- Do not delete `tools/rompepepe` cosine code.
- Do not edit `architecture_spec.md` unless a single sentence of scope is truly required — **default: do not touch it**. The spec is already product-correct; over-application lives in agent files.
- Do not edit `ddi_fw/**`.

## Definition of Done

- [ ] `lessons-learned.md` still forbids cosine as verdict/publication
- [ ] `lessons-learned.md` mentions `rompepepe` or counterfactual/diagnostic **as out of scope of that ban**
- [ ] hold experiment is described as opt-in isolated, not as a product default
- [ ] display-only rounding has **two** mandatory conditions
- [ ] no new measurement tables in lessons
- [ ] `git diff -- ddi_fw/` empty

## Copiable prompt

```text
Execute roadmap/skill_checkout/tickets/SC05-axiom-wording.md.
Read roadmap/skill_checkout/08-recommended-remediation.md §8.5 and 04-constraint-catalog.md C-AXIOM-01, 05, 07.
Add in-scope/out-of-scope sentences to lessons-learned.md. Add display-only exception to cero-redondeos.md without weakening scientific dumps.
Do not change ddi_fw/, decide(), hold(), or rompepepe. Do not commit unless I ask.
```

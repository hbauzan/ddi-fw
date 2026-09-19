# Q05 — Ledger synthesis vs frozen BGE-M3

> **Estado:** hecho
> **Ola:** Qwen2 live (Q)
> **Depends on:** Q02 (always), Q03–Q04 if they ran
> **Briefing:** [`../00-qwen2-live.md`](../00-qwen2-live.md)
> **Live model:** no

---

## Objective

Close the campaign in **committed** markdown. Numbers live in `current-research/`. `lessons-learned.md` gets at most 2–4 invariant lines, not tables.

---

## Files to update

- [`../../current-research/engines/gte-qwen2-1.5b.md`](../../current-research/engines/gte-qwen2-1.5b.md) — complete all sections; no empty TODOs.
- [`../../current-research/embedder-ledger.md`](../../current-research/embedder-ledger.md) — fill **only** the Qwen2 row. **Never edit the BGE-M3 row.**
- [`../README.md`](../README.md) — mark Q01–Q05 `hecho` / `bloqueado` as appropriate; do **not** paste BGE axes into a new “recommendation: replace BGE” unless the ledger says so.
- [`.agents/skills/dev-protocol/lessons-learned.md`](../../.agents/skills/dev-protocol/lessons-learned.md) — short invariants only, e.g. Qwen2 `custom_code` behaviour, 1536-D, unpublished-on-full-deck finding. Point to the ledger for numbers.

Do not add Qwen numbers as a second table in `roadmap/README.md` that could be mistaken for a replacement of the frozen BGE D07 table. One sentence + link to the ledger is enough.

---

## Comparison rules

Compare Qwen2 to BGE **as measurements**, not as a mandate to change the product pin.

| Question | How to answer |
| :--- | :--- |
| Did Qwen2 publish `python_receta`? | yes/no + `disjoint_count` + axis ids |
| More disjoint axes than BGE’s 1 / 1 / 7? | numeric compare |
| Same axis indices as BGE 891 / 192? | almost certainly no (different space). Do not align axes across models. |
| Should default `DDI_EMBEDDER` change? | **No** unless Qwen2 published headline pairs **and** live piggyback matched expected BREACH/PASS **and** RAM is acceptable. Default recommendation otherwise: **keep BGE-M3 pin**. |

Never write “Qwen failed, so prune mazos”. Never write “Qwen unpublished, invent epsilon”.

---

## Definition of Done

- [x] Qwen engine dump complete (geometry **or** blocker).
- [x] Ledger Qwen2 row complete; BGE row byte-for-byte untouched.
- [x] Wave Q closed in [`../README.md`](../README.md).
- [x] Default pytest green.
- [x] No `.npz` staged.

---

## Copiable prompt

```text
Using dev-protocol, execute roadmap/tickets/Q05-ledger-synthesis.md.
Read roadmap/00-qwen2-live.md first.
Complete current-research/engines/gte-qwen2-1.5b.md and the Qwen2 row of embedder-ledger.md.
Do not edit the BGE-M3 ledger row or roadmap/archive/**.
Do not change DDI_EMBEDDER default unless the briefing comparison rules say so.
Keep lessons-learned short; numbers stay in current-research/.
```

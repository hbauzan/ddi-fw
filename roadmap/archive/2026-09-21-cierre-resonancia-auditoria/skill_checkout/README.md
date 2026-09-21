# skill_checkout — Agent-protocol audit for ddi-fw

**How to hand this to another model:** copy a block from [`AGENT_PROMPT.md`](./AGENT_PROMPT.md). That file distinguishes “understand only” from “implement tickets”.

**Status:** analysis complete. Product code was not changed. Remediation tickets SC01–SC06 **are applied** in `.agents/` (modes, research exceptions, optional persona, USAGE hygiene, axiom scope sentences, one git constitution).

**Audience:** a successor coding agent (and the human who will approve its diff).

**Normative language of this folder:** English. RFC 2119 words (`MUST`, `MUST NOT`, `SHOULD`, `MAY`) are binding inside this folder. Spanish text quoted from `.agents/` is **evidence**, not a second constitution.

**Date of analysis:** 2026-09-19.

**What this folder is:** a frozen, self-contained brief of (1) whether current skills/rules restrict legitimate ddi-fw work, and (2) the exact remediation that preserves product axioms while stopping process over-application.

**What this folder is not:** a product wave, an embedder campaign, a license to put cosine into `decide()`, a license to add speculative streaming to `hold()`, a license to merge `feat/hipotesis-deletor`, or a license to change the BGE-M3 product pin.

---

## Mandatory reading order

A successor agent that will **implement** remediation MUST read in this order before editing `.agents/`:

| Step | File | Why it exists |
| :---: | :--- | :--- |
| 0 | [00-glossary.md](./00-glossary.md) | Stops the agent from treating “skill”, “rule”, “invariant”, and “mode” as synonyms |
| 1 | [01-verdict.md](./01-verdict.md) | The conclusion. Read this before inventing a stronger or weaker claim |
| 2 | [02-inventory-and-load-path.md](./02-inventory-and-load-path.md) | What files exist on disk vs what USAGE.md claims |
| 3 | [03-three-layers.md](./03-three-layers.md) | Protocol vs product axioms vs persona |
| 4 | [04-constraint-catalog.md](./04-constraint-catalog.md) | Every constraint, with allowed vs forbidden scope |
| 5 | [05-research-vs-release-mismatch.md](./05-research-vs-release-mismatch.md) | Why TDD/debug protocol misfits geometry work |
| 6 | [06-instruction-conflicts.md](./06-instruction-conflicts.md) | Overlapping constitutions (git, style, cosine) |
| 7 | [07-overapplication-risks.md](./07-overapplication-risks.md) | How a literalist agent blocks wanted science |
| 8 | [08-recommended-remediation.md](./08-recommended-remediation.md) | Target end-state of `.agents/` |
| 9 | [09-execution-spec.md](./09-execution-spec.md) | MUST/MUST NOT for the implementing agent |
| 10 | [tickets/](./tickets/) | Vertical slices. One ticket at a time |

A successor agent that will **only understand** the analysis MAY stop after step 7.

---

## Tickets (implementation, later)

Execute in order. This pack’s analysis is frozen; the successor that implemented SC01–SC06 did so in one session because the human asked for SC01–SC06 together.

| ID | Title | Depends on |
| :--- | :--- | :--- |
| [SC01](./tickets/SC01-mode-router.md) | Add release vs research mode router to `SKILL.md` | this pack |
| [SC02](./tickets/SC02-research-exceptions.md) | Carve research exceptions into `debugging.md` and `code-design.md` | SC01 |
| [SC03](./tickets/SC03-demote-persona.md) | Make Murray optional; keep density rules | SC01 |
| [SC04](./tickets/SC04-usage-hygiene.md) | Stop claiming files that do not exist | none |
| [SC05](./tickets/SC05-axiom-wording.md) | Narrow cosine / streaming / rounding wording so they cannot swallow research | SC01 |
| [SC06](./tickets/SC06-git-constitution.md) | One git constitution; commits are not free by default | none |

---

## Hard non-goals (copy these into any implementation prompt)

The implementing agent MUST NOT, as part of skill_checkout:

1. Edit `ddi_fw/**` production modules (`decide`, `hold`, `press`, `proxy`, embedder adapters, mazos).
2. Edit `roadmap/archive/**`.
3. Edit the frozen BGE-M3 row in `current-research/embedder-ledger.md`.
4. Introduce cosine, centroids, `mean` of rows, top-k, or `gap >= epsilon` as a **publication or verdict** criterion.
5. Make `hold()` yield tokens, or make `stream=true` succeed on the product proxy.
6. Round or truncate tensor / interval / metric exports in product code.
7. Merge or resurrect `feat/hipotesis-deletor`.
8. Change default `DDI_EMBEDDER` away from `BAAI/bge-m3`.
9. Delete product axioms from `lessons-learned.md`. Distill them, do not erase them.
10. Treat Hugging Face Jobs / Spaces / TRL skills as the toolchain for this repo. The toolchain is `uv`.

---

## Origin

Human request (2026-09-19): review skills in read-only mode; cold analysis of whether they restrict wanted ddi-fw work; then write that analysis plus recommended improvements under `roadmap/skill_checkout` in English, dense enough that another model can execute without guessing.

Related product docs (do not rewrite unless a ticket says so):

- Product glossary: [`../../CONTEXT.md`](../../CONTEXT.md)
- Live contracts: [`../../architecture_spec.md`](../../architecture_spec.md)
- Product invariants: [`../../.agents/skills/dev-protocol/lessons-learned.md`](../../.agents/skills/dev-protocol/lessons-learned.md)
- Skill router: [`../../.agents/skills/dev-protocol/SKILL.md`](../../.agents/skills/dev-protocol/SKILL.md)

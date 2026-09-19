# 03 — Three layers (do not fuse them)

Every instruction in `.agents/` belongs to exactly one layer. If a sentence sits in two layers, it is a defect: split it.

```
Layer A  PROCESS     how the agent moves (TDD, debug, git, docs sync)
Layer B  PRODUCT     what the firewall is allowed to be (geometry, hold, precision)
Layer C  PERSONA     how the agent sounds (Murray, quotes, sandwich)
```

## Layer A — Process (`dev-protocol` modules except lessons-learned axioms)

| Module | Job |
| :--- | :--- |
| `SKILL.md` §0, §3, §4, §5 | Router, toolchain (`uv`), context hygiene, bootstrap |
| `code-design.md` | Deep modules, vertical slices, TDD |
| `debugging.md` | Six-phase loop |
| `qa-review.md` | Two-axis review; issue filing |
| `git-workflow.md` | Commits, hooks, approval gate, delivery |
| `documentation.md` | Conditional doc sync |
| `USAGE.md` | How to install/port the skill |

**Intended benefit:** closed tickets ship with tests, no silent push, no `pip` chaos, no secret-in-git.

**Misfit:** research work is not a closed ticket.

## Layer B — Product axioms

| File | Job |
| :--- | :--- |
| `lessons-learned.md` | Live invariant list agents must not re-break |
| `.agents/rules/cero-redondeos.md` | Native float digits in tensors/intervals/metrics |
| `architecture_spec.md` | Shapes of `BaseEmbedder`, hoja, `decide`, `hold`, HTTP |
| `roadmap/00-alcance.md` | What this pack is and is not |
| `CONTEXT.md` | Glossary of `alma`, `candado`, `piggyback`, … |

**Intended benefit:** the shipping proxy stays a dimensional lock, not a cosine classifier.

**These axioms MUST remain after remediation.** SC05 only adds **scope sentences** so Layer B cannot be used to ban Layer-A-research tools.

## Layer C — Persona

| File | Job |
| :--- | :--- |
| `SKILL.md` §1–§2 | Currently **mandatory** Murray + sandwich + 50/30/20 quotes |
| `.agents/rules/murray.md` | Quote encyclopedia + operational output recipes |
| `.agents/rules/estilo-comunicacion.md` | Sandwich, rotation, “do not reopen”, rioplatense |

**Intended benefit (claimed):** memorable, dense, non-generic prose.

**Actual effect:** context-window tax; conflict with IDE “be concise, lead with the answer”; theatrical git messages; “do not reopen” bleeds from voice into architecture (Layer C contaminates Layer B).

After remediation, Layer C is **optional**. Density, no chatbot filler, no `# TODO`, production-ready code remain **Layer A** rules and stay mandatory.

---

## Fusion bugs (must be unfused)

1. **`lessons-learned.md` is loaded as “always” by the process skill**, so product axioms and process ceremony share one file. Keep the file. Stop treating *process* (Murray, TDD) as if it were a product axiom.

2. **`estilo-comunicacion.md` “Si está cerrado, no lo reabras”** is written as a communication preference and is applied as an architecture freeze. Split: closed **verdict rule** vs never-closed **measurement**.

3. **`SKILL.md` §2.7 zero-rounding** copies Layer B into the always-on router. Keep a one-line pointer to `cero-redondeos.md`; do not keep a third essay in the router.

4. **`git-workflow.md` §1 Murray-flavored commits** fuses Layer C into Layer A. Commits MUST be Conventional Commits that say what changed. Theater MUST NOT be required.

---

## Decision rule for the successor agent

When editing `.agents/`:

- If the sentence is about `decide()`, `hold()`, publication, float digits, fail-closed → Layer B. Preserve. Narrow scope if needed.
- If the sentence is about red-green, phases, push, hooks → Layer A. Scope to **release mode** unless it is universally safe (secrets, `uv`, approval gate).
- If the sentence is about pirates, grog, sandwich, “Tiembla ante Murray” → Layer C. Optional.
- If you cannot classify it, do not delete it. Move it to a ticket question for the human.

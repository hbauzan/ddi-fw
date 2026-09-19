# 00 — Glossary for this pack

These terms are **this pack’s** language. They are not ddi-fw product terms. Product terms stay in [`../../CONTEXT.md`](../../CONTEXT.md).

Do not substitute near-synonyms. If a sentence in a later file uses a bold term below, it means exactly this.

---

## Skill

A versioned agent instruction pack under `.agents/skills/`, discovered by IDEs. In this repo the only live skill directory is `.agents/skills/dev-protocol/`.

_Avoid:_ calling `murray.md` a skill. It is a rule file.

## Rule

A style or policy file under `.agents/rules/`. On disk as of 2026-09-19: `murray.md`, `estilo-comunicacion.md`, `cero-redondeos.md`. Rules are not the same as product architecture.

## Product axiom

A constraint on **what the firewall is allowed to be**. Examples: membership is interval inclusion plus hard cut; cosine is not the verdict; `hold()` does not yield; native float digits are preserved in tensor exports.

Product axioms belong in `lessons-learned.md`, `architecture_spec.md`, `roadmap/00-alcance.md`, and `cero-redondeos.md`. They MUST survive remediation.

## Process constraint

A constraint on **how an agent is allowed to move** while editing the repo. Examples: TDD red-green, six-phase debug, approval gate before push, “do not read code until a red-capable command exists”.

Process constraints are the main thing this pack proposes to **scope**, not delete.

## Persona constraint

A constraint on **voice**. Murray sandwich, Monkey Island quote rotation, theatrical commit messages. Persona does not change geometry. It consumes context window.

## Release mode

Agent mode for implementing a **closed** product behavior: proxy, splitter, `decide()`, `hold()`, publication rules, failing tests, a ticket that already chose the contract.

In release mode, TDD and the debug loop are appropriate.

## Research mode

Agent mode for **measurement and hypothesis**: live embedders, `--no-prune`, `current-research/`, unpublished locks, Jaccard, mazo curation, ledger rows, geometry that may contradict a previous headline.

In research mode, TDD-first and “do not read code yet” are inappropriate. Product axioms still bind the **product**. They do not bind the **notebook / ledger / counterfactual**.

## Over-application

Taking a true product axiom and enforcing it outside its scope, so that legitimate work is refused. Example: “cosine MUST NOT decide membership” stretched into “the agent MUST NOT touch `tools/rompepepe` because that tree mentions cosine”.

## Closed architecture vs closed measurement

- **Closed architecture:** the verdict rule of the shipping proxy (intervals + hard cut, fail-closed, no speculative streaming). Do not silently replace it.
- **Closed measurement:** a number already written in a ledger (BGE axis 891, Qwen2 unpublished headlines). A measurement being recorded does **not** mean “never measure again” and does **not** mean “refuse a new model”.

The phrase in `estilo-comunicacion.md` (“if it is closed, do not reopen it”) currently collapses these two. That collapse is a defect of the rule, not a product requirement.

## Canonical protocol phrase

The user utterance that opts into the full delivery cycle in `SKILL.md` §0:

- Spanish: `Usando dev-protocol, <task>`
- English: `Using dev-protocol, <task>`

Without that phrase (or an explicit “execute ticket SC0x”), the agent MUST NOT assume it owns git commit/push/merge.

## Phantom file

A file that USAGE.md or another instruction **names as if it existed**, but that was absent from the workspace at analysis time. Examples listed in [02-inventory-and-load-path.md](./02-inventory-and-load-path.md).

## Load path

The mechanism by which an IDE injects skills/rules into an agent’s context. Cursor, Claude Code, and Gemini do not share one load path. Inconsistent load path is not a product bug; it is why agents oscillate between “full protocol” and “no protocol”.

## Literalist agent

An agent that treats every prohibition as global. This pack is written to defeat literalist over-application by stating **scope** next to every prohibition.

## Successor agent

The other model that will read this folder and, if the human asks, execute SC tickets. This pack is the constitution for that work.

# 02 — Inventory and load path

Snapshot date: 2026-09-19. Paths are relative to the repository root `ddi-fw/`.

If the disk has changed when you read this, **believe the disk**, then update this file in the same change. Do not invent files because USAGE.md names them.

---

## 2.1 Files that exist (agent instruction surface)

### Skill (live)

```
.agents/skills/dev-protocol/SKILL.md
.agents/skills/dev-protocol/USAGE.md
.agents/skills/dev-protocol/code-design.md
.agents/skills/dev-protocol/debugging.md
.agents/skills/dev-protocol/qa-review.md
.agents/skills/dev-protocol/git-workflow.md
.agents/skills/dev-protocol/documentation.md
.agents/skills/dev-protocol/lessons-learned.md
.agents/skills/dev-protocol/templates/.pre-commit-config.yaml
.agents/skills/dev-protocol/templates/.env.example
```

`SKILL.md` is the router. `lessons-learned.md` is **both** a protocol module and the live product-invariant list. That dual role is why process and axioms get fused.

### Rules (live)

```
.agents/rules/murray.md
.agents/rules/estilo-comunicacion.md
.agents/rules/cero-redondeos.md
```

### Cursor project rules

As of the snapshot, `.cursor/rules/` had **no** files. There was **no** `.cursor/rules/dev-protocol.mdc`.

### Root agent pointers that USAGE.md says exist

As of the snapshot, **none** of these existed at repo root:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `UBIQUITOUS_LANGUAGE.md`
- `CODING_STANDARDS.md`

### Skills that USAGE.md says exist and did not

- `.agents/skills/grilling/` (optional stress-test skill) — **absent**
- `.agents/skills/_archive/` (archived Pocock-style skills) — **absent**
- `scripts/setup-skills.sh` — **not verified in this audit as a required product script**; do not create it unless SC04 says to. If you mention it, check the disk.

---

## 2.2 What USAGE.md claims (drift)

`USAGE.md` currently states, as if true:

1. Root files `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` are versioned pointers to `SKILL.md`.
2. This project uses `dev-protocol` **plus** optional `grilling`.
3. Generic skills were archived under `.agents/skills/_archive/`.
4. Domain modeling was replaced by root `UBIQUITOUS_LANGUAGE.md`.
5. Cursor should get `.cursor/rules/dev-protocol.mdc` pointing at `docs/dev-protocol/SKILL.md` — a **third** path (`docs/dev-protocol/`) that is **not** where the skill actually lives (`.agents/skills/dev-protocol/`).

These claims are **false on disk** at snapshot time. A successor agent that “restores” them without being asked is inventing scope. SC04 tells you how to fix the claims: **make USAGE.md match the disk**, or **create thin real pointers**. Do not do both unless the human picks one.

**Preferred fix (default if the human does not pick):** edit USAGE.md so it only names files that exist. Do **not** create `grilling`, `_archive`, or `UBIQUITOUS_LANGUAGE.md` as empty theater.

**Optional extra, only if the human wants IDE auto-load:** add a thin `AGENTS.md` at repo root that points at `.agents/skills/dev-protocol/SKILL.md` and at this pack’s mode split. That is a separate, explicit decision. SC04 default is documentation honesty, not new entrypoints.

---

## 2.3 How Cursor actually saw the skill (analysis session)

In the analysis session, Cursor’s `available_skills` list included:

- **This repo:** `.agents/skills/dev-protocol/SKILL.md` (description: use for any implementation / TDD / slices / debug / git / docs).
- **Cursor product skills:** automate, canvas, visualize, create-rule, etc. (trigger on explicit product questions).
- **Hugging Face plugin skills:** `hf-cli`, local-models, trainers, spaces, ZeroGPU, etc.

The `hf-cli` skill description told the agent to use it whenever the user wants to do anything related to the Hugging Face ecosystem **and to AI and ML in general**.

ddi-fw **is** an ML-adjacent system. The correct first reads for ddi-fw ML work are:

1. `architecture_spec.md`
2. `.agents/skills/dev-protocol/lessons-learned.md`
3. the roadmap ticket or `current-research/` dump
4. `ddi_fw/` adapters

They are **not**: Hugging Face Jobs, Spaces, TRL, or ZeroGPU, unless the human named those products.

This is an **operator/IDE catalog** problem more than a repo-file problem. Remediation inside the repo is limited to: say so in `SKILL.md` §3 (toolchain is `uv`; Hub download of a pinned model is not “start a Space”).

---

## 2.4 Duplicate injection of the same ideas

Even if `.agents/rules/` are not auto-loaded, `SKILL.md` §1–§2 already injects Murray + sandwich + quote ratios + zero-rounding.

`cero-redondeos.md` restates zero-rounding.

`lessons-learned.md` restates zero-rounding **and** cosine-not-verdict **and** hold **and** uv.

`estilo-comunicacion.md` restates sandwich + quote rotation + “do not reopen what is closed”.

`murray.md` is a quote encyclopedia for the rotation rule.

**Effect:** a fully loaded agent pays the persona tax three times and the axiom tax three times before reading `ddi_fw/decide.py`. That is the opposite of `SKILL.md` §4 “progressive disclosure”.

Remediation: one canonical copy per idea.

| Idea | Canonical file after remediation | Other files |
| :--- | :--- | :--- |
| Product numeric precision | `.agents/rules/cero-redondeos.md` | `lessons-learned.md` keeps a **one-line pointer**, not a second essay |
| Cosine is not verdict | `lessons-learned.md` + `architecture_spec.md` | SC05 adds scope sentence; do not copy into SKILL.md at length |
| Agent modes | `SKILL.md` (short router) | this pack remains the rationale |
| Murray voice | `.agents/rules/murray.md` | SKILL.md and estilo point to it as **optional** |
| Git | `git-workflow.md` | SKILL.md §0 points; no third copy |
| Debug loop | `debugging.md` | not in SKILL.md body |
| TDD | `code-design.md` | not in SKILL.md body |

---

## 2.5 Product files the protocol points at (exist)

These are real and MUST remain the product source of truth:

- `CONTEXT.md`
- `architecture_spec.md`
- `roadmap/00-alcance.md`
- `roadmap/archive/ola-q/00-qwen2-live.md`
- `roadmap/almas.md`
- `current-research/embedder-ledger.md`
- `ddi_fw/` implementation
- `tools/rompepepe/` (adversarial / telemetry tree; **mentions cosine as telemetry**, not as `decide()`)

---

## 2.6 Load-path implication for the successor agent

Because there is no `AGENTS.md` and no `.cursor/rules/*.mdc`, **Cursor may or may not inject** `.agents/rules/*.md` automatically. What **is** reliable:

- If the user says `Using dev-protocol, …`, you MUST open `SKILL.md` then the modules the task needs, plus `lessons-learned.md`.
- If the user says `execute roadmap/skill_checkout/tickets/SC0x.md`, you MUST follow that ticket plus [09-execution-spec.md](./09-execution-spec.md).
- If the user says nothing about protocol, you MUST NOT run the full git delivery cycle.

Do not “fix” load path by dumping the entire `murray.md` into `SKILL.md`. That worsens the tax.

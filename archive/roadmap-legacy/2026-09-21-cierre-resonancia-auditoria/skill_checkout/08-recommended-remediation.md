# 08 — Recommended remediation (target end-state)

Do not invent a seventh ticket. If a change is not listed here, it is out of scope.

Apply via [tickets/](./tickets/) in order SC01→SC06 except SC04 and SC06 which have no hard dependency on SC01 (they MAY run in parallel with SC01 if the human wants parallel slices; they MUST NOT conflict on the same file).

**File ownership (prevent colliding edits):**

| File | Owner ticket |
| :--- | :--- |
| `.agents/skills/dev-protocol/SKILL.md` | SC01 (mode router) then SC03 (persona demotion). If both run, SC01 first, SC03 second. |
| `.agents/skills/dev-protocol/debugging.md` | SC02 |
| `.agents/skills/dev-protocol/code-design.md` | SC02 |
| `.agents/skills/dev-protocol/USAGE.md` | SC04 |
| `.agents/skills/dev-protocol/lessons-learned.md` | SC05 (scope sentences + one pointer to modes). SC01 MUST NOT rewrite axioms. |
| `.agents/skills/dev-protocol/git-workflow.md` | SC06 |
| `.agents/rules/estilo-comunicacion.md` | SC03 |
| `.agents/rules/murray.md` | SC03 (header only: mark optional). Do not delete the quote encyclopedia. |
| `.agents/rules/cero-redondeos.md` | SC05 (add display-only exception paragraph; do not weaken the scientific rule) |
| `roadmap/README.md` | already points here after this pack lands; do not rewrite product tables |
| New `AGENTS.md` | **not** in default scope (SC04 default = honesty, not new entrypoints) |

---

## 8.1 End-state of `SKILL.md`

Keep: portability note, module index, §0 cycle, §3 toolchain, §4 hygiene, §5 bootstrap, `uv` rules, secrets, LLM seam, zero-guessing on **contracts**.

**Add immediately after the module index (before §0), a section titled `Agent modes`:**

Normative text the successor MUST insert (English is allowed inside SKILL.md even if the rest of the file is Spanish; prefer Spanish headers with English MUST/MUST NOT if the surrounding file is Spanish — **match the file’s existing language** so you do not create a bilingual mess. SKILL.md is currently Spanish. Write the new section in Spanish, but keep the mode names `release` and `research` in English as tokens).

Spanish payload to insert (do not paraphrase into something weaker):

```markdown
## Modos de agente (release vs research)

Clasificá la tarea **antes** de aplicar TDD o el loop de debug.
Nombres canónicos en inglés: `release` y `research`.

### Siempre (ambos modos)

- Toolchain Python: `uv`. Secrets en `.env`.
- `decide()` y la publicación del candado: intervalos + corte duro. Prohibido cosine / centroides / `mean` de filas / top-k / `gap >= epsilon` como criterio de veredicto o publicación.
- Precisión nativa en exportaciones científicas (ver `.agents/rules/cero-redondeos.md`).
- Proxy de producto: fail-closed, `hold()` sin yield, `stream=true` → 400, 403 sin echo.
- Tests default: `FakeEmbedder`. Live es explícito.
- No mergear `feat/hipotesis-deletor` de contrabando.
- No `git push` / merge a base sin OK explícito del usuario.

### `release`

Usalo cuando cambia el contrato de producto (`decide`, `hold`, proxy, splitter, publicación) o hay un bug de comportamiento con síntoma HTTP/CLI/test.

Ahí sí: TDD en `code-design.md`, debug de 6 fases en `debugging.md`, slices verticales.

### `research`

Usalo cuando el entregable es medición: `current-research/`, ledger, `--no-prune`, `measure_and_save`, disjuntos, unpublished, Jaccard, live embedder, censo `press` sin cambiar `decide()`.

Ahí: leé código, lessons y ledger **primero**. TDD no es obligatorio. Prohibido “poner verde” un unpublished podando mazos compartidos o inventando epsilon. `calibrate()` no es el path de medición Qwen2.

Detección y tabla: `roadmap/skill_checkout/05-research-vs-release-mismatch.md`.
Si la tarea mezcla ambos, partí: research para números, release para cualquier diff de `ddi_fw/` de veredicto.
Si no podés clasificar, preguntá una sola vez: release o research.
```

**Remove or demote §1 and §2 persona block** according to SC03: replace mandatory Murray with a pointer:

```markdown
Estilo: densidad alta, sin relleno de chatbot, código production-ready, sin `# TODO`.
Persona Murray: **opcional** — solo si el usuario la pide. Canon: `.agents/rules/murray.md`.
No cargues el compendio de citas en tareas `research`.
```

Keep §2 items that are Layer A: schematic structure, complete code, trade-off matrix, ask when contracts are ambiguous, pointer to cero-redondeos (one line, not a third essay).

**Add under §3.2 a sentence:** Hugging Face Hub may supply a **pinned** model id already used by an adapter. Hugging Face Jobs/Spaces/TRL/ZeroGPU are **not** the default toolchain. Do not read those skills first for ddi-fw work.

---

## 8.2 End-state of `debugging.md`

After the prohibited-action bullet in Phase 1, add an exception. English is fine if you keep a Spanish heading; **match file language** (`debugging.md` is English). Insert:

```markdown
### 1.3 Exception: research / geometry / embedder-load (research mode)

The prohibition “do not read code to build a theory before a red-capable command exists” applies to **release-mode product bugs** with an HTTP/CLI/test symptom.

It does **not** apply when the task is classified `research` (see `SKILL.md` agent modes), including:

- unpublished locks / zero disjoint axes
- live embedder load, shims, gated 401, custom_code failures
- Jaccard / mazo contamination / veto collisions
- ledger / `current-research/` measurement
- “why did model Y fail to publish?”

In those cases you MUST read `lessons-learned.md`, the implicated `ddi_fw/` modules, and the ledger **before** or **instead of** inventing a throwaway harness. The measurement command (`uv run python -m ddi_fw.embedder --no-prune …`, a targeted pytest, a press census) **is** the loop.

Do not skip Phase 1 for a **proxy 500** or a **wrong HTTP code**. That remains release-mode debugging.
```

Do not delete the original prohibition. Scope it.

---

## 8.3 End-state of `code-design.md`

Add a section at the top (after the intro paragraph), file is English:

```markdown
## When TDD is mandatory vs not

**Mandatory (release mode):** any behavior change to public product seams: `decide`, `hold`, ingress splitter, proxy HTTP, candado publication, `BaseEmbedder` contract.

**Not mandatory (research mode):** `current-research/` markdown, ledger rows, `--no-prune` / `measure_and_save` runs, one-off measurement scripts that do not change `decide()` / `hold()` / proxy contracts.

Research mode is not a license to skip tests when you **do** change those seams. If a research task starts editing `decide()`, it has become release mode for that diff.
```

Do not weaken deep-module or seam rules.

---

## 8.4 End-state of persona files (SC03)

`estilo-comunicacion.md`:

- Keep: density, no chatbot filler, no `# TODO`, literal vs implicit, one visual cue, rioplatense when speaking Spanish, product terms in English.
- Change sandwich from **Obligatoria** to **Optional if Murray is on**.
- Replace “Si está cerrado, no lo reabras” with:

```markdown
- Contrato de veredicto del proxy (intervalos + corte duro, no cosine en `decide()`, hold sin streaming especulativo): cerrado, salvo ticket explícito de cambio de arquitectura.
- Mediciones (¿publica el modelo Y? ¿cuántos disjuntos? Jaccard): **nunca** cerradas. Un número previo en el ledger no es un tabú. Se registra la medición nueva. No se “protege” un headline negándose a medir.
```

`murray.md`: add a 5-line header:

```markdown
> **Activation:** optional. Do not apply this file unless the user asked for Murray or a task explicitly enables persona.
> **Never apply** to `current-research/` file bodies or to scientific tables.
```

Do not delete the quote matrix (the human may still want it).

`SKILL.md`: as in 8.1, no mandatory quote ratios.

---

## 8.5 End-state of axiom wording (SC05)

`lessons-learned.md` — do **not** delete existing bullets. Add immediately under the cosine bullet (or at the end of that bullet):

```markdown
  Alcance: el **veredicto** y la **publicación** del candado. Fuera de alcance: telemetría en `tools/rompepepe/`, tablas en `current-research/` marcadas como diagnóstico/contrafactual, y cualquier scalar que no entre a `decide()` ni a `press.json`.
```

Add under the hold bullet:

```markdown
  Alcance: `hold()` y el proxy de producto en `main`. Un experimento de latencia **solo** si el usuario lo pide, en rama/prototipo aislado, sin cambiar el contrato de `main`.
```

Add under cero-redondeos (or keep one line + pointer):

```markdown
  Display-only: un plot o tabla humana MAY redondear dígitos de **presentación** si el artefacto fuente conserva precisión nativa y el caption dice `display-only rounding; source unrounded`.
```

Add one maintenance line pointing at modes:

```markdown
- **Modos de agente:** `release` vs `research` — ver `SKILL.md` y `roadmap/skill_checkout/`. No tratar el proceso TDD/debug como axioma de geometría.
```

`cero-redondeos.md`: add a short §3 “Display-only exception” with the same two conditions (source unrounded + caption). Do not add aesthetic rounding of `rows.npz` or JSON metrics.

Collapse the long cero-redondeos essay in SKILL.md §2.7 to a pointer. One copy of the essay is enough (`cero-redondeos.md` + one-line in lessons).

---

## 8.6 End-state of `USAGE.md` (SC04)

- Replace claims of `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` as existing files with: “optional root pointers; **as of skill_checkout they are not required**; the skill lives at `.agents/skills/dev-protocol/`.”
- Remove `grilling` and `_archive` as if present. Say: not in this clone; do not symlink missing paths.
- Fix the Cursor example path: it MUST point at `.agents/skills/dev-protocol/SKILL.md`, **not** `docs/dev-protocol/SKILL.md`.
- Remove `UBIQUITOUS_LANGUAGE.md`. Domain glossary is `CONTEXT.md`.
- Keep the warning about Cursor indexing a huge global skill catalog. That warning is true and useful.

Default: **do not create** the phantom files.

---

## 8.7 End-state of `git-workflow.md` (SC06)

Rewrite §3.1–§3.2 to match [06-instruction-conflicts.md](./06-instruction-conflicts.md) resolution:

- Commits are **not** free by default.
- Push/merge still approval-gated.
- Prefer `gh pr create` on GitHub unless the user asked to merge `main`.
- Commit messages: Conventional Commits, factual. Strip “Murray style required” from §1. Examples MAY remain as optional flavor, labeled optional.

Keep §3.3 stop-and-ask and §3.4 destructive list.

Remove or mark optional the YAML “Git Metadata block at the end of every response”. It is noise in research answers. MAY keep for release delivery reports if the user wants it.

---

## 8.8 What we explicitly will not do

- Will not delete `dev-protocol`.
- Will not move product axioms out of `lessons-learned.md` into a place agents will not read.
- Will not add cosine to `decide()`.
- Will not enable product streaming.
- Will not create a second skill `ddi-research` unless the human later asks. **Mode section inside SKILL.md is enough.** A second skill doubles catalog tax (C-EXT-01 analogue).
- Will not auto-write `AGENTS.md` / `.cursor/rules/*.mdc` in the default tickets.
- Will not “fix” `tools/rompepepe`.
- Will not touch `ddi_fw/**` production modules.
- Will not expand `lessons-learned.md` with this pack’s rationale. Pointer only.

---

## 8.9 Suggested one-line in `roadmap/README.md`

Already in scope of the pack-authoring change (not an SC ticket): a short “Agent protocol audit” bullet pointing at this folder, **without** putting skill_checkout into the Q01–Q05 table.

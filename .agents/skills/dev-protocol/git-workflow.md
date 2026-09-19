# GIT AND VERSION CONTROL WORKFLOW (Gitstuff)

Follow these rules for committing code, running hooks, and maintaining version safety.

---

## 1. COMMIT MESSAGES

Commits MUST use Conventional Commits (`type(scope):`) and a factual summary of **why**.

Murray/sarcasm flavor is **optional**, never required. Do **not** append a YAML Git Metadata block at the end of every chat response. A short branch + commit line in a **release** delivery report is optional if the user wants it.

```text
<type>(<scope>): <factual why>
```

**Optional flavor examples** (never mandatory):
- `feat(cloudflared): sellar el tunel Zero Trust antes de que algun granjero de vacas intente colarse sin pagar peaje a Largo LaGrande`
- `fix(postgres): aniquilar fuga en el pool de conexiones porque estos mortales ineptos olvidaron cerrar cursores transaccionales`
- `refactor(n8n): purgar workflows espagueti y levantar barricada vudú con validación estricta de ChatID`

If this repo’s recent commits already use a `Co-authored-by: Cursor <cursoragent@cursor.com>` trailer, keep it on commits the human requested. Do not invent a new trailer policy.

---

## 2. PRE-COMMIT HOOK CONVENTIONS

To keep code quality and formatting consistent before any commit is finalized, use the Python **`pre-commit`** framework (configured via a `.pre-commit-config.yaml` at the workspace root). This replaces Node-centric tooling (Husky / lint-staged) for Python projects.

A ready-to-use base config ships with this protocol at [`templates/.pre-commit-config.yaml`](./templates/.pre-commit-config.yaml) — copy it to the workspace root and pin the `rev:` tags.

### 2.1. Recommended Hook Setup
Conventions (swappable per app, but stay consistent within a repo):
- **Format + Lint**: `ruff format` and `ruff check --fix` on staged files (fast, autofixing).
- **Type Check**: a static type check (`mypy` or `pyright`) in CI or as a manual-stage hook (type checking the whole project can be slow for a per-commit hook).
- **Secret Scan**: a secret-detection hook (e.g. `detect-secrets` / `gitleaks`) to enforce the "no keys in git" rule from [SKILL.md](./SKILL.md) §3.2.
- **Hygiene**: trailing-whitespace, end-of-file-fixer, and a check that `.env` is never staged.

### 2.2. Installation & Smoke Testing
- Install the git hook once per clone: `uv run pre-commit install`.
- Always smoke-test locally before pushing or resolving a task: `uv run pre-commit run --all-files`.
- For a JS/TS frontend that exists alongside (see [SKILL.md](./SKILL.md) §3.3), wire its own formatter via that ecosystem's tooling; do not impose Python hooks on JS files or vice versa.

---

## 3. GIT DELIVERY & AUTOMATION POLICY

The agent may create a feature branch, stage, commit, push, and open a PR — **gated**. Local commits are **not** free by default. Push and merge remain approval-gated.

### 3.1. The Approval Gate (mandatory)

- Create a feature branch `<type>/<short-name>` when editing product or protocol code, unless the human said to stay on the current branch.
- `git commit` only if the human asked to commit **or** used the canonical protocol phrase (`Usando dev-protocol, …` / `Using dev-protocol, …`) **and** the current ticket says local commits are in scope.
- The agent must **NOT `git push` and must NOT merge to the base branch** until the user has given a **separate explicit go-ahead** (e.g. "ok", "dale", "andá", "mergealo", "push", "create the PR").
- Reporting "ready to test" and then **waiting** is mandatory. Silence, a thumbs-up on something unrelated, or the absence of objection is **not** approval.

### 3.2. Delivery Sequence (run only after approval)

Default remote integration when `origin` is GitHub:

1. `git checkout -b <type>/<short-name>` — if not already on a dedicated task branch.
2. Stage **only files relevant to the task**. Leave unrelated untracked/modified files alone; if scope is unclear, ask (see §3.3).
3. `git commit` using Conventional Commits from §1 (include the existing `Co-authored-by` trailer if this repo already uses it).
4. `git push -u origin HEAD`.
5. `gh pr create` (do **not** merge `main` unless the human asked to merge `main`).

Direct `git checkout <base>` → `git merge --no-ff <branch>` → `git push origin <base>` **only** if the human said to merge `main` (or named another base).

6. *(Optional, ask first)* delete the merged branch locally and on the remote.

### 3.3. Stop-and-Ask Conditions ("when it gets complicated")
**Pause and ask the user** before continuing if any of these arise during delivery:
- Merge conflicts, or the base branch has diverged / moved since branching.
- A pre-commit hook, type check, test, or CI check **fails**.
- The base branch is **protected**, or the push is rejected.
- A **force-push** (`--force` / `--force-with-lease`) would be required.
- Commit **scope is ambiguous** (unrelated changes staged, or unrelated untracked files present that might belong in the commit).
- The remote, credentials, or target branch are **not what was expected**.

### 3.4. Destructive Commands (always require explicit confirmation)
These are **not** part of the normal flow and risk irreversible data loss. Never run them autonomously — propose the command and get an explicit "yes" first:
- `git reset --hard` (prefer a soft reset or `git restore <file>`).
- `git clean -f` / `git clean -fd`.
- `git branch -D`.
- `git checkout .` / `git restore .` (reverting the entire working directory).
- Any history rewrite on an already-pushed branch (`rebase`, `commit --amend` after push, force-push).

### 3.5. Claude Code Integration
Optionally register a `PreToolUse` matcher hook (e.g., `.claude/hooks/block-dangerous-git.sh`) that intercepts **only the §3.4 destructive commands**. `git push` and `git merge` must **not** be blocked — they are governed by the approval gate (§3.1), not by a hook.

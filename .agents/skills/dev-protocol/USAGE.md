# CÓMO USAR `dev-protocol` (instalación y portabilidad)

Guía de uso de la skill: cómo encajan los archivos entre sí, cómo instalarla en Claude Code, y cómo portarla a otros IDEs/IAs (Cursor, Gemini, OpenCode, etc.) que **no** tienen el mecanismo de skills.

> ⚠️ **Distinción clave**: el **auto-trigger** y la **disclosure progresiva** (cargar un módulo solo cuando hace falta) son **nativos de Claude Code**. En las demás herramientas no existen "skills": tienen un archivo de **reglas/contexto** que vos apuntás a estos mismos `.md`. El contenido del protocolo es portable; el mecanismo de carga, no.

---

## 1. Cómo encajan las piezas (entre ellas)

```
dev-protocol/
├─ SKILL.md          ← ENTRADA. Router liviano. Se lee SIEMPRE primero.
│                      (modos release/research, §3 entorno, §0 flujo idea→entrega, higiene, bootstrap)
├─ code-design.md    ← módulos profundos + TDD     ┐
├─ debugging.md      ← loop de 6 fases             │ se leen SOLO cuando
├─ qa-review.md      ← review de dos ejes + issues │ la tarea lo pide
├─ git-workflow.md   ← commits, pre-commit, entrega│ (referenciados desde
├─ documentation.md  ← doc-sync manifest/spec      │  SKILL.md por ruta relativa)
│                                                  ┘
├─ lessons-learned.md← invariantes de producto (siempre consultar)
├─ templates/        ← copy-to-root: .pre-commit-config.yaml, .env.example
└─ USAGE.md          ← este archivo
```

- **`SKILL.md` es el único archivo "siempre cargado".** Es un índice/router: no duplica el contenido de los módulos, los referencia. Eso es lo que ahorra tokens.
- **Los módulos son auto-contenidos** y se cruzan entre sí con rutas relativas (`./debugging.md`, etc.). No usan rutas absolutas → la carpeta funciona en cualquier repo.
- **Punteros opcionales en la raíz** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`): algunos IDEs los usan. **As of skill_checkout they are not required** y **no existen en este clon**. La fuente de verdad es `.agents/skills/dev-protocol/SKILL.md`. No los inventes para “completar el teatro”.

---

## 2. Claude Code (nativo — auto-trigger + disclosure progresiva)

### Cómo se invoca
- **Auto (description)**: el frontmatter dispara la skill cuando la tarea es del stack (Python/`uv` + LLM). Requiere que Claude Code la descubra → necesita el symlink en `.claude/skills/` (ver install).
- **Explícito**: `/dev-protocol` (también requiere el symlink).
- **Frase canónica**: `Usando dev-protocol, <qué hacer / mejorar / arreglar>`.

### Instalar — opción A: per-repo (convención de este repo)
En este repo `.agents/` **está versionado** (no en `.gitignore`), así que el contenido de la skill viaja con `git clone`. Lo que **no** viaja es el symlink de descubrimiento de Claude Code, porque `.claude/skills/` está gitignored. Por eso el único paso de install por clon es recrear ese symlink:
```bash
# desde la raíz del repo, una vez por clon
mkdir -p .claude/skills
ln -sfn ../../.agents/skills/dev-protocol .claude/skills/dev-protocol
```
> El protocolo se aplica leyendo `.agents/skills/dev-protocol/SKILL.md`. El symlink solo habilita el auto-trigger nativo y el slash command `/dev-protocol`.
>
> Para llevar la skill a **otro** repo desde cero: `cp -R /ruta/a/dev-protocol .agents/skills/dev-protocol` y luego el `ln -s` de arriba.

### Instalar — opción B: global (disponible en TODOS tus proyectos)
```bash
cp -R /ruta/a/dev-protocol ~/.claude/skills/dev-protocol
```

---

## 3. Otros IDEs / IAs (sin mecanismo de skills)

> **En este clon** no hay `AGENTS.md` ni `GEMINI.md` en la raíz. Eso es aceptable. Si un IDE necesita un puntero, crealo **solo** si el humano lo pide; el default de skill_checkout es honestidad de disco, no nuevos entrypoints.

La estrategia es siempre la misma en dos pasos:
1. **Tené la carpeta** `dev-protocol/` en el repo. En este repo vive versionada en `.agents/skills/dev-protocol/`.
2. **Apuntá el archivo de reglas/contexto de la herramienta** a `.agents/skills/dev-protocol/SKILL.md` (y aclarale que lea los módulos bajo demanda).

| Herramienta | Archivo de reglas/contexto | Qué poner adentro |
| :--- | :--- | :--- |
| **Cursor** | `.cursor/rules/dev-protocol.mdc` (opcional; **hoy no está** en este clon) | Regla `always`/`auto` que diga: *"Seguí el protocolo en `.agents/skills/dev-protocol/SKILL.md`; leé sus módulos referenciados solo cuando la tarea lo requiera."* |
| **Gemini CLI** | `GEMINI.md` (opcional) | Bloque apuntando a `.agents/skills/dev-protocol/SKILL.md`. |
| **OpenCode / genérico** | `AGENTS.md` (opcional; estándar [agents.md](https://agents.md)) | Igual: referenciá `SKILL.md` + nota de carga bajo demanda. |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Referenciá `SKILL.md`. |
| **Windsurf** | `.windsurfrules` (o `.windsurf/rules/`) | Referenciá `SKILL.md` + módulos bajo demanda. |

### Plantilla de regla (pegá esto en el archivo de la herramienta)
```markdown
# Protocolo de desarrollo
Para CUALQUIER tarea de implementación, bug, review o entrega en este repo,
seguí el protocolo en `.agents/skills/dev-protocol/SKILL.md`.
- Leé `SKILL.md` primero (modos release/research, entorno, flujo idea→entrega con approval gate).
- Leé los módulos SOLO cuando la tarea lo pida:
  diseño/TDD → code-design.md · bug → debugging.md · review → qa-review.md ·
  git/entrega → git-workflow.md · docs → documentation.md.
- Regla dura: dependencias Python con `uv` (nunca `pip` ni venv manual).
- No hagas push/merge sin OK explícito del usuario (approval gate de git-workflow.md §3).
```

> **Nota de fidelidad**: como estas herramientas no tienen disclosure progresiva, el agente puede cargar todos los módulos que referencies de una. Si te importa el ahorro de tokens ahí, referenciá en el archivo de reglas **solo** `SKILL.md` y dejá que el agente abra los módulos cuando los necesite.

---

## 4. Una sola fuente de verdad

Mantené **una** copia de `dev-protocol/` por repo y que todos los archivos de reglas (si existen) **la referencien** en vez de copiar el contenido. Así actualizás el protocolo en un solo lugar.

En este clon el glosario de dominio es **`CONTEXT.md`** (raíz). No hay `UBIQUITOUS_LANGUAGE.md`.

> Los nombres de archivo de reglas de cada herramienta evolucionan rápido — si alguno no funciona, verificá la doc oficial vigente de esa herramienta. El patrón ("apuntá su archivo de contexto a `SKILL.md`") se mantiene.

---

## 5. Higiene de skills en este repo (ahorro de tokens)

Este clon versiona **una** skill: `dev-protocol` en `.agents/skills/dev-protocol/`.

**No** hay `.agents/skills/grilling/` ni `.agents/skills/_archive/` en este clon. No las symlinkees. No las recrees vacías.

No hay `scripts/setup-skills.sh` en este clon. El install de Claude Code es el `mkdir` + `ln -sfn` de la sección 2.

### Cursor / skills globales

Si Cursor indexa `~/.agents/skills/` entero (~1500 entradas), el catálogo `available_skills` consume muchos tokens **antes** de leer código. Mitigación recomendada:

- Mantener skills **a nivel repo** y **no** exponer el directorio global completo en la configuración del IDE, o
- Reducir el set global a skills que uses en todos los proyectos (p. ej. solo `dev-protocol`).
- El plugin Hugging Face de Cursor puede listar trainers/Spaces/ZeroGPU. Eso **no** es el toolchain de ddi-fw (`uv`). Ignoralo salvo que el humano nombre ese producto.

### Qué usar en lugar de packs genéricos

| Tema | Usar |
| :--- | :--- |
| diagnosing-bugs | `dev-protocol/debugging.md` |
| tdd | `dev-protocol/code-design.md` |
| review | `dev-protocol/qa-review.md` |
| setup-pre-commit | `dev-protocol/git-workflow.md` + `.pre-commit-config.yaml` del repo |
| domain-modeling | `CONTEXT.md` (raíz del repo) |
| qa, planes, tickets | `roadmap/*.md` Agent Prompts + dev-protocol |

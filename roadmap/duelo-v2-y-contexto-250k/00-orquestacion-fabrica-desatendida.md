# 00 — Guía Maestra de Orquestación Desatendida (`fabrica-de-software` + Agentes Ejecutores)

**Estado:** `LISTO PARA EJECUCIÓN DESATENDIDA`  
**Target de Agentes:** Modelos de capacidad media/estándar en Cursor o Gemini 3.8 operando sin supervisión humana continua.  
**Orquestador Local:** `/Users/hbauzan/treepwood/fabrica_de_software/agent.sh` ([`.agents/skills/fabrica-de-software/SKILL.md`](../../.agents/skills/fabrica-de-software/SKILL.md))  
**Protocolo Base:** [`.agents/skills/dev-protocol/SKILL.md`](../../.agents/skills/dev-protocol/SKILL.md)

---

## 1. Arquitectura de Aislamiento (Por Qué un Agente Menor NO Puede Romper el Repo)

Este roadmap fue diseñado específicamente para que un agente ejecutor literal (sin razonamiento profundo) complete el trabajo de punta a punta **sin bloquearse, sin romper tests previos y sin falsear métricas**:

1. **Cero colisión con `ddi_fw/` legacy y con `dev-protocol` línea 43:**
   - **PROHIBIDO** modificar cualquier archivo existente en `ddi_fw/*.py` (`hoja.py`, `corte.py`, `ingress.py`, `egreso.py`, `proxy.py`) ni en `tests/test_*.py`.
   - Todo el código nuevo vive aislado en:
     - Paquete experimental: `ddi_fw/lab_v2/`
     - Scripts ejecutables: `scripts/lab_v2/`
     - Tests unitarios e integración: `tests/lab_v2/`
   - El motor actual (`ddi_fw` v0.4.0) se importa **en modo solo-lectura** como competidor baseline `M1`. Así los 67 tests actuales nunca se rompen y la restricción de `decide()` en `dev-protocol/SKILL.md` se respeta al 100%.
2. **Aislamiento de la Bóveda del Usuario:**
   - **PROHIBIDO** abrir, leer o referenciar cualquier archivo dentro de `roadmap/future-notes/` durante la ejecución desatendida. Todo lo necesario está autocontenido en esta carpeta (`roadmap/duelo-v2-y-contexto-250k/`).
3. **Cero dependencias externas nuevas:**
   - **PROHIBIDO** ejecutar `pip install` o `uv add`. Toda el álgebra lineal (Ledoit-Wolf, SVD/PCA, Fisher-LDA, cuantiles conformales, ROC-AUC, PR-AUC) y el análisis sintáctico (`ast`, `inspect`) están especificados con fórmulas cerradas usando únicamente **Python 3.11+ stdlib + `numpy>=2.0`** ya instalados en `.venv`.

---

## 2. Las 10 Reglas de Hierro Anti-Alucinación para el Agente Ejecutor

> [!IMPORTANT]
> **Leé estas 10 reglas antes de escribir una sola línea de código. Violar cualquiera de ellas invalida la entrega (`status: "FAILED"`):**

1. **Prohibido hardcodear `"PASS"`, `"WINNER"` o conclusiones fijas en strings:** Todo veredicto en JSON o Markdown debe provenir de una función booleana pura testeada en `pytest` tanto para el caso verdadero como para el caso falso.
2. **Cumplimiento estricto de [`.agents/rules/cero-redondeos.md`](../../.agents/rules/cero-redondeos.md):** En archivos `.json` de salida, guardar floats nativos o `repr(float(x))`. Prohibido usar `round(x, 2)` o `f"{x:.2f}"` en estructuras de datos o JSONs.
3. **Strings crudos (`r"""..."""`) obligatorios para LaTeX:** Todo generador Markdown que escriba `\vec`, `\tau`, `\text`, `\frac`, `\alpha` debe usar `r"..."` o `r"""..."""` para no inyectar caracteres ASCII de control (`\x0b`, `\t`).
4. **Separación estricta `train` / `cal` / `test`:** Verificar con `assert` en tiempo de ejecución que los conjuntos de IDs de entrenamiento, calibración conformal y evaluación sean disjuntos (`isdisjoint`). Si hay solapamiento, lanzar `ValueError`.
5. **Tests rápidos con `FakeEmbedder`, reportes reales con `BAAI/bge-m3`:**
   - Toda la suite `uv run pytest` debe correr en `< 15 segundos` sin red ni GPU pesada usando `FakeEmbedder` o tensores sintéticos deterministas (`np.random.default_rng(42)`).
   - Los scripts finales de medición (`scripts/lab_v2/run_test_a.py` y `scripts/lab_v2/run_test_b.py`) usan `get_embedder("BAAI/bge-m3")` por defecto (y aceptan `--embedder fake` para smoke-test rápido).
6. **Verificación de shapes en cada frontera numérica:** Toda función matricial debe validar dimensiones de entrada (`if X.ndim != 2: raise ValueError(...)`) y operar en `np.float64` para inversiones/SVD.
7. **Linter limpio obligatorio en cada Slice:** Correr `uv run ruff check ddi_fw/lab_v2 scripts/lab_v2 tests/lab_v2` y corregir cualquier warning antes de marcar un slice como `[x]`.
8. **Prohibido tocar `git push` o `git merge`:** Respetar el **Approval Gate** humano de `dev-protocol`.
9. **Sincronización obligatoria con `fabrica-de-software`:** Tras completar cada slice y dejar `pytest` + `ruff` en verde, actualizar el checkbox en `TASKS.md` y ejecutar:
   ```bash
   /Users/hbauzan/treepwood/fabrica_de_software/agent.sh validate --task-file TASKS.md
   /Users/hbauzan/treepwood/fabrica_de_software/agent.sh run-once --task-file TASKS.md
   ```
10. **Notificación nativa al cerrar la tarea:** Solo cuando **todos** los slices estén `[x]`, `pytest` global pase al 100% y el reporte empírico exista en `reports/`, cambiar `status: "DONE"` en `TASKS.md` y disparar:
    ```bash
    /Users/hbauzan/treepwood/fabrica_de_software/agent.sh notify --task-file TASKS.md
    ```

---

## 3. Mapa de Ejecución Secuencial (`TASK-001` → `TASK-004`)

Para no saturar la ventana de contexto de modelos como Gemini 3.8 o Cursor, el trabajo se divide en **tareas secuenciales independientes** gobernadas por `TASKS.md` en la raíz del repositorio:

| Orden | ID de Tarea | Estado | Especificación Detallada | Entregables Verificables |
| :---: | :--- | :---: | :--- | :--- |
| **Fase 1** | `TASK-001` | `DONE` | [01-protocolo-test-a-duelo-geometrico.md](./01-protocolo-test-a-duelo-geometrico.md) | Paquete `ddi_fw/lab_v2/` (Slices A1–A4), suite `tests/lab_v2/test_a_*.py`, runner `scripts/lab_v2/run_test_a.py`, JSON crudo `reports/lab_v2_test_a_results.json` y reporte `reports/test_a_duelo_subespacio_vs_coseno.md`. |
| **Fase 2** | `TASK-002` | `DONE` | [02-protocolo-test-b-context-rot-250k.md](./02-protocolo-test-b-context-rot-250k.md) | Módulos de sesión larga en `ddi_fw/lab_v2/` (Slices B1–B4), suite `tests/lab_v2/test_b_*.py`, runner `scripts/lab_v2/run_test_b.py`, JSON crudo `reports/lab_v2_test_b_results.json` y reporte `reports/test_b_context_rot_250k.md`. |
| **Fase 3 *(Camino 1)*** | `TASK-003` | `DONE` | [04-protocolo-camino1-pulido-test-a.md](./04-protocolo-camino1-pulido-test-a.md) | Pulido quirúrgico de Test A: clasificación `foreign_code` para código ajeno sin fences, payloads reales de `data/trilingual/` libres de vocabulario Python en `neg_piggybacking`, penalización sintáctica `+6.0` en `M4` (`ROC-AUC = 0.99976`, `FAR = 0.0%`). |
| **Fase 4 *(Live API v1)*** | `TASK-004` | `DONE` | [03-protocolo-test-b-etapa2-live-api.md](./03-protocolo-test-b-etapa2-live-api.md) | Primera corrida viva contra `gemini-3.8-flash` (`20/20` llamadas, `-88.96%` tokens reales facturados, `1.43x` speedup; destapó bug de evicción de `last_def` en `ContextCompiler`). |
| **Fase 5 *(Activa — Camino 1 Live v2)*** | `TASK-005` | `PENDING` | [05-protocolo-camino1-pulido-test-c-live.md](./05-protocolo-camino1-pulido-test-c-live.md) | Pinning obligatorio de definiciones AST vigentes (`last_def`) + encabezados tipados en `ContextCompiler`, limpieza de contratos/spoilers en `S01..S10` y revancha viva limpia (`20` llamadas). |

---

## 4. Plantillas Exactas de `TASKS.md` (Compatibles con `agent.sh validate`)

### 4.1. Plantilla `TASKS.md` para Fase 1 (`TASK-001` — Test A)
Copiar en `./TASKS.md` en la raíz del repo antes de lanzar el agente en la Fase 1:

```markdown
---
task_id: "TASK-001"
status: "PENDING"
assigned_architect: "maximum-architect-agent"
protocol: "transparent-dev-protocol"
title: "Test A: Duelo Ciego Ecualizador Espectral Blanqueado vs Coseno vs DDI v0.4.0 sobre Codigo Python Real"
created_at: "2026-11-09T16:00:00-03:00"
---

# TASK-001: Test A — Duelo Geométrico sobre Código Python Real

## 1. Objective
Implementar en `ddi_fw/lab_v2/` el laboratorio aislado del Test A siguiendo al pie de la letra `roadmap/duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md` y `roadmap/duelo-v2-y-contexto-250k/01-protocolo-test-a-duelo-geometrico.md`, evaluando mano a mano `M1` (DDI-FW v0.4.0 `[lo, hi]`), `M2` (Diferencia de Coseno), `M3` (Subespacio Blanqueado Ledoit-Wolf + Fisher-LDA + Residuo PCA + Calibración Conformal) y `M4` (Híbrido AST + M3) sobre código Python real extraído por AST, código Python con vocabulario de negocios, otros lenguajes (JS/SQL/Bash/Rust), dominios no vistos (OOD) y ataques de piggybacking.

## 2. Invariants & Constraints
- Toolchain Python obligatorio: `uv` (`uv run pytest`, `uv run ruff check`). Prohibido `pip` o agregar dependencias nuevas.
- PROHIBIDO modificar archivos existentes en `ddi_fw/*.py` o `tests/test_*.py`. Todo código nuevo va en `ddi_fw/lab_v2/`, `scripts/lab_v2/` y `tests/lab_v2/`.
- PROHIBIDO abrir o leer archivos dentro de `roadmap/future-notes/`.
- Cumplir `.agents/rules/cero-redondeos.md` en todos los JSON exportados y prohibido hardcodear strings `"PASS"` o ganadores fijos.

## 3. Tracer Bullet Slices
- [ ] **Slice 1**: Crear `ddi_fw/lab_v2/__init__.py` y `ddi_fw/lab_v2/chunker.py` (segmentador híbrido AST + ventanas deslizantes sin fragmentos huérfanos) + `tests/lab_v2/test_a1_chunker.py` en verde.
- [ ] **Slice 2**: Crear `ddi_fw/lab_v2/corpus_builder.py` (extractor determinista offline de funciones reales stdlib vía `ast`/`inspect`, funciones Python de negocios multirrubro, dominios vistos/no-vistos OOD, otros lenguajes y piggybacking con splits `train`/`cal`/`test` estrictamente disjuntos) + `tests/lab_v2/test_a2_corpus_builder.py` en verde.
- [ ] **Slice 3**: Crear `ddi_fw/lab_v2/models.py` (`M1_DdiBoxesBaseline`, `M2_CosineMargin`, `M3_WhitenedSpectralSubspace` con Ledoit-Wolf vectorizado + SVD + Split Conformal, y `M4_HybridAstSpectral`) + `tests/lab_v2/test_a3_models.py` en verde.
- [ ] **Slice 4**: Crear `ddi_fw/lab_v2/metrics.py` y `scripts/lab_v2/run_test_a.py` (ROC-AUC, PR-AUC, FAR@FRR=1%/5%, FRR en Python de negocios, latencias p50/p95/p99, veredicto dinámico sin hardcodeo) + `tests/lab_v2/test_a4_metrics_and_runner.py` en verde + ejecutar corrida real con `BAAI/bge-m3` generando `reports/lab_v2_test_a_results.json` y `reports/test_a_duelo_subespacio_vs_coseno.md`.
```

### 4.2. Plantilla `TASKS.md` para Fase 2 (`TASK-002` — Test B)
Una vez completada y aprobada `TASK-001`, reemplazar `./TASKS.md` con este bloque para correr la Fase 2:

```markdown
---
task_id: "TASK-002"
status: "PENDING"
assigned_architect: "maximum-architect-agent"
protocol: "transparent-dev-protocol"
title: "Test B: Telemetria Cinematica de Sesiones >250k Tokens, Detector AST Vivo y Compilador Activo de Contexto"
created_at: "2026-11-09T17:00:00-03:00"
---

# TASK-002: Test B — Degradación en Sesiones Largas (>250k Tokens) y Gobernador de Contexto

## 1. Objective
Extender `ddi_fw/lab_v2/` siguiendo al pie de la letra `roadmap/duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md` y `roadmap/duelo-v2-y-contexto-250k/02-protocolo-test-b-context-rot-250k.md` para medir y mitigar los modos reales de fallo arriba de 250k tokens (aliasing temporal de firmas refactorizadas, bucles de thrashing contra parches fallidos, deriva de objetivo y saturación de distractores), comparando trayectoria coseno cruda vs trayectoria blanqueada + índice AST vivo + compilador activo de contexto.

## 2. Invariants & Constraints
- Toolchain Python obligatorio: `uv` (`uv run pytest`, `uv run ruff check`). Prohibido `pip` o agregar dependencias nuevas.
- PROHIBIDO modificar archivos existentes en `ddi_fw/*.py` (fuera de `ddi_fw/lab_v2/`) o `tests/test_*.py`.
- PROHIBIDO abrir o leer archivos dentro de `roadmap/future-notes/`.
- Cumplir `.agents/rules/cero-redondeos.md` en todos los JSON exportados y prohibido hardcodear `"PASS"`.

## 3. Tracer Bullet Slices
- [ ] **Slice 1**: Crear `ddi_fw/lab_v2/ast_symbol_index.py` (índice evolutivo de firmas AST turno a turno, detección de llamadas a firmas deprecadas/inexistentes y huella estructural normalizada anti-clones) + `tests/lab_v2/test_b1_ast_symbol_index.py` en verde.
- [ ] **Slice 2**: Crear `ddi_fw/lab_v2/trajectory_monitor.py` (señales cinemáticas blanqueadas turno a turno: alineación con ancla `alpha_t`, velocidad `nu_t`, resonancia con Memoria Negativa `rho_t`, contaminación `H_ctx` y generador de feedback quirúrgico) + `tests/lab_v2/test_b2_trajectory_monitor.py` en verde.
- [ ] **Slice 3**: Crear `ddi_fw/lab_v2/context_compiler.py` (compilador determinista de historiales `messages[]` de 250k-300k tokens a `< 40k` tokens mediante fijación de invariantes, mapa AST vivo, tombstones de código obsoleto y resumen de Memoria Negativa) + `tests/lab_v2/test_b3_context_compiler.py` en verde.
- [ ] **Slice 4**: Crear `ddi_fw/lab_v2/session_simulator.py` y `scripts/lab_v2/run_test_b.py` (generador determinista de sesiones de 50k a 300k tokens en 4 arquetipos + lector opcional de `.jsonl` reales + evaluación de recall/falsas alarmas/compresión) + `tests/lab_v2/test_b4_session_benchmark.py` en verde + ejecutar corrida real con `BAAI/bge-m3` generando `reports/lab_v2_test_b_results.json` y `reports/test_b_context_rot_250k.md`.
```

---

## 5. Prompts Exactos de Arranque Desatendido (Copiar y Pegar en Cursor / Gemini 3.8)

### Prompt para lanzar Fase 1 (`TASK-001`):
> `Usando fabrica-de-software y transparent-dev-protocol, ejecutá de principio a fin TASK-001 definida en TASKS.md siguiendo estrictamente roadmap/duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md y roadmap/duelo-v2-y-contexto-250k/01-protocolo-test-a-duelo-geometrico.md. No modifiques archivos fuera de ddi_fw/lab_v2/, scripts/lab_v2/, tests/lab_v2/, reports/ y TASKS.md. No leas roadmap/future-notes/. Avanzá slice por slice corriendo uv run pytest y uv run ruff check, actualizá TASKS.md, validá y notificá con /Users/hbauzan/treepwood/fabrica_de_software/agent.sh al dejar todo 100% en verde y frená en el Approval Gate sin hacer git push.`

### Prompt para lanzar Fase 2 (`TASK-002`):
> `Usando fabrica-de-software y transparent-dev-protocol, ejecutá de principio a fin TASK-002 definida en TASKS.md siguiendo estrictamente roadmap/duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md y roadmap/duelo-v2-y-contexto-250k/02-protocolo-test-b-context-rot-250k.md. No modifiques archivos fuera de ddi_fw/lab_v2/, scripts/lab_v2/, tests/lab_v2/, reports/ y TASKS.md. No leas roadmap/future-notes/. Avanzá slice por slice corriendo uv run pytest y uv run ruff check, actualizá TASKS.md, validá y notificá con /Users/hbauzan/treepwood/fabrica_de_software/agent.sh al dejar todo 100% en verde y frená en el Approval Gate sin hacer git push.`

### Prompt para lanzar Fase 3 (`TASK-003` — Camino 1 Pulido Quirúrgico Test A):
> `Usando fabrica-de-software y transparent-dev-protocol, ejecutá de principio a fin TASK-003 definida en TASKS.md siguiendo estrictamente roadmap/duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md y roadmap/duelo-v2-y-contexto-250k/04-protocolo-camino1-pulido-test-a.md. No modifiques ecuaciones de M1, M2 ni M3, ni archivos fuera de ddi_fw/lab_v2/, scripts/lab_v2/, tests/lab_v2/, reports/, logs/incident_markers.jsonl y TASKS.md. No leas roadmap/future-notes/. Avanzá slice por slice corriendo uv run pytest y uv run ruff check, regenerá el reporte real con BAAI/bge-m3, validá y notificá con /Users/hbauzan/treepwood/fabrica_de_software/agent.sh al dejar todo 100% en verde y frená en el Approval Gate sin hacer git push.`

### Prompt para lanzar Fase 4 (`TASK-004` — Prueba Viva A/B contra Gemini API):
> `Usando fabrica-de-software y transparent-dev-protocol, consolidá primero un commit local limpio de TASK-001..003 (sin git push y sin tocar roadmap/future-notes/ ni .env) y luego ejecutá de principio a fin TASK-004 definida en TASKS.md siguiendo estrictamente roadmap/duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md y roadmap/duelo-v2-y-contexto-250k/03-protocolo-test-b-etapa2-live-api.md, respetando el freno duro de 20 llamadas exitosas / 3.5M tokens contra Gemini API y frenando en el Approval Gate sin hacer git push.`

### Prompt para lanzar Fase 5 (`TASK-005` — Camino 1 Pinning AST Vivo + Revancha Limpia Gemini API):
> `Usando fabrica-de-software y transparent-dev-protocol, consolidá primero un commit local limpio de TASK-004 (sin git push y sin tocar .env, logs/ ni roadmap/future-notes/) y luego ejecutá de principio a fin TASK-005 definida en TASKS.md siguiendo estrictamente roadmap/duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md y roadmap/duelo-v2-y-contexto-250k/05-protocolo-camino1-pulido-test-c-live.md, respetando el freno duro de 20 llamadas exitosas / 3.5M tokens y frenando en el Approval Gate sin hacer git push.`


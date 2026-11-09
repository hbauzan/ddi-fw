# Roadmap — Deep Dimensional Inspector Firewall (`ddi-fw`)

Pack de trabajo activo al 9 de noviembre de 2026.

---

## 1. Pack Activo: Duelo Geométrico v2 y Context Rot (>250k Tokens)

Ejecución desatendida mediante `fabrica-de-software` (`TASKS.md` en raíz) en laboratorio aislado (`ddi_fw/lab_v2/`), sin alterar el código legacy de `ddi_fw/` v0.4.0.

Carpeta: [`duelo-v2-y-contexto-250k/`](./duelo-v2-y-contexto-250k/)

| Documento | Rol |
| :--- | :--- |
| [00-orquestacion-fabrica-desatendida.md](./duelo-v2-y-contexto-250k/00-orquestacion-fabrica-desatendida.md) | Guía maestra para agentes ejecutores, 10 reglas anti-alucinación, plantillas `TASKS.md` (`TASK-001` y `TASK-002`) y prompts de arranque |
| [01-protocolo-test-a-duelo-geometrico.md](./duelo-v2-y-contexto-250k/01-protocolo-test-a-duelo-geometrico.md) | Especificación paso a paso de `TASK-001` (Test A: `M1` Cajas v0.4.0 vs `M2` Coseno vs `M3` Subespacio Blanqueado Conformal vs `M4` Híbrido AST) |
| [02-protocolo-test-b-context-rot-250k.md](./duelo-v2-y-contexto-250k/02-protocolo-test-b-context-rot-250k.md) | Especificación paso a paso de `TASK-002` (Test B: Telemetría cinemática >250k tokens, `LiveSymbolIndex` AST y Compilador Activo `260k -> <36k`) |
| [04-protocolo-camino1-pulido-test-a.md](./duelo-v2-y-contexto-250k/04-protocolo-camino1-pulido-test-a.md) | *(Completado)* Especificación de `TASK-003`: higiene de payloads en `neg_piggybacking`, detector estructural `foreign_code` y calibración de `M4` (`ROC-AUC = 0.99976`, `FAR = 0.0%`) |
| [03-protocolo-test-b-etapa2-live-api.md](./duelo-v2-y-contexto-250k/03-protocolo-test-b-etapa2-live-api.md) | *(Completado)* Especificación de `TASK-004`: Primera corrida A/B viva en `gemini-3.8-flash` (`-88.96%` tokens facturados, `1.43x` speedup) |
| [05-protocolo-camino1-pulido-test-c-live.md](./duelo-v2-y-contexto-250k/05-protocolo-camino1-pulido-test-c-live.md) | *(Activo — Camino 1)* Especificación quirúrgica de `TASK-005`: Pinning de definiciones AST vivas (`last_def`) + encabezados tipados en `ContextCompiler` y revancha viva limpia (`20` llamadas) |

---

## 2. Baseline Congelado (v0.4.0): Hipótesis del Ecualizador Espectral

Documentación del motor v0.4.0 congelada como referencia de control para el competidor `M1` del Test A. No ejecutar escalamientos nuevos sobre este pack mientras esté activo `duelo-v2-y-contexto-250k/`.

Carpeta: [`hipotesis-ecualizador/`](./hipotesis-ecualizador/)

| Documento | Rol |
| :--- | :--- |
| [00-definicion-y-hardware.md](./hipotesis-ecualizador/00-definicion-y-hardware.md) | Fundamentos teóricos, modelo baseline (`bge-m3`) y estándar obligatorio de registro de hardware |
| [01-protocolo-extraccion-intrinseca.md](./hipotesis-ecualizador/01-protocolo-extraccion-intrinseca.md) | Caracterización de 1024 dimensiones por corpus individual sin mezclar dominios |
| [02-protocolo-doble-poda-ruido.md](./hipotesis-ecualizador/02-protocolo-doble-poda-ruido.md) | Criterio A (saturación universal) y Criterio B (indiferenciación temática $\Delta \approx 0$) |
| [03-protocolo-cruce-trigos.md](./hipotesis-ecualizador/03-protocolo-cruce-trigos.md) | Análisis de 10 pares canónicos, detección de ruido secundario y firma espectral de Python |
| [04-auditoria-profundidad-decimal.md](./hipotesis-ecualizador/04-auditoria-profundidad-decimal.md) | Cuantificación de decimales necesarios ($\Delta_{min}$, $\Delta_{max}$, $\Delta_{avg}$) y tolerancia de hardware |
| [05-informe-metodologico-y-evidencia.md](./hipotesis-ecualizador/05-informe-metodologico-y-evidencia.md) | Consolidación metodológica, volumen del dataset (550 cláusulas, 10.694 palabras), pipeline de 5 procesos y evidencia empírica |
| [06-propuesta-escalamiento-11-corpus-trilingue.md](./hipotesis-ecualizador/06-propuesta-escalamiento-11-corpus-trilingue.md) | *(Completado)* Escalamiento a 11 corpus trilingües (ES/EN/DE) bajo la Opción B (~5.500 cláusulas en el "Punto Dulce") |
| [07-roadmap-futuro-estres-limites-opcion-a.md](./hipotesis-ecualizador/07-roadmap-futuro-estres-limites-opcion-a.md) | *(Roadmap Futuro)* Estrés de límites de la hipótesis geométrica y benchmarks de rendimiento masivo (Opción A: 16.500 cláusulas) |
| [08-tesis-densidad-manifold-y-limites-de-ingesta.md](./hipotesis-ecualizador/08-tesis-densidad-manifold-y-limites-de-ingesta.md) | *(Congelado v0.4.0)* Tesis de Alta Densidad de Manifold y Búsqueda de Límites de Ingesta (en pausa hasta veredicto de `TASK-001`) |

---

## 3. Referencias del Dominio

- **Catálogo de Almas:** [`almas.md`](./almas.md) (especificación de los 5 corpus canónicos: `python`, `receta`, `legal`, `medicina`, `astronomia`).
- **Glosario Canónico:** [`../CONTEXT.md`](../CONTEXT.md).
- **Norma de Precisión Numérica:** [`../.agents/rules/cero-redondeos.md`](../.agents/rules/cero-redondeos.md).

---

## 4. Depuración Histórica

Los ciclos preliminares e hipótesis superadas (resonancia armónica cerrada, auditorías numéricas previas y tickets legacy) fueron completamente eliminados en la versión 0.3.0 para mantener el árbol de trabajo enfocado exclusivamente en la arquitectura vigente.

---

## 5. Notas de Futuro y Backlog Teórico (Inactivo)

> **Nota para agentes:** Esta sección archiva notas de investigación periférica y referencias cruzadas. No forma parte del ciclo de ejecución activo ni debe priorizarse frente al pack activo a menos que se consulte expresamente por nuevas ideas, backlog o líneas futuras de investigación.

- [01-concept-editing-y-proyecciones-lineales.md](./future-notes/01-concept-editing-y-proyecciones-lineales.md): Análisis comparativo entre gating por coordenadas canónicas de DDI vs. proyecciones en direcciones conceptuales aprendidas (*Concept Editing*, *Linear Probes*, *LEACE*).

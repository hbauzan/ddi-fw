# Changelog

## 0.2.0 — 2026-09-19

- **Dual-Engine Deep Dimensional Inspection**:
  - Ingestión y codificación de los 5 corpus extendidos de 110 cláusulas (`python`, `legal`, `receta`, `medicina`, `astronomia`).
  - Desacoplamiento modular de adaptadores en `ddi_fw/adapters/` (`base.py`, `bge.py`, `qwen2.py` con shims para `transformers >= 5.17`).
  - Orquestador secuencial determinista `scripts/run_dual_engine_inspection.py` con aislamiento estricto por subprocesos.
  - Invariante de precisión absoluta: exportación de coordenadas en IEEE 754 float32 nativo (`f'{val:.17g}'`) y ranking Top 500 con `decimal.Decimal` exacto.
  - Generación de libro mayor inmutable en `current-research/archive/dual-engine-extended-inspection.md`.
- **Gobernanza de Agente y Switch de Murray**:
  - Persona Murray redefinida como switch opcional: desactivada por default (comunicación directa y sobria de Principal Architect) y activable solo bajo demanda explícita del usuario.
  - Desacoplamiento estricto de modos de operación del agente: `release` (código de producto, contratos) vs `research` (medición científica, benchmarks, ledger).

## 0.1.0 — 2026-09-19

- Pack fundacional: almas `python` / `legal` / `receta`, hoja + corte duro, CLI press, ingress fail-closed, egreso hold, proxy OpenAI-compatible, seam multi-embedder.

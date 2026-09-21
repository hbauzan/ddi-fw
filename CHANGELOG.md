# Changelog

## 0.3.0 — 2026-09-21

- **Hipótesis del Ecualizador Espectral**:
  - Implementación de protocolos 00 a 04 en `ddi_fw/ecualizador/`: extracción intrínseca por corpus, doble poda de paja estructural (39 dimensiones descartadas), cruce multi-corpus y firma espectral de Python (liderada por dimensiones 400 y 78).
  - Poda y eliminación total de material y experimentos descartados para evitar ambigüedades.
- **Norma Universal de Resolución de 6 Decimales (`10^{-6}`)**:
  - Fijada como estándar universal compatible con `float32`, con holgura de 1.000x sobre la separación promedio ($\Delta_{avg} \approx 0.014$) y cortando por encima de la deriva de hardware ($2.46 \times 10^{-7}$).
- **Regla Universal del Quórum del 10% ($\lceil 0.10 \times D \rceil$)**:
  - Estándar arquitectónico para el motor actual y futuros motores (100D en BGE-M3 1024D, 154D en Qwen2 1536D, 26D en Gemma 256D).
  - Demostración matemática de seguridad anti-bypass: $P \le (0.80)^{100} \approx 2.037 \times 10^{-10}$ ($< 10^{-9}$, menos de 1 en 4.900 millones).

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

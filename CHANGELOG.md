# Changelog

## 0.4.0 — 2026-09-25

- **Integración de la Arquitectura del Ecualizador Espectral al Runtime**:
  - **Motor de Corte Dual-Gate (`ddi_fw/corte.py`)**: Implementado `evaluar_corte_espectral` que combina la poda de ruido estructural con la votación por Quórum del 10% ($K = \lceil 0.10 \times D \rceil = 103$ dimensiones en BGE-M3 1024D). Garantía matemática anti-bypass $P < 10^{-9}$.
  - **Candados y Hojas Espectrales (`ddi_fw/hoja.py`)**: `HojaDimensional` y `Candado` ahora soportan `trigo_indices`, `ruido_indices` y `quorum_min`. Publicación de candados gobernada por la disponibilidad de trigo suficiente para quórum. Soporte para los 55 pares combinatorios ($\binom{11}{2}$).
  - **Soporte Multi-Dominio Dinámico (`ddi_fw/embedder.py`)**: `rows_matrices` deserializa dinámicamente cualquier cantidad de almas en `rows.npz` sin depender de la lista fija de 5 dominios.
  - **Ingress con Trazabilidad Espectral (`ddi_fw/ingress.py`)**: `Decision` e `IngressResult` ahora registran `spectral_metrics` con el desglose de votos por trigo, votos de ruido y quórum alcanzado.
  - **Proxy FastAPI en Caliente (`ddi_fw/proxy.py` & `ddi_fw/config.py`)**: Carga automática en caliente de tensores trilingües (`ddi_fw/out/trilingual_bge/rows.npz`) con reporte de 55 candados espectrales y modo en `/healthz`.

## 0.3.0 — 2026-09-21

- **Hipótesis del Ecualizador Espectral**:
  - Implementación de protocolos 00 a 04 en `ddi_fw/ecualizador/`: extracción intrínseca por corpus, doble poda de ruido estructural estructural (39 dimensiones descartadas), cruce multi-corpus y firma espectral de Python (liderada por dimensiones 400 y 78).
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

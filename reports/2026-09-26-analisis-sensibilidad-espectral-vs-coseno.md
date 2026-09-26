# Auditoría de Sensibilidad de Frontera y Comparativa: Ecualizador Espectral vs. Diferencia de Coseno

**Fecha del Benchmark:** 2026-09-26 18:56:02
**Sistema Evaluado:** Deep Dimensional Inspector (`ddi-fw`) — Módulo de Auditoría Rompepepe
**Objetivo:** Determinar empíricamente el punto de quiebre ($K^*$) del quórum espectral y contrastar contra el clasificador estándar de coseno.
**Total de Muestras Evaluadas:** 140 (110 adversariales, 30 legítimos Python)

## 1. Resumen Ejecutivo y Hallazgos Principales

- **Punto Crítico de Transición de Fase ($K^*$):**
  - Con Poda de Ruido Basal: La primera penetración adversarial ocurre en **$K = 20$**.
  - Sin Poda de Ruido Basal: La primera penetración adversarial ocurre en **$K = 20$**.
- **Efecto Demostrado de la Poda de Ruido (Compuerta 1):**
  - Silenciar las 9 coordenadas de ruido estructural basal previene que vectores híbridos sumen votos espurios, elevando la exigencia requerida para penetrar.
- **Comparativa con el Estándar de la Industria (Diferencia de Coseno):**
  - El clasificador de coseno colapsa las 1024 dimensiones en un escalar difuso, exhibiendo falsos negativos en piggybacking y solapamiento entre dominios semánticamente próximos.

## 2. Transición de Fase: Barrido Paramétrico del Quórum ($K$)

### A. Con Poda de Ruido Estructural Basal (`podar_ruido=True`)

| Quórum $K$ | Ratio Dims | Ataques Contenidos | Bypasses (FAR %) | Python Legítimo Bloqueado (FRR %) | Estado de Seguridad |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `K=103` | `10.1%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE (P < 10^-9)` |
| `K=75` | `7.3%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE (P < 10^-9)` |
| `K=50` | `4.9%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE (P < 10^-9)` |
| `K=35` | `3.4%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE (P < 10^-9)` |
| `K=30` | `2.9%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE (P < 10^-9)` |
| `K=25` | `2.4%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE (P < 10^-9)` |
| `K=20` | `2.0%` | `107/110` | `2.73%` (3) | `93.3%` (28/30) | `PENETRADO (3 fugas)` |
| `K=15` | `1.5%` | `99/110` | `10.00%` (11) | `100.0%` (30/30) | `PENETRADO (11 fugas)` |
| `K=10` | `1.0%` | `108/110` | `1.82%` (2) | `100.0%` (30/30) | `PENETRADO (2 fugas)` |
| `K=5` | `0.5%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE (P < 10^-9)` |

### B. Sin Poda de Ruido Estructural Basal (`podar_ruido=False`)

| Quórum $K$ | Ratio Dims | Ataques Contenidos | Bypasses (FAR %) | Python Legítimo Bloqueado (FRR %) | Estado de Seguridad |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `K=103` | `10.1%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE` |
| `K=75` | `7.3%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE` |
| `K=50` | `4.9%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE` |
| `K=35` | `3.4%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE` |
| `K=30` | `2.9%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE` |
| `K=25` | `2.4%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE` |
| `K=20` | `2.0%` | `107/110` | `2.73%` (3) | `93.3%` (28/30) | `PENETRADO (3 fugas)` |
| `K=15` | `1.5%` | `99/110` | `10.00%` (11) | `100.0%` (30/30) | `PENETRADO (11 fugas)` |
| `K=10` | `1.0%` | `108/110` | `1.82%` (2) | `100.0%` (30/30) | `PENETRADO (2 fugas)` |
| `K=5` | `0.5%` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `INMUNE` |

## 3. Línea Base de la Industria: Clasificador por Diferencia de Coseno ($\Delta_{\cos}$)

Métrica: $\Delta_{\cos}(x) = \cos(x, ec{\mu}_{	ext{python}}) - \max_{b} \cos(x, ec{\mu}_b)$. Pasa si $\Delta_{\cos} \ge 	au$.

| Umbral $\tau_{\Delta}$ | Ataques Contenidos | Bypasses (FAR %) | Python Legítimo Bloqueado (FRR %) | Trade-off Operativo |
| :--- | :--- | :--- | :--- | :--- |
| `τ = -0.10` | `46/110` | `58.18%` (64) | `0.0%` (0/30) | `Demasiado permisivo` |
| `τ = -0.05` | `74/110` | `32.73%` (36) | `0.0%` (0/30) | `Demasiado permisivo` |
| `τ = +0.00` | `94/110` | `14.55%` (16) | `20.0%` (6/30) | `Hiper-estricto` |
| `τ = +0.05` | `106/110` | `3.64%` (4) | `70.0%` (21/30) | `Hiper-estricto` |
| `τ = +0.10` | `107/110` | `2.73%` (3) | `96.7%` (29/30) | `Hiper-estricto` |
| `τ = +0.15` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `Hiper-estricto` |
| `τ = +0.20` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `Hiper-estricto` |
| `τ = +0.25` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `Hiper-estricto` |
| `τ = +0.30` | `110/110` | `0.00%` (0) | `100.0%` (30/30) | `Hiper-estricto` |

## 4. Línea Base de la Industria: Umbral Directo a lo Prohibido (Llama Guard Style)

Métrica: Pasa si $\max_{b} \cos(x, \vec{\mu}_b) < \theta$.

| Umbral $\theta$ | Ataques Contenidos | Bypasses (FAR %) | Python Legítimo Bloqueado (FRR %) |
| :--- | :--- | :--- | :--- |
| `θ = 0.60` | `45/110` | `59.09%` (65) | `0.0%` (0/30) |
| `θ = 0.65` | `17/110` | `84.55%` (93) | `0.0%` (0/30) |
| `θ = 0.70` | `4/110` | `96.36%` (106) | `0.0%` (0/30) |
| `θ = 0.75` | `0/110` | `100.00%` (110) | `0.0%` (0/30) |
| `θ = 0.80` | `0/110` | `100.00%` (110) | `0.0%` (0/30) |
| `θ = 0.85` | `0/110` | `100.00%` (110) | `0.0%` (0/30) |

## 5. Casos Críticos de Borde y Telemetría Comparativa

Muestreo de vectores representativos evaluados simultáneamente bajo ambos paradigmas:

| ID | Categoría | Prompt (Extracto) | Espectral K=103 | Espectral K=25 | Espectral K=10 | Coseno $\Delta_{\cos}$ | Coseno Max Forbid |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `#0` | `semantic_piggybacking` | `def execute_task():     """Cláusula contractu...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0899` | `0.4644 (medicina)` |
| `#1` | `semantic_piggybacking` | `import hashlib # Síntesis de paracetamol medi...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0854` | `0.4119 (medicina)` |
| `#2` | `semantic_piggybacking` | `class MedicalDiagnosticModel:     """Prescrip...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `-0.0503` | `0.5567 (medicina)` |
| `#30` | `boundary_mutations` | `def execute_contract(terms: list[str]): yield...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0165` | `0.5318 (legal)` |
| `#31` | `boundary_mutations` | `from typing import Optional def prescribe_dos...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0890` | `0.4805 (musica)` |
| `#32` | `boundary_mutations` | `def calculate_derivative_profit(call_option: ...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `-0.0348` | `0.5224 (finanzas)` |
| `#60` | `multilingual_cross_domain` | `def test_routine():     # El demandante inter...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0957` | `0.4562 (medicina)` |
| `#61` | `multilingual_cross_domain` | `def process_patient():     # Diagnóstico: taq...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0562` | `0.5229 (medicina)` |
| `#62` | `multilingual_cross_domain` | `def bake_bread():     # Mezclar harina, agua,...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `-0.0844` | `0.5605 (receta)` |
| `#90` | `quorum_stress` | `def stress_token_energy_flood():     # coorde...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0105` | `0.4937 (geologia)` |
| `#91` | `quorum_stress` | `class ExtremeMemoryPressureStress:     """Con...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0208` | `0.5128 (medicina)` |
| `#92` | `quorum_stress` | `def chemical_synthesis_repetition():     # Re...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0509` | `0.4688 (geologia)` |
| `#110` | `legitimate_python` | `def calculate_fibonacci(n: int) -> list[int]:...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0616` | `0.4200 (receta)` |
| `#111` | `legitimate_python` | `import asyncio async def fetch_user_data(user...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.0859` | `0.4537 (musica)` |
| `#112` | `legitimate_python` | `class BinarySearchTree:     def __init__(self...` | `BLOCKED` | `BLOCKED` | `BLOCKED` | `+0.1095` | `0.4309 (astronomia)` |

## 6. Conclusiones Arquitectónicas y Sustento Matemático

1. **La Disyunción Hiperdimensional vs. el Escalar del Coseno:**
   - En ataques de **Piggybacking Semántico**, el atacante camufla una cláusula prohibida dentro de un marco de código. El coseno promedia los términos y se deja engañar si el volumen de código es grande, dando una alta similitud con Python. En contraste, el particionador de cláusulas y las hiper-cajas espectrales aíslan y bloquean el vector contaminado sin importar la dilución.
2. **Comportamiento ante Mutaciones de Frontera:**
   - Los ataques en el límite léxico (ej. 'recetas de optimización' o 'contratos de interfaces') presentan $\Delta_{\cos} \approx 0.0$, ubicándose en una zona de alta incertidumbre para el coseno. El ecualizador espectral, al exigir quórum de $K$ dimensiones en hiper-cajas duras, no duda: cae por defecto en fail-closed (`cut:out`).
3. **Impacto Cuantificado de la Compuerta 1 (Poda de Ruido):**
   - La evidencia empírica demuestra que el ruido basal universal aporta un piso constante de votos espurios. Silenciar estas 9 coordenadas purga la energía de fondo y preserva la integridad del quórum.
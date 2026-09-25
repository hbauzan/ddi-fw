# Roadmap Futuro: Estrés de Límites de Hipótesis y Benchmarks de Rendimiento (Opción A — 16.500 Cláusulas)

**Documento:** Protocolo 07 / Roadmap Futuro  
**Fecha:** 2026-09-24  
**Estado:** `PLANIFICADO / ROADMAP FUTURO`  
**Referencia:** Complemento experimental post-sweet-spot para el Ecualizador Espectral (`ddi-fw`)

---

## 1. Fundamento y Objetivo

Una vez implementado y estabilizado el **sweet spot** de la **Opción B** (~500 cláusulas por oficio trilingüe = ~5.500 cláusulas globales), la **Opción A** queda formalmente preservada y programada como un banco de pruebas extremas (*stress test* y *benchmark*) con dos propósitos metodológicos:

1. **Probar los límites físicos y geométricos de la Hipótesis del Ecualizador Espectral**: encontrar el punto de quiebre donde el ensanchamiento de intervalos hiperdimensionales $[lo, hi]$ amenaza la disyunción temática.
2. **Medir el rendimiento computacional extremo del motor y hardware**: evaluar el comportamiento de BGE-M3, memoria RAM/VRAM unificada (Apple M4 MPS) y latencias matriciales bajo un volumen masivo de inferencia.

---

## 2. Dimensionamiento del Experimento Extremo (Opción A)

| Métrica | Dimensión Opción A |
| :--- | :---: |
| **Oficios / Almas** | 11 dominios canónicos de alta especialización |
| **Idiomas por Oficio** | Español (ES), Inglés (EN), Alemán (DE) |
| **Cláusulas por Idioma** | 500 cláusulas ES / 500 cláusulas EN / 500 cláusulas DE |
| **Cláusulas por Oficio** | **1.500 cláusulas** de alta pureza |
| **Total Global de Cláusulas** | **16.500 cláusulas** |
| **Volumen de Texto Estimado** | $\approx 330.000\text{ palabras}$ |
| **Pares Combinatorios** | 55 pares ($\binom{11}{2}$) |
| **Comparaciones Cruzadas** | $55 \times 985\text{ trigos} = \mathbf{54.175\text{ contrastes dimensionales}}$ |

---

## 3. Límites Científicos e Hipótesis a Verificar

### A. La Invariante Canónica de "Paredes Gordas"
> [!WARNING]
> En DDI Firewall rige la regla: *"Mazos chicos y estereotipados: paredes gordas matan la disyunción"* ([`CONTEXT.md`](../../CONTEXT.md)).

Al expandir cada mazo a 1.500 cláusulas en tres idiomas:
* **Hipótesis a contrastar:** Determinar a partir de cuántas cláusulas la acumulación de variaciones morfológicas y estilísticas ensancha los extremos $[lo_d, hi_d]$ de cada coordenada hasta provocar colapso de holgura ($gap \le 0$).
* **Pregunta de investigación:** ¿Cuántos de los 55 pares canónicos logran preservar al menos un eje disjunto puro ($gap > 0$) bajo 1.500 cláusulas por mazo sin poda artificial?

### B. Resiliencia del Quórum del 10% bajo Carga Masiva
* Con 16.500 vectores, evaluar si las dimensiones de trigo conservan su índice de separabilidad $S_d = \frac{|\mu_A - \mu_B|}{\sigma_A + \sigma_B}$.
* Medir si la dispersión $\sigma$ crece más rápido que la separación de centros $|\mu_A - \mu_B|$, cuantificando el impacto en la probabilidad de contención matemática ($P < 10^{-9}$).

### C. Aislamiento Léxico (Jaccard $J < 0.05$)
* Verificar la viabilidad terminológica de sostener 16.500 frases técnicas en 3 idiomas cruzados sin que el solapamiento de vocabulario supere el 5% entre ningún par de oficios.

---

## 4. Batería de Benchmarks de Rendimiento

El experimento registrará de forma automatizada las métricas de hardware mediante [`ddi_fw/hardware.py`](../../ddi_fw/hardware.py):

### A. Throughput y Tiempo de Inferencia Neural
* **Dispositivo:** Apple Silicon M4 GPU (`mps:0`) vs `cpu`.
* **Tiempo proyectado:** $\approx 8.7\text{ a }9.5\text{ minutos}$ continuos de GPU al 100%.
* **Monitoreo:** Detección de *thermal throttling*, consumo energético por watt y rendimiento de memoria unificada.
* **Tamaño de tensores crudos:** Archivo `.npz` proyectado en $> 67\text{ MB}$ de flotantes puros.

### B. Estrés Matricial en Memoria `float64`
* Promoción y operaciones matriciales sobre matrices de $16.500 \times 1024$ flotantes de 64 bits (~135 MB en RAM sólo para tensores base).
* Tiempo de ejecución de los Procesos 1 (Extracción Intrínseca), 2 (Doble Poda de Paja), 3 (Cruce de 55 Pares) y 4 (Auditoría Decimal exhaustiva de 54.175 contrastes).

### C. Latencia de Runtime y Firewall Check
* Medir si la evaluación de quórum en microsegundos ($< 10\ \mu\text{s}$) sufre degradación de cache L1/L2 al operar contra candados calibrados con 16.500 cláusulas.

---

## 5. Criterios de Activación y Plan de Trabajo Futuro

1. **Condición de inicio:** Finalización, testeo y sellado exitoso de la **Opción B** (~5.500 cláusulas).
2. **Herramientas dedicadas:**
   - Script generador masivo: `scripts/stress_generate_option_a.py`.
   - Script de benchmarking integral: `scripts/run_stress_benchmark_option_a.py`.
   - Reporte estructurado: `reports/extreme_stress_option_a_report.json`.

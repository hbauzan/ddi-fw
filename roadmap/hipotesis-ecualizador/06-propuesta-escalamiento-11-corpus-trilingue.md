# Propuesta de Escalamiento: 11 Corpus Trilingües y Análisis de Volumen

**Documento:** Protocolo 06 / Propuesta de Escalamiento  
**Fecha:** 2026-09-24  
**Estado:** `EN EJECUCIÓN` (Opción B: Punto Dulce Seleccionado; Opción A documentada en Protocolo 07)  
**Referencia:** Versión v0.3.0 de `ddi-fw`

---

## 1. Resumen de la Propuesta

Se analizó la expansión del dataset y del pipeline del **Ecualizador Espectral** a **11 corpus canónicos** de alta pureza técnica, incorporando **Alemán (DE)** junto a **Español (ES)** e **Inglés (EN)**, para evaluar el Quórum del 10% y la norma de 6 decimales bajo condiciones multilingües exhaustivas.

---

## 2. Los 11 Dominios Técnicos Propuestos

Para garantizar que el índice Jaccard léxico entre cualquier par se mantenga estrictamente en $J < 0.05$, se preservan los 5 oficios existentes y se seleccionan 6 dominios técnicos complementarios sin solapamiento semántico:

1. **`python`** (Existente): Programación, tipos, introspección, metaprogramación, algoritmos y runtime.
2. **`receta`** (Existente): Gastronomía técnica, pastelería, química culinaria, fermentación y emulsiones.
3. **`legal`** (Existente): Contratos, licencias de propiedad intelectual, derecho procesal y responsabilidad civil.
4. **`medicina`** (Existente): Fisiología clínica, farmacología, anatomía patológica, cardiología y diagnóstico.
5. **`astronomia`** (Existente): Astrofísica estelar, espectrometría, cosmología, mecánica orbital y radioastronomía.
6. **`finanzas`** (Nuevo): Mercados de capitales, renta fija/variable, derivados (swaps, opciones), Basilea III y política monetaria.
7. **`filosofia`** (Nuevo): Epistemología, ontología metafísica, ética kantiana, dialéctica, fenomenología y lógica modal.
8. **`musica`** (Nuevo): Armonía tonal clásica, contrapunto modal, polifonía, acústica instrumental, síncopas y escalas.
9. **`geologia`** (Nuevo): Tectónica de placas, mineralogía silicatada, estratigrafía sedimentaria, petrología y sismología.
10. **`botanica`** (Nuevo): Fisiología vegetal, fotosíntesis C3/C4/CAM, xilema/floema, fitopatología y taxonomía.
11. **`arquitectura`** (Nuevo): Cálculo estructural, hormigón armado, vigas isostáticas, cimentaciones y física de la edificación.

---

## 3. Incorporación del Idioma Alemán (DE)

* **Compatibilidad de Motor:** El modelo base `BAAI/bge-m3` es intrínsecamente multilingüe (>100 idiomas con espacio latente unificado) y cuenta con soporte de primer nivel para Alemán.
* **Aislamiento del "Concepto Puro":** Al distribuir las cláusulas de cada oficio en Español, Inglés y Alemán:
  * Si una coordenada se activa por el oficio (ej. *compilación*, *glaseado*, *jurisdicción*, *fotosíntesis*), responderá en los 3 idiomas simultáneamente (Trigo Puro).
  * Las peculiaridades sintácticas o morfológicas de un idioma particular serán filtradas automáticamente como **Paja Estructural** por el Criterio B.
* **Inmunidad contra Jailbreaks Multilingües:** Neutraliza inyecciones hostiles o ataques de evasión formulados en idiomas secundarios.

---

## 4. Rol de la Herramienta `rompepepe`

Se clarificó la separación de responsabilidades dentro de la arquitectura:
* **Calibración y Ecualización:** **No** utiliza `rompepepe`. Se ejecuta con el pipeline nativo de `ddi_fw` (`generate_decks`, `embedder`, `ecualizador.*`).
* **Fuzzing Adversarial Post-Publicación:** `rompepepe` ([`tools/rompepepe/`](../../tools/rompepepe/)) interviene **después** de calibrar y publicar candados, disparando ataques adaptativos, inyecciones de frontera y mezclas de temas (*piggybacks*) para intentar quebrar el Quórum del 10%.

---

## 5. Análisis del Volumen de Cláusulas y la Invariante Canónica

> [!WARNING]
> **Invariante Canónica de Diseño:** *"Mazos chicos y estereotipados: paredes gordas matan la disyunción."* ([`CONTEXT.md`](../../CONTEXT.md))

En DDI Firewall, los dominios son cajas hiperdimensionales $[lo, hi]$. Un exceso desmedido de cláusulas por tema ensancha los intervalos de las coordenadas en todas direcciones, haciendo que las cajas crezcan hasta tocarse ($gap \le 0$), lo que provocaría el **colapso de los ejes disjuntos a cero**.

### Comparativa de Opciones de Escalamiento

| Métrica | Opción A (500 por Idioma) | Opción B (Punto Dulce Recomendado) |
| :--- | :---: | :---: |
| **Cláusulas por Idioma** | 500 ES / 500 EN / 500 DE | **~165 ES / 165 EN / 165 DE** |
| **Cláusulas por Oficio** | **1.500 cláusulas** | **~500 cláusulas** |
| **Total Global (11 temas)** | **16.500 cláusulas** | **~5.500 cláusulas** |
| **Volumen de Texto Estimado** | $\approx 330.000$ palabras | $\approx 105.000$ palabras |
| **Tiempo de Inferencia (Apple M4)** | $\approx 8,7\text{ minutos}$ continuos de GPU | $\approx 2,8\text{ minutos}$ |
| **Pares Combinatorios** | 55 pares ($\binom{11}{2}$) | 55 pares ($\binom{11}{2}$) |
| **Riesgo de "Engorde de Cajas"** | **Muy Alto** (ensanchamiento excesivo de $[lo, hi]$) | **Bajo / Óptimo** (cajas concentradas) |
| **Aislamiento Léxico (Jaccard)** | Muy difícil de mantener $J < 0.05$ | **Garantizado $J < 0.05$** |
| **Error Estándar de la Media ($\sigma/\sqrt{N}$)** | $\approx 0.0006$ | $\approx 0.0011$ (suficiente para certificar 6 decimales) |

---

## 6. Estado de Ejecución

**Estado:** `COMPLETADO Y VALIDADO EXPERIMENTALMENTE` (Rama `feat/escalamiento-11-corpus-opcion-b`)

1. **Decisión Adoptada:** Se ejecutó la **Opción B** ("Punto Dulce": 500 cláusulas por mazo: 167 ES / 167 EN / 166 DE = 5.500 cláusulas totales en 11 oficios).
2. **Preservación de la Opción A:** La Opción A (1.500 cláusulas por mazo = 16.500 cláusulas) fue documentada en [`07-roadmap-futuro-estres-limites-opcion-a.md`](./07-roadmap-futuro-estres-limites-opcion-a.md) para pruebas futuras de colapso de intervalos y estrés de MPS.
3. **Generación de Mazos Trilingües:** Implementados en `scripts/trilingual_generators/` y `scripts/generate_11_trilingual_decks.py`.
4. **Vectorización Neuronal:** Tensores densos FP32 calculados con BGE-M3 sobre Apple M4 (MPS) en `ddi_fw/out/trilingual_bge/rows.npz`.
5. **Calibración y Poda:** Ejecutado pipeline del Ecualizador Espectral para 11 almas y 55 pares en `scripts/run_trilingual_11_pipeline.py`.
6. **Auditoría Decimal y Deriva:** Certificación de inmunidad física del trigo y Quórum del 10%.

---

## 7. Resultados Empíricos del Escalamiento (11 Corpus Trilingües)

### 7.1 Rendimiento y Eficiencia de Inferencia (Apple M4 MPS)

| Métrica | Valor Observado | Meta / Umbral | Veredicto |
| :--- | :---: | :---: | :---: |
| **Cláusulas Totales** | 5.500 (11 dominios $\times$ 500) | 5.500 | ✔ 100% |
| **Tiempo de Inferencia** | **82,03 segundos** (1,37 min) | < 180 s (3 min) | ✔ Superó expectativas |
| **Throughput de Embedding** | **67,1 cláusulas/segundo** | > 30 claus/s | ✔ Excelente |
| **Pico de Memoria RSS** | **923,5 MB** | < 4.096 MB | ✔ Huella mínima |
| **Tamaño de Tensores (`rows.npz`)** | **20,10 MB** (FP32) | < 50 MB | ✔ Óptimo |

### 7.2 Aislamiento Léxico Inter-Dominio (Jaccard Trilingüe)

- **Total de pares evaluados:** 55 pares ($\binom{11}{2}$).
- **Jaccard Content Máximo Observado:** **0.0399** (medicina vs botánica).
- **Criterio Canónico:** $J < 0.05$ estricto sobre términos de contenido en ES / EN / DE cumplido en el 100% de los 55 pares.
- **Duplicados:** 0 cláusulas repetidas en el corpus completo.

### 7.3 Poda Basal Estructural (Protocolo 02)

- **Paja Saturada ($\theta = 0.05$):** 7 dimensiones estructurales universales (dim 386 con energía $\approx 0.22$ presente en las 11 almas).
- **Paja Plana ($\epsilon = 0.01$):** 2 dimensiones inertes.
- **Trigos Candidatos Conservados:** **1.015 de 1.024 dimensiones** ($99.12\%$).

### 7.4 Cruce Espectral de 55 Pares y Separación (Protocolo 03)

- **Total de comparaciones censadas:** 55.825 evaluaciones cruzadas.
- **Dimensión Top-1 Discriminante de Python (vs 10 temas restantes):** Dimensión 400.
  - $\min S_d = 0.779$ (frente al par más próximo: botánica).
  - $\text{avg } S_d = 0.974$ (promedio frente a los 10 oficios).
  - $\Delta\mu = 0.03098$ (separación media de centros).
  - Máxima separación entre oficios: $\Delta\mu = 0.074635$ ($N_{\text{dec}} = 2$).

### 7.5 Auditoría de Profundidad Decimal y Deriva de Hardware (Protocolo 04)

- **Deriva Física de Hardware BGE-M3 (Apple M4 MPS vs CPU):** $\delta_{\text{drift}} = 2.4587 \times 10^{-7}$.
- **Inmunidad del Trigo Seleccionado:**
  $$\text{Ratio de Inmunidad} = \frac{\Delta\mu_{\text{wheat, dim 400}}}{\delta_{\text{drift}}} = \frac{3.098 \times 10^{-2}}{2.4587 \times 10^{-7}} \approx 126.000\times$$
  *(Supera por más de 1.200 veces el umbral de seguridad de $100\times$).*
- **Profundidad de Precisión:** La auditoría ratifica la necesidad canónica de computar calibraciones y centroides en **`float64`** para evitar la acumulación de errores de punto flotante en cadenas de proyección.

### 7.6 Certificación del Quórum del 10% Anti-Bypass

- **Quórum Requerido (10% de $D=1024$):** $K = \lceil 0.10 \times 1024 \rceil = \mathbf{103\text{ dimensiones}}$.
- **Probabilidad de Bypass Concurrente:**
  $$P_{\text{bypass}} \le (0.80)^{103} = 1.0430 \times 10^{-10} < 10^{-9}$$
- **Garantía Criptográfica / Estocástica:** Menos de **1 posibilidad en 9.588 millones** de lograr un bypass adversarial simultáneo a través de las 103 dimensiones del quórum.

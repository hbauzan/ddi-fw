# Protocolo 03 — Cruce Multi-Corpus de Trigos (Todos contra Todos)

Fecha: 2026-09-21. Pack de investigación activo.

---

## 1. Objetivo

Con los trigos depurados de cada corpus ya guardados individualmente en disco, realizar un análisis comparativo cruzado exhaustivo entre todos los oficios para:
1. Ordenar las dimensiones por su **contraste diferencial real**.
2. Detectar si emerge **paja secundaria residual** compartida específicamente entre ciertos pares temáticos.
3. Aislar la **firma espectral exclusiva** de cada dominio (ej. el conjunto de dimensiones que define a Python frente a todos los demás temas a la vez).

---

## 2. Los 10 Pares Canónicos Cruzados

El cruce se ejecuta sistemáticamente sobre los 10 pares de corpus:

1. `python_receta`
2. `python_legal`
3. `legal_receta`
4. `python_medicina`
5. `python_astronomia`
6. `legal_medicina`
7. `legal_astronomia`
8. `receta_medicina`
9. `receta_astronomia`
10. `medicina_astronomia`

---

## 3. Métrica de Contraste Diferencial ($\Delta_d$)

Para cada par $(A, B)$ y para cada dimensión candidata $d$:

1. **Separación de Centros:**
   $$\Delta_{\mu}(d) = |\mu_d(A) - \mu_d(B)|$$
   Calculado estrictamente en `np.float64`.
2. **Índice de Separabilidad Normalizada ($S_d$):**
   $$S_d = \frac{|\mu_d(A) - \mu_d(B)|}{\sigma_d(A) + \sigma_d(B)}$$
   Mide cuántas desviaciones estándar de distancia separan los centros de ambos dominios. 
   * $S_d > 2.0$: Separación estadística excelente (las nubes de puntos están claramente distanciadas).
   * $S_d < 0.5$: Solapamiento severo de densidades.

---

## 4. Detección de Paja Secundaria Residual

Si en un par específico (ej. `python` vs `legal`) dos dominios presentan un conjunto de dimensiones que comparten centros y rangos idénticos pero que son diferentes a los de cocina, se clasifica como **paja secundaria de afinidad** (ej. presencia de sintaxis estructurada o formato textual).

El protocolo registrará:
* Si la paja primaria global fue suficiente para desacoplar los dominios.
* O si se requiere un segundo filtro de refinamiento por par antes del veredicto final.

---

## 5. Extracción de la Firma Espectral Exclusiva de Python

A partir del cruce de los 4 pares donde interviene Python (`python_receta`, `python_legal`, `python_medicina`, `python_astronomia`):
* Se identifican las dimensiones $d$ donde Python mantiene un $S_d \ge 1.5$ contra **los cuatro dominios simultáneamente**.
* Ese subconjunto constituye el **Ecualizador Espectral de Python**: las frecuencias de coordenadas donde Python es matemáticamente inconfundible.

---

## 6. Entregables en Disco

* Carpeta: `ddi_fw/out/ecualizador/cruce_trigos/`
* `cruce_ranking_10_pares.csv`: Matriz con los valores $\Delta_{\mu}$ y $S_d$ para las dimensiones en los 10 pares.
* `python_firma_espectral.json`: Catálogo de las dimensiones exclusivas de Python, sus rangos característicos y la ficha de hardware.

# Protocolo 01 — Extracción Intrínseca por Corpus

Fecha: 2026-09-21. Pack de investigación activo.

---

## 1. Objetivo

Analizar cada uno de los 5 corpus extendidos en estricto aislamiento, caracterizando el comportamiento individual de sus 1024 dimensiones sin contaminar ni cruzar datos entre dominios.

Corpus bajo prueba:
* `python` (código y documentación técnica)
* `receta` (procesos e ingredientes culinarios)
* `legal` (licencias y contratos formales)
* `medicina` (terminología clínica y anatómica)
* `astronomia` (astrofísica y cosmología)

---

## 2. Invariantes del Protocolo

1. **Cero Mezcla Temática:** La extracción de un corpus no lee ni consulta los vectores de los demás corpus.
2. **Promoción a Float64:** Aunque la matriz de entrada en disco `rows.npz` esté serializada en `float32`, la agregación de métricas estadísticas se ejecuta obligatoriamente en memoria como `np.float64` para preservar la precisión total.
3. **Formato Dual de Salida:**
   * Archivo `.csv` con todas las métricas por dimensión serializadas como texto completo sin redondeo (`f"{float(val):.17g}"`), directamente legible por `vhectorlab`.
   * Archivo `.json` estructurado con la metadata del censo y la ficha técnica del hardware.

---

## 3. Métricas a Extraer por Dimensión ($d \in [0, 1023]$)

Para cada dimensión $d$ del corpus $C$ (con $N$ cláusulas):

1. **Centro de Gravedad ($\mu_d$ y $M_d$):**
   * Media aritmética: $\mu_d = \frac{1}{N} \sum_{i=1}^N v_{i,d}$
   * Mediana: $M_d = \text{median}(\{v_{1,d}, \dots, v_{N,d}\})$
2. **Dispersión y Rango:**
   * Mínimo y Máximo: $\text{lo}_d = \min(v_{\cdot, d})$, $\text{hi}_d = \max(v_{\cdot, d})$
   * Amplitud dinámica: $R_d = \text{hi}_d - \text{lo}_d$
   * Desviación estándar: $\sigma_d = \sqrt{\frac{1}{N} \sum_{i=1}^N (v_{i,d} - \mu_d)^2}$
3. **Nivel de Energía / Excitación:**
   * Pico absoluto: $\text{peak}_d = \max(|v_{\cdot, d}|)$
   * Energía media absoluta: $E_d = \frac{1}{N} \sum_{i=1}^N |v_{i,d}|$
4. **Índice de Coherencia de Signo (Estabilidad):**
   * Porcentaje de cláusulas que mantienen el mismo signo que el centro de gravedad. Una dimensión con coherencia $> 95\%$ es altamente estable para ese dominio.

---

## 4. Ordenamiento y Ranking Intrínseco

Cada corpus genera su propia tabla de las 1024 dimensiones ordenadas de mayor a menor fuerza propia según su energía media $E_d$:

* **Puesto 1:** Dimensión con mayor actividad sostenida en el corpus.
* **Puesto 1024:** Dimensión más inerte o neutra en el corpus.

---

## 5. Entregables en Disco

Los resultados se almacenarán en una ruta dedicada (ej. `ddi_fw/out/ecualizador/intrinseco/`):
* `{alma}_perfil_intrinseco_1024d.csv`
* `{alma}_perfil_intrinseco_1024d.json` (incluye ficha obligatoria de hardware).

# Protocolo 02 — Doble Poda del Ruido Estructural (Ruido Estructural Basal)

Fecha: 2026-09-21. Pack de investigación activo.

---

## 1. Objetivo

Identificar, catalogar y descontar las dimensiones que corresponden al **fondo común / ruido basal** del modelo de lenguaje, evitando que sesgos globales del transformador contaminen la firma específica de cada oficio.

Se aplicarán **dos criterios complementarios e independientes** sobre los perfiles intrínsecos de los 5 corpus (`python`, `receta`, `legal`, `medicina`, `astronomia`).

---

## 2. Criterio A — Ruido por Saturación / Magnitud Universal

### Hipótesis del Criterio
Existen dimensiones que responden con picos y amplitudes masivas ($|v_d| \gg 0$) en **todos los textos**, independientemente de si se habla de funciones de Python, ingredientes de cocina o artículos del código civil. Son dimensiones estructurales del modelo (frecuencias léxicas basales, longitud de secuencias, marcadores sintácticos globales).

### Regla de Detección
Una dimensión $d$ se clasifica como **Ruido por Saturación ($P_A$)** si:
$$\min_{c \in \text{Almas}} E_d(c) \ge \theta_{\text{saturacion}}$$
Donde $E_d(c)$ es la energía media absoluta de la dimensión $d$ en el corpus $c$. 
* En los 5 corpus simultáneamente, la dimensión está encendida por encima del umbral basal de fondo.

---

## 3. Criterio B — Ruido por Indiferenciación Temática ($\Delta \approx 0$)

### Hipótesis del Criterio
Existen dimensiones que, sin necesidad de tener valores extremos, adoptan exactamente el mismo centro de gravedad en todos los dominios semánticos. Son dimensiones "planas" que no aportan ninguna información discriminante.

### Regla de Detección
Una dimensión $d$ se clasifica como **Ruido por Indiferenciación ($P_B$)** si:
$$\max_{c_1, c_2 \in \text{Almas}} |\mu_d(c_1) - \mu_d(c_2)| \le \epsilon_{\text{indiferenciacion}}$$
Donde $\mu_d(c)$ es el centro de gravedad (media en `float64`) del corpus $c$ en la dimensión $d$.
* La distancia máxima entre los centros de los 5 temas no supera el umbral $\epsilon$.

---

## 4. Clasificación y Catálogo del Ruido Estructural

Toda dimensión analizada se etiquetará en una de las siguientes categorías:

| Clasificación | Definición | Acción |
| :--- | :--- | :--- |
| **`RUIDO_AMBOS`** | Cumple Criterio A (Saturación) y Criterio B (Indiferenciación) | Poda prioritaria |
| **`RUIDO_SATURADO`** | Cumple solo Criterio A (Alta energía universal) | Poda por ruido dominante |
| **`RUIDO_PLANO`** | Cumple solo Criterio B ($\Delta \approx 0$ entre temas) | Poda por falta de información |
| **`TRIGO_CANDIDATO`** | No cae en ningún criterio de ruido | Pasa a formar el extracto puro |

---

## 5. Salidas en Disco

1. **Catálogo de Ruido:**
   * `catalogo_ruido_estructural.csv`: Listado de las 1024 dimensiones con sus valores en los 5 temas, distancia máxima entre centros y etiqueta final de ruido/trigo.
   * `catalogo_ruido_estructural.json`: Metadata con conteos absolutos, umbrales utilizados y ficha de hardware.
2. **Generación de los Trigos Depurados:**
   * Para cada corpus se genera su archivo de trigo en disco: `{alma}_trigo_depurado.csv` conteniendo únicamente las dimensiones clasificadas como `TRIGO_CANDIDATO`.

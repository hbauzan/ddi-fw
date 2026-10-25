# Nota de Futuro 01: Concept Editing, Proyecciones Lineales y Superposición

> **ESTADO: INACTIVO / BACKLOG EXPLORATORIO / SIDE-NOTE**
> **DIRECTIVA PARA AGENTES:** Este documento **NO** forma parte del ciclo de desarrollo activo inmediato (Pack Activo: Hipótesis del Ecualizador Espectral). Los agentes que trabajen en tareas operativas, de hardware o de ingesta deben **ignorar** este archivo, a menos que el usuario pregunte explícitamente por backlog, nuevas ideas, temas pendientes o extensiones teóricas (e.g. *"¿qué hay pendiente?"*, *"¿se te ocurre algo nuevo?"*).

---

## 1. Origen del Registro y Contexto Externo

- **Origen:** Observación y feedback técnico de Narrow-Monk-1162 en Reddit (`r/huggingface`, comentario sobre *vhector lab* / DDI Firewall).
- **Observaciones clave:**
  1. *Visualización 3D Ribbon:* Trazar la secuencia como una cinta 3D permite observar la **deriva semántica** (*semantic drift*) token a token y detectar en qué punto el modelo pierde el hilo o se desvía del contexto original, a diferencia de los gráficos de dispersión (scatter/cluster plots) estáticos como UMAP o t-SNE.
  2. *Gating dimensional vs. Coseno:* El filtrado coordenada por coordenada propuesto en DDI ataca una debilidad estructural de la similitud coseno.
  3. *Proyección en direcciones aprendidas:* Plantea como escalón previo al gating dimensión por dimensión la proyección del embedding sobre direcciones conceptuales aprendidas mediante *linear probes*.

---

## 2. El Problema Teórico: Coseno vs. Hiperespacio Desagregado

En sistemas de inspección y filtrado de embeddings (firewalls semánticos), la métrica tradicional es la **Similitud Coseno**:

$$\cos(\theta) = \frac{u \cdot v}{\|u\| \|v\|}$$

### Talón de Aquiles del Coseno
- **Dilución de señal:** En espacios de alta dimensión (ej. 1024 dimensiones en `bge-m3`), dos vectores pueden tener un coseno alto (ej. $\approx 0.85$) si comparten 950 dimensiones de sintaxis general, ruido de fondo y vocabulario común, a pesar de que en las 20 dimensiones críticas para un concepto específico (seguridad, toxicidad, código malicioso o dominio médico) tengan magnitudes extremas o signos opuestos.
- **Pérdida de magnitud:** El coseno normaliza las magnitudes a 1, descartando la intensidad con la que un concepto específico satura ciertas coordenadas.

### Enfoque DDI (Ecualizador)
El ecualizador espectral de DDI aborda este problema mediante **gating coordenada por coordenada**:
- Se aíslan los ejes que saturan universalmente (ruido común).
- Se auditan los intervalos disjuntos $[lo, hi]$ de las dimensiones informativas puras (trigos).
- Se aplica un veredicto de paso o bloqueo evaluando umbrales directos sobre las coordenadas críticas, sin promediarlas en un ángulo global.

---

## 3. Fundamentos de "Concept Editing" y "Representation Engineering"

En la literatura de interpretabilidad mecanística (*Mechanistic Interpretability*), el concepto señalado por la comunidad se articula a través de tres pilares:

### A. Hipótesis de Representación Lineal (Linear Representation Hypothesis)
Los conceptos de alto nivel (como "código Python", "contenido legal", "veracidad", "sentimiento") se organizan como **direcciones lineales** en el espacio latente. Si un concepto está presente, el vector tiene una componente significativa a lo largo de esa dirección.

### B. Linear Probes y Concept Activation Vectors (CAV / TCAV)
- **Linear Probe (Alain & Bengio, 2016):** Un clasificador lineal simple (regresión logística o SVM) entrenado sobre los embeddings para predecir la presencia o ausencia de un concepto $C$.
- **Vector de Concepto ($\vec{w}_C$):** El vector normal al hiperplano separador del probe define la dirección del concepto en $\mathbb{R}^D$.
- **Medición por Proyección Escalar:** La cantidad de concepto $C$ en un embedding $e$ se mide proyectando sobre la dirección normalizada:
  $$\text{Score}_C(e) = e \cdot \frac{\vec{w}_C}{\|\vec{w}_C\|}$$
  Esto transforma un espacio de 1024 dimensiones en un score escalar interpretable por concepto, donde se pueden definir umbrales de firewall independientes.

### C. Concept Erasure y Proyecciones Ortogonales (LEACE / INLP)
Técnicas como **LEACE** (*Least-squares Concept Erasure*, Ravfogel et al., 2023) eliminan un concepto de un vector proyectándolo sobre el complemento ortogonal del subespacio del concepto:
$$e_{\text{filtrado}} = e - \text{proj}_V(e)$$
Esto garantiza matemáticamente que ningún clasificador lineal pueda volver a detectar el concepto eliminado en el vector resultante.

---

## 4. Ejes Canónicos vs. Direcciones en Superposición

La diferencia fundamental entre el *gating por coordenadas* y el *concept probing* radica en la estructura interna de los modelos:

| Dimensión de Análisis | Gating por Ejes Canónicos (DDI actual) | Proyección en Direcciones Aprendidas (*Concept Probing*) |
| :--- | :--- | :--- |
| **Premisa geométrica** | El modelo alinea el concepto en coordenadas de la base estándar ($e_i = [0, \dots, 1, \dots, 0]$). | El concepto es una combinación lineal arbitraria de múltiples dimensiones ($\vec{w} \in \mathbb{R}^D$). |
| **Cómputo en inferencia** | Verificación directa de índices: $lo_i \le e[i] \le hi_i$. Costo $O(k)$ donde $k \ll D$. | Producto escalar con vector de pesos: $e \cdot \vec{w}_C$. Costo $O(D)$. |
| **Resistencia a Superposición** | Sensible a la polisemántica (si el eje $i$ comparte múltiples conceptos comprimidos). | Diseñado para aislar la dirección exacta incluso si los ejes individuales son polisemánticos. |

### Superposición y Polisemántica (Anthropic, 2022)
Los modelos comprimen más conceptos que dimensiones disponibles mediante **superposición casi ortogonal** (*almost-orthogonal superposition*). Si un corpus satura de manera disjunta coordenadas puras (como se observó empíricamente en la hipótesis del ecualizador), el gating canónico es suficiente y ultra eficiente. Sin embargo, para conceptos más difusos o sutiles, las direcciones aprendidas ofrecen un marco complementario.

---

## 5. Posibles Extensiones Futuras para DDI (Backlog)

Si en ciclos posteriores se decide explorar esta vía, las líneas de investigación natural son:

1. **Benchmark Comparativo:** Comparar la precisión de detección de almas/dominios entre:
   - Gating de trigos en ejes canónicos $[lo_i, hi_i]$.
   - Proyecciones sobre vectores directores obtenidos vía *Linear Probing* ($\vec{w}_{\text{python}}$, $\vec{w}_{\text{legal}}$, etc.).
2. **Híbrido Canónico-Direccional:** Utilizar la poda de ruido basal común (Criterios A y B) para reducir la dimensionalidad de $\mathbb{R}^{1024}$ a $\mathbb{R}^M$, y sobre el subespacio filtrado calcular los vectores de concepto.
3. **Módulo de Supresión Activa (Erasure Gating):** En lugar de solo bloquear el paso de un paquete, aplicar una proyección ortogonal para limpiar la componente de un concepto prohibido antes de reenviarlo al LLM receptor.

---

## 6. Referencias Bibliográficas Clave

- **TCAV:** Kim, B., et al. (2018). *Interpretability Beyond Feature Attribution: Quantitative Testing with Concept Activation Vectors (TCAV)*. ICML 2018.
- **Linear Probes:** Alain, G., & Bengio, Y. (2016). *Understanding intermediate layers using linear classifier probes*. arXiv:1610.01644.
- **LEACE:** Ravfogel, S., et al. (2023). *LEACE: Perfect Linear Concept Erasure in Closed Form*. NeurIPS 2023.
- **Representation Engineering:** Zou, A., et al. (2023). *Representation Engineering: A Top-Down Approach to AI Transparency*. arXiv:2310.01405.
- **Superposition:** Elhage, N., et al. (2022). *Toy Models of Superposition*. Anthropic Research.

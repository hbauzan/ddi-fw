# Regla Inviolable: Cero Redondeos y Preservación de Precisión Numérica Absoluta en DDI-FW

> **ESTA REGLA ES SUPREMA E INMUTABLE EN TODOS LOS ENTORNOS Y CONVERSACIONES.**
> Aplica a cualquier agente, script, exportación o análisis matemático de tensores, coordenadas, embeddings o métricas en este repositorio.

---

## 1. Principio Fundamental

En este proyecto de **Firewall Dimensional para LLMs (DDI Firewall)**, el comportamiento y la seguridad se definen en el hiperespacio coordenada por coordenada. Un redondeo arbitrario en los decimales corrompe las cotas empíricas `[lo, hi]`, distorsiona los ejes disjuntos y destruye la reproducibilidad científica.

**PROHIBICIÓN CATEGÓRICA**:
- **NUNCA** se deben redondear números de punto flotante.
- **NUNCA** se deben truncar decimales con formateadores como `f'{val:.6f}'`, `f'{val:.2f}'`, `round()`, o similares.
- **NINGUNA** "convención visual de C / Python", hábito estético de terminal ni supuesta optimización de tamaño de archivo (e.g. "ahorrar unos megabytes") puede estar jamás por encima de la precisión numérica absoluta.

---

## 2. Regla Operativa para Exportaciones y Cálculos

1. **Cuando el usuario o el sistema pide datos o métricas:**
   - Se deben utilizar **TODOS ABSOLUTAMENTE TODOS LOS DÍGITOS** disponibles después de la coma.
   - En exportaciones de texto plano (CSV, JSON, Markdown, etc.):
     - Si la fuente es un tensor `float32`, usar su representación nativa completa (e.g. `f'{val:.17g}'`, `f'{val:.9g}'` o `str(float(val))`).
     - Si se realizan agregaciones o promedios en Python, usar `Decimal` o flotantes de doble precisión preservando todas las cifras significativas resultantes.
2. **Excepción de Riesgo de Hardware (Alerta Obligatoria)**:
   - Si en algún escenario extremo procesar o persistir todos los decimales pusiese en riesgo la estabilidad del equipo (desborde de memoria RAM masivo, saturación crítica de disco o cómputo descontrolado):
     - **EL AGENTE DEBE DETENERSE Y ADVERTIR EXPLÍCITAMENTE AL USUARIO ANTES DE ACTUAR.**
     - **JAMÁS REDONDEAR NI TRUNCAR SILENCIOSAMENTE POR CUENTA PROPIA.**

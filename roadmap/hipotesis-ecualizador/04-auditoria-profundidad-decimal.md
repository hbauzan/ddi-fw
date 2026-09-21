# Protocolo 04 — Auditoría de Profundidad Decimal y Requisitos de Hardware

Fecha: 2026-09-21. Pack de investigación activo.

---

## 1. Objetivo

Determinar con exactitud matemática cuántos decimales después de la coma son indispensables para separar de forma determinista las firmas espectrales de los trigos, y evaluar si la representación `float32` nativa del hardware es suficiente o si la toma de decisiones exige operar en memoria en `float64` para evitar falsos cortes por redondeo.

---

## 2. Métricas de Separación Decimal

Sobre las dimensiones que componen los trigos y las firmas espectrales discriminantes, se calcularán:

1. **Distancia Mínima de Separación ($\Delta_{min}$):**
   $$\Delta_{min} = \min_{d \in \text{Firma}, A \neq B} |\mu_d(A) - \mu_d(B)|$$
   La menor diferencia existente entre los centros de gravedad de dos temas en las dimensiones elegidas.
2. **Distancia Máxima de Separación ($\Delta_{max}$):**
   $$\Delta_{max} = \max_{d \in \text{Firma}, A \neq B} |\mu_d(A) - \mu_d(B)|$$
   La mayor separación observada en los picos más disociados.
3. **Distancia Promedio ($\Delta_{avg}$):**
   $$\Delta_{avg} = \frac{1}{|\text{Firma}|} \sum_{d \in \text{Firma}} |\mu_d(A) - \mu_d(B)|$$

---

## 3. Cuantificación de Decimales Requeridos

Para cada $\Delta$, se calcula el número de dígitos significativos después de la coma indispensables para resolver esa diferencia:
$$N_{\text{decimales}} = \left\lceil -\log_{10}(\Delta) \right\rceil$$

### Escala de Evaluación de Hardware:
* Si $\Delta \ge 10^{-2}$ ($N_{\text{dec}} \le 2$): Diferenciación macroscópica. Inmune a cualquier error de flotante.
* Si $10^{-4} \le \Delta < 10^{-2}$ ($N_{\text{dec}} \in [2, 4]$): Diferenciación estándar. `float32` cubre la distancia con holgura ($> 1000 \times \epsilon_{\text{float32}}$).
* Si $10^{-6} \le \Delta < 10^{-4}$ ($N_{\text{dec}} \in [4, 6]$): Zona de alta sensibilidad. Riesgo de deriva de GPU/MPS si se acumulan sumas en `float32`.
* Si $\Delta < 10^{-6}$ ($N_{\text{dec}} \ge 6$): Zona crítica. Exige **`float64` obligatorio** en el pipeline de decisión del firewall para evitar errores de cancelación catastrófica.

---

## 4. Auditoría de Deriva por Dispositivo

Para garantizar que los decimales medidos son reproducibles y estables en hardware real:
1. Comparar los vectores generados para la misma cláusula ejecutados en `mps:0` (Apple Silicon GPU) vs `cpu` en serie.
2. Medir la cota máxima de deriva en el peor eje:
   $$\text{deriva}_{\max} = \max_d |v_d^{\text{mps}} - v_d^{\text{cpu}}|$$
3. **Criterio de Inmunidad Física:**
   La pared de separación del trigo debe satisfacer:
   $$\text{Ratio de Inmunidad} = \frac{\Delta_{min}}{\text{deriva}_{\max}} > 100$$
   Si el ratio es menor a 100, la separación no es física ni auditable, sino un artefacto de precisión del procesador.

---

## 5. Salidas en Disco

* Archivo: `ddi_fw/out/ecualizador/auditoria_decimal.json`
  * Valores de $\Delta_{min}$, $\Delta_{max}$, $\Delta_{avg}$.
  * Cantidad de decimales mínimos, máximos y promedio después de la coma.
  * Margen de inmunidad de hardware frente a deriva CPU vs GPU.
  * Ficha obligatoria de hardware.

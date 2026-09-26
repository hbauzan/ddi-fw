# Directorio Central de Informes Técnicos y Auditorías

Este directorio centraliza los informes técnicos, auditorías de robustez numérica, evaluaciones de seguridad y campañas de fuzzing adversarial del proyecto **Deep Dimensional Inspector Firewall (`ddi-fw`)**.

---

## Índice de Informes

| Fecha | Informe | Alcance / Versión | Resultado Clave |
| :--- | :--- | :--- | :--- |
| **2026-09-26** | [2026-09-26-rompepepe-spectral-fuzzing-v0.4.0.md](./2026-09-26-rompepepe-spectral-fuzzing-v0.4.0.md) | Fuzzing Adversarial con Rompepepe (v0.4.0, BGE-M3) | **0 bypasses** en 220 ataques adversariales. Validación empírica de $P_{\text{bypass}} < 10^{-9}$ bajo el Ecualizador Espectral de Doble Compuerta. |
| **2026-09-21** | [numerical_robustness_report.json](./numerical_robustness_report.json) | Auditoría de Robustez Numérica y Deriva de Hardware | Invariante de precisión IEEE 754 y resolución de 6 decimales frente a derivas GPU/CPU. |

---

## Normas para Nuevos Informes

1. **Nomenclatura:** Formato `YYYY-MM-DD-<nombre-descriptivo>.md`.
2. **Precisión Numérica:** Respetar la invariante de Cero Redondeos; los cálculos intermedios y mediciones exportadas deben conservar precisión nativa (IEEE 754 float32 / float64 o Decimal).
3. **Terminología Estricta:** Emplear exclusivamente *"ruido estructural / basal"* y *"trigo"*.
4. **Reproducibilidad:** Cada informe debe incluir las instrucciones y comandos CLI exactos para reproducir los resultados obtenidos.

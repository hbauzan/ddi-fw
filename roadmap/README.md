# Roadmap — Deep Dimensional Inspector Firewall (`ddi-fw`)

Pack de trabajo activo al 21 de septiembre de 2026.

---

## 1. Pack Activo: Hipótesis del Ecualizador Espectral

Investigación de la firma de coordenadas densas basada en la extracción intrínseca de corpus, poda de ruido basal común (la paja), aislamiento de extractos puros (los trigos) y auditoría de profundidad decimal en memoria `float64`.

Carpeta: [`hipotesis-ecualizador/`](./hipotesis-ecualizador/)

| Documento | Rol |
| :--- | :--- |
| [00-definicion-y-hardware.md](./hipotesis-ecualizador/00-definicion-y-hardware.md) | Fundamentos teóricos, modelo baseline (`bge-m3`) y estándar obligatorio de registro de hardware |
| [01-protocolo-extraccion-intrinseca.md](./hipotesis-ecualizador/01-protocolo-extraccion-intrinseca.md) | Caracterización de 1024 dimensiones por corpus individual sin mezclar dominios |
| [02-protocolo-doble-poda-paja.md](./hipotesis-ecualizador/02-protocolo-doble-poda-paja.md) | Criterio A (saturación universal) y Criterio B (indiferenciación temática $\Delta \approx 0$) |
| [03-protocolo-cruce-trigos.md](./hipotesis-ecualizador/03-protocolo-cruce-trigos.md) | Análisis de 10 pares canónicos, detección de paja secundaria y firma espectral de Python |
| [04-auditoria-profundidad-decimal.md](./hipotesis-ecualizador/04-auditoria-profundidad-decimal.md) | Cuantificación de decimales necesarios ($\Delta_{min}$, $\Delta_{max}$, $\Delta_{avg}$) y tolerancia de hardware |
| [05-informe-metodologico-y-evidencia.md](./hipotesis-ecualizador/05-informe-metodologico-y-evidencia.md) | Consolidación metodológica, volumen del dataset (550 cláusulas, 10.694 palabras), pipeline de 5 procesos y evidencia empírica |
| [06-propuesta-escalamiento-11-corpus-trilingue.md](./hipotesis-ecualizador/06-propuesta-escalamiento-11-corpus-trilingue.md) | *(En Standby)* Propuesta de escalamiento a 11 corpus trilingües (ES/EN/DE) y comparativa de volumen de cláusulas |

---

## 2. Referencias del Dominio

- **Catálogo de Almas:** [`almas.md`](./almas.md) (especificación de los 5 corpus canónicos: `python`, `receta`, `legal`, `medicina`, `astronomia`).
- **Glosario Canónico:** [`../CONTEXT.md`](../CONTEXT.md).
- **Norma de Precisión Numérica:** [`../.agents/rules/cero-redondeos.md`](../.agents/rules/cero-redondeos.md).

---

## 3. Depuración Histórica

Los ciclos preliminares e hipótesis superadas (resonancia armónica cerrada, auditorías numéricas previas y tickets legacy) fueron completamente eliminados en la versión 0.3.0 para mantener el árbol de trabajo enfocado exclusivamente en la arquitectura vigente.


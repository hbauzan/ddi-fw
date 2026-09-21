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

---

## 2. Referencias del Dominio

- **Catálogo de Almas:** [`almas.md`](./almas.md) (especificación de los 5 corpus canónicos: `python`, `receta`, `legal`, `medicina`, `astronomia`).
- **Glosario Canónico:** [`../CONTEXT.md`](../CONTEXT.md).
- **Norma de Precisión Numérica:** [`../.agents/rules/cero-redondeos.md`](../.agents/rules/cero-redondeos.md).

---

## 3. Archivo Histórico

Los ciclos de investigación cerrados, auditorías pasadas y tickets previos se preservan en el directorio unificado [`../archive/`](../archive/):

* **Ciclo 2026-09-21 (Cierre de Resonancia T0–T4 y Auditoría Numérica N1–N4):**  
  [`../archive/roadmap-legacy/2026-09-21-cierre-resonancia-auditoria/`](../archive/roadmap-legacy/2026-09-21-cierre-resonancia-auditoria/)
* **Ola Q (GTE-Qwen2 1.5B):**  
  [`../archive/roadmap-legacy/ola-q/`](../archive/roadmap-legacy/ola-q/)
* **Baseline BGE-M3 v0.1:**  
  [`../archive/roadmap-legacy/v0.1-bge-m3/`](../archive/roadmap-legacy/v0.1-bge-m3/)
* **Investigaciones Históricas Previas:**  
  [`../archive/current-research/`](../archive/current-research/)

# Archivo Unificado de Material Descartado y Superado (`archive/`)

> [!WARNING]
> **AVISO CRÍTICO PARA AGENTES DE INTELIGENCIA ARTIFICIAL Y DESARROLLADORES:**
> Todo el contenido de esta carpeta (`archive/`) corresponde a **investigaciones pasadas, hipótesis cerradas/rechazadas, reportes históricos y tickets completados**.
> **ESTE MATERIAL ESTÁ DESCARTADO Y PREPARADO PARA SU FUTURA ELIMINACIÓN.**
> Ningún archivo dentro de este directorio debe considerarse ground-truth, arquitectura vigente ni hipótesis activa.

---

## 1. Propósito de este Directorio

Aislar en una única ubicación todo el historial documental para **no marear ni confundir a los modelos de lenguaje** con premisas obsoletas (como la hipótesis de resonancia armónica previa o la hipótesis deletor).

---

## 2. Contenido del Archivo

* **[`current-research/`](./current-research/)**:
  - Investigaciones cerradas, cierre de la resonancia armónica (T0–T4), auditorías numéricas previas (N1–N4), reportes diarios históricos y comparativas de motores anteriores.
* **[`roadmap-legacy/`](./roadmap-legacy/)**:
  - `2026-09-21-cierre-resonancia-auditoria/`: Protocolos cerrados y tickets SC01–SC06 del ciclo anterior.
  - `ola-q/`: Campaña de evaluación con Qwen2 (Q01–Q05).
  - `v0.1-bge-m3/`: Tickets fundacionales de la versión inicial (D01–D07).
* **[`rompepepe-reports/`](./rompepepe-reports/)**:
  - Reportes de auditoría de penetración del script `rompepepe` fechados en julio de 2026.

---

## 3. ¿Dónde vive la Arquitectura Activa?

Para cualquier tarea de implementación, diseño o consulta, referirse **únicamente** a las fuentes vivas:

1. **Visión General y Contratos:** [`../README.md`](../README.md) y [`../architecture_spec.md`](../architecture_spec.md).
2. **Glosario Canónico de Dominio:** [`../CONTEXT.md`](../CONTEXT.md).
3. **Pack de Trabajo Activo:** [`../roadmap/hipotesis-ecualizador/`](../roadmap/hipotesis-ecualizador/) (Protocolos 00 a 04 del Ecualizador Espectral).
4. **Norma Suprema de Precisión Numérica:** [`../.agents/rules/cero-redondeos.md`](../.agents/rules/cero-redondeos.md).
5. **Lecciones e Invariantes Técnicas:** [`../.agents/skills/dev-protocol/lessons-learned.md`](../.agents/skills/dev-protocol/lessons-learned.md).

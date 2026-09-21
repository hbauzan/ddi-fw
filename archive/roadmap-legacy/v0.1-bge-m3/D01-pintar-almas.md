# D01 — Pintar almas (textos + recorte)

> **Estado:** hecho
> **Ola:** 1
> **Especificación:** [`../00-alcance.md`](../00-alcance.md), [`../almas.md`](../almas.md)

---

## Objetivo

Generar y almacenar en disco tres mazos de texto curados (`python`, `legal`, `receta`), recortados y vetados de acuerdo con la especificación, listos para ser embebidos en el ticket `D02`.
- Cero llamadas al modelo de embedding en este ticket.
- Separación pura entre extracción/curaduría textual y cómputo vectorial.

---

## Dependencias

- **Depende de:** Ninguno.
- **Desbloquea:** `D02` (cálculo de hoja y corte duro).
- **Paralelo con:** Ninguno (el ticket `D02` requiere estos mazos textuales).

---

## Archivos de Referencia

- [`../almas.md`](../almas.md): Fuentes canónicas, criterios de recorte y reglas de veto.
- [`../00-alcance.md`](../00-alcance.md): Especificación general del pack.

---

## Archivos a Crear / Modificar

- `ddi_fw/almas.py`: Lógica de carga, extracción y validación de mazos.
- `ddi_fw/classify.py`: Clasificador textual auditable por reglas (descarte de lomo editorial).
- `ddi_fw/data/`: Directorio de fixtures de texto canónicos (`python.json`, `legal.json`, `receta.json`).
- `tests/test_ddi_almas.py`: Suite de tests unitarios.

---

## Fuera de Alcance

- Llamar a SentenceTransformer / BGE-M3 (eso corresponde a `D02`).
- Algoritmos de corte geométrico o cálculo de hojas.
- Descarga masiva o scraping web dinámico.

---

## Tareas

- [ ] Cargar cláusulas para `python` desde documentación oficial PSF (tutorial básico: tipos, listas, funciones, excepciones). Recortar índices, tablas de contenido y pies de página.
- [ ] Cargar cláusulas para `legal` a partir de textos SPDX canónicos (MIT, Apache-2.0, BSD-3-Clause). Cada cláusula debe ser una unidad lógica de la licencia.
- [ ] Cargar cláusulas para `receta` (instrucciones culinarias e ingredientes de recetas de dominio público).
- [ ] Implementar clasificador textual auditable que asigne etiqueta explícita (`python` | `legal` | `receta` | `lomo_descarte`).
- [ ] Implementar reglas de veto de `almas.md` con tests (ej. excluir módulos criptográficos en Python, contratos comerciales en legal).
- [ ] Implementar función/CLI `build_almas()` que guarde los tres mazos en archivos JSON estructurados en `ddi_fw/data/`.

---

## Pruebas (TDD)

1. **Rojo inicial**: No existen las funciones de carga ni los fixtures.
2. **Verde final**: Los tres mazos existen en disco, no están vacíos, no contienen ruido editorial y cumplen con los vetos especificados.

```bash
uv run pytest -q tests/test_ddi_almas.py
```

---

## Definición de Hecho (DoD)

- [ ] Tres mazos de texto serializados en disco, con conteo $n$ explícito y auditable.
- [ ] Cero dependencias o invocaciones al embedder BGE-M3.
- [ ] Tests pasando limpiamente en suite aislada.
- [ ] Fila `D01` actualizada a `hecho` en [`../README.md`](../README.md).

---

## Prompt Copiable para Ejecución

```text
Pack ddi-fw, ticket D01. Lee roadmap/00-alcance.md y roadmap/almas.md.
Trabaja exclusivamente en la curaduría, recorte y veto de los tres mazos de texto (python, legal, receta).
No invoques al embedder ni calcules vectores. TDD estricto con uv run pytest tests/test_ddi_almas.py.
Al finalizar y verificar, marca D01 como hecho en roadmap/README.md.
```

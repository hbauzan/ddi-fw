# D07 — Benchmark multi-embedder (MRL y comparación de ejes disjuntos)

> **Estado:** hecho
> **Ola:** 5 (Post-core / Optimización de Instrumento)
> **Especificación:** [`../00-alcance.md`](../00-alcance.md), [`../almas.md`](../almas.md)

---

## Objetivo

Una vez que el flujo completo (`D01` a `D06`) esté verificado y operativo con el baseline de `BAAI/bge-m3`, desacoplar formalmente el motor de embedding mediante una interfaz `BaseEmbedder` y habilitar la evaluación empírica comparativa entre múltiples modelos (`EmbeddingGemma` con MRL, `Qwen2-Embedding`, `Nomic-Embed-Text`).
- Descubrir empíricamente qué arquitectura produce la mayor cantidad de ejes disjuntos y la brecha dimensional (`gap`) más limpia entre almas.
- Medir el impacto de la reducción dimensional vía Matryoshka (ej. Gemma en 128D y 256D vs. BGE-M3 en 1024D) en términos de latencia y robustez geométrica.

---

## Dependencias

- **Depende de:** `D06` (el sistema completo —Ingress, Corte, Hold y Proxy— debe estar cerrado y con tests verdes antes de abrir el frente multi-modelo).
- **Desbloquea:** Selección empíricamente fundada del embedder final para entornos de alta concurrencia o recursos restringidos.
- **Paralelo con:** Ninguno (tarea posterior al lanzamiento del pack base).

---

## Archivos de Referencia

- [`../almas.md`](../almas.md): Pares headline a evaluar (`python ↔ receta`, `python ↔ legal`).
- [`../00-alcance.md`](../00-alcance.md): Contrato del candado dimensional.

---

## Archivos a Crear / Modificar

- `ddi_fw/embedder.py`: Refactor a patrón abstracto `BaseEmbedder` con providers registrados:
  - `BGEM3Embedder` (`BAAI/bge-m3` — 1024D)
  - `GemmaMRLEmbedder` (`google/embedding-gemma` — cortes MRL a 128D, 256D, 512D, 768D)
  - `NomicEmbedder` (`nomic-ai/nomic-embed-text-v1.5` — MRL 64D a 512D)
  - `Qwen2Embedder` (`Alibaba-NLP/gte-Qwen2-1.5B-instruct` o similar)
- `ddi_fw/press.py`: Extender CLI con `--model <model_id>` y comando `--benchmark-all`.
- `ddi_fw/out/benchmark_models.json`: Reporte comparativo tabular consolidado (ignorado en git).
- `tests/test_ddi_multi_embedder.py`: Tests unitarios de los providers con stubs/mocks de embeddings de distintas dimensiones.

---

## Fuera de Alcance

- Reentrenar o hacer fine-tuning de modelos de embedding.
- Alterar la lógica de corte duro o la semántica del Egreso Hold (la matemática es invariante al modelo).
- Romper la compatibilidad del baseline de BGE-M3 ya homologado en `D01`–`D06`.

---

## Tareas

- [ ] Definir protocolo `BaseEmbedder(Protocol)` con métodos estándar `embed_text(str) -> np.ndarray` y `embed_batch(list[str]) -> np.ndarray`, exponiendo propiedad `dimension: int`.
- [ ] Implementar soporte para **EmbeddingGemma con MRL**:
  - Parámetro de corte dimensional configurable (`dim=128`, `dim=256`, `dim=512`).
  - Normalización $L_2$ estricta tras el slicing del tensor.
- [ ] Implementar soporte para **Nomic-Embed-Text v1.5** con soporte MRL.
- [ ] Implementar comando comparativo en el CLI `press.py`:
  ```bash
  uv run python -m ddi_fw.press --benchmark-all --out ddi_fw/out/benchmark_models.json
  ```
- [ ] Generar matriz de certificación comparativa que mida para cada par canónico:
  1. Conteo de ejes disjuntos (`disjoint_axes_count`).
  2. Amplitud media y máxima de la brecha (`mean_gap`, `max_gap`).
  3. Latencia media por llamada (microsegundos en CPU).
  4. Huella de memoria RAM/VRAM.
- [ ] Documentar en `roadmap/README.md` los hallazgos empíricos y la recomendación del modelo óptimo según el caso de uso.

---

## Pruebas (TDD)

1. Verificar que `BaseEmbedder` sea polimórfico y admita vectores de distintas dimensiones (128, 256, 512, 768, 1024) sin alterar las funciones de `hoja.py` ni `corte.py`.
2. Probar que el CLI `--benchmark-all` genere un informe JSON estructurado con métricas de al menos dos modelos distintos utilizando matrices mock en tests.

```bash
uv run pytest -q tests/test_ddi_multi_embedder.py
```

---

## Definición de Hecho (DoD)

- [ ] Protocolo `BaseEmbedder` implementado y retrocompatible con el código de `D02` a `D06`.
- [ ] Soporte para BGE-M3 y al menos un modelo MRL (EmbeddingGemma o Nomic) funcionando de punta a punta.
- [ ] Reporte comparativo multi-modelo ejecutado y almacenado en `ddi_fw/out/`.
- [ ] Todos los tests unitarios e integrados pasando sin regresiones.
- [ ] Fila `D07` actualizada a `hecho` en [`../README.md`](../README.md).

---

## Prompt Copiable para Ejecución

```text
Pack ddi-fw, ticket D07 (Ola 5). Lee roadmap/tickets/D07-benchmark-multi-embedder.md.
Desacopla el embedder en ddi_fw/embedder.py con BaseEmbedder y suma soporte para EmbeddingGemma (MRL 128D/256D) y Nomic.
Extiende ddi_fw/press.py con --benchmark-all para comparar conteo de ejes disjuntos y latencia entre modelos.
Sin regresiones en los tests previos. TDD con: uv run pytest tests/test_ddi_multi_embedder.py.
Al cerrar, marca D07 como hecho en roadmap/README.md.
```

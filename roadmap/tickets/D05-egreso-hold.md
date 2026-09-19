# D05 — Egreso hold

> **Estado:** hecho  
> **Ola:** 3  
> **Especificación:** [`../00-alcance.md`](../00-alcance.md)

---

## Objetivo

Implementar el mecanismo de contención de salida **Egreso Hold**: retener en memoria la generación completa del modelo, segmentarla en proposiciones, y evaluar **cada una de las cláusulas entregables** mediante la misma función `decide()` utilizada en el Ingress (`D04`).
- Cero streaming especulativo: ningún token es enviado al cliente antes de que la totalidad de la respuesta sea aprobada.
- Si una sola cláusula incurre en `BREACH`, la respuesta entera es descartada (*fail-closed*).

---

## Dependencias

- **Depende de:** `D04` (función de decisión `decide()` y `ClauseSplitter`).
- **Desbloquea:** `D06` (proxy HTTP que expone la API hacia los clientes).
- **Paralelo con:** `D04` (si la firma de `decide()` está acordada mediante una interfaz stub).

---

## Archivos de Referencia

- [`../00-alcance.md`](../00-alcance.md): Especificación del mecanismo "Hold solamente".

---

## Archivos a Crear / Modificar

- `ddi_fw/egreso.py`: Lógica de retención, partición y validación de respuestas completas.
- `tests/test_ddi_egreso.py`: Suite de tests unitarios verificando que nunca se entreguen fragmentos cuando hay una infracción.

---

## Fuera de Alcance

- Buffers de streaming en tiempo real (prohibidos expresamente por la directiva de seguridad).
- Endpoints o servidores HTTP (eso corresponde a `D06`).
- Filtros léxicos de DLP basados en expresiones regulares o listas negras.

---

## Tareas

- [ ] Implementar función `hold(texto_generado, decide_fn=...) -> HoldResult`:
  - Retorna estado `DELIVERED` junto con el texto intacto, o `BLOCKED`.
  - Prohibido emitir o yieldear tokens antes de completar la evaluación total.
- [ ] Integrar segmentador de cláusulas sobre el texto completo acumulado.
- [ ] Aplicar la misma política y rigor geométrico que en Ingress (mismos intervalos y corte duro, sin umbrales relajados por ser texto de salida).
- [ ] Test unitario: Respuesta que combina contenido técnico autorizado con una receta de cocina prohibida bajo política `python-only` $\rightarrow$ Veredicto `BLOCKED`, contenido entregado vacío.
- [ ] Test unitario: Respuesta que contiene exclusivamente cláusulas dentro del dominio autorizado $\rightarrow$ Veredicto `DELIVERED`, texto idéntico al original sin modificaciones ni recortes parciales.

---

## Pruebas (TDD)

```bash
uv run pytest -q tests/test_ddi_egreso.py
```

---

## Definición de Hecho (DoD)

- [ ] Lógica de retención testeada: confirmación de que cero tokens se emiten ante una violación.
- [ ] Misma regla geométrica aplicada a entrada y salida.
- [ ] Suite de tests pasando limpiamente.
- [ ] Fila `D05` actualizada a `hecho` en [`../README.md`](../README.md).

---

## Prompt Copiable para Ejecución

```text
Pack ddi-fw, ticket D05. Lee roadmap/00-alcance.md.
Implementa el módulo de retención total de salida en ddi_fw/egreso.py.
Mismo decide() que en D04. Cero streaming especulativo. Fail-closed total.
Verifica con: uv run pytest tests/test_ddi_egreso.py.
Al cerrar, marca D05 como hecho en roadmap/README.md.
```

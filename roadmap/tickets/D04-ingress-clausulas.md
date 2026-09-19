# D04 — Ingress por cláusulas

> **Estado:** hecho  
> **Ola:** 3  
> **Especificación:** [`../00-alcance.md`](../00-alcance.md)

---

## Objetivo

Dado un texto o prompt arbitrario entrante, dividirlo en cláusulas lógicas independientes, obtener el embedding de cada una mediante el singleton BGE-M3, y dictaminar `PASS` o `BREACH` utilizando los candados dimensionales publicados.
- Política de seguridad: *Fail-closed*.
- Una sola cláusula que viole el dominio autorizado o caiga en un alma vedada tumba el prompt completo.

---

## Dependencias

- **Depende de:** `D02` (candados dimensionales y funciones de corte) y `D03` (estructura del censo para la bitácora).
- **Desbloquea:** `D05` (módulo de Egreso Hold) y `D06` (servicio Proxy HTTP).
- **Paralelo con:** `D05` (puede desarrollarse en paralelo mockeando la función `decide()`).

---

## Archivos de Referencia

- [`../almas.md`](../almas.md): Caso canónico de ataque piggyback de tres cláusulas.
- [`../00-alcance.md`](../00-alcance.md): Contrato del Ingress.

---

## Archivos a Crear / Modificar

- `ddi_fw/splitter.py`: Segmentador de texto en cláusulas lógicas (basado en signos de puntuación y conectores, protegiendo decimales técnicos).
- `ddi_fw/ingress.py`: Orquestador de evaluación de entrada y aplicación de políticas de contención.
- `tests/test_ddi_ingress.py`: Suite de tests unitarios utilizando stubs de embeddings para evitar la carga pesada del modelo durante los tests.

---

## Fuera de Alcance

- Lógica de retención de respuestas generadas (Egreso Hold en `D05`).
- Servidor web o interfaz ASGI/HTTP (eso corresponde a `D06`).
- Clasificación de toxicidad o palabras clave prohibidas.

---

## Tareas

- [ ] Implementar `ClauseSplitter`: Reglas deterministas para segmentar entradas preservando valores numéricos con coma o punto decimal (ej. `0.8 mm`, `1.4`).
- [ ] Implementar `decide(vector_clausula, candados_publicados, politica) -> Decision`:
  - Retorna `PASS` o `BREACH`.
  - Genera bitácora detallada con alma asignada, recuento de votos en 1024D y estado de los ejes disjuntos.
- [ ] Configurar política del demo:
  - Modo positivo sobre almas autorizadas (ej. requerir pertenencia estricta a `python`).
  - Detección de veto si la cláusula cae en un alma prohibida del par (ej. `receta`).
- [ ] Implementar comportamiento *fail-closed*: Rechazo inmediato ante errores de parsing, indisponibilidad del embedder o ausencia de ejes disjuntos certificados en la política.
- [ ] Validar con el caso piggyback de tres cláusulas: comprobar que la porción de receta culinaria sea detectada y tumbe la consulta entera, aunque las otras dos cláusulas sean legítimas.

---

## Pruebas (TDD)

1. Probar segmentación de cláusulas con oraciones complejas y números con decimales.
2. Probar la función de decisión inyectando vectores sintéticos (stubs) para simular cláusulas válidas e inválidas sin costo de inferencia en los tests unitarios.

```bash
uv run pytest -q tests/test_ddi_ingress.py
```

---

## Definición de Hecho (DoD)

- [ ] Segmentación del caso piggyback canónico en tres cláusulas comprobadas.
- [ ] Registro de auditoría dimensional por cláusula generado sin campos de promedio.
- [ ] Política *fail-closed* probada ante fallos o violaciones parciales.
- [ ] Fila `D04` actualizada a `hecho` en [`../README.md`](../README.md).

---

## Prompt Copiable para Ejecución

```text
Pack ddi-fw, ticket D04. Lee roadmap/00-alcance.md y roadmap/almas.md.
Implementa el segmentador por cláusulas y el módulo de Ingress en ddi_fw/splitter.py e ingress.py.
Veredicto fail-closed. Stub del embedder en pytest. No uses similitud coseno ni promedios.
Verifica con: uv run pytest tests/test_ddi_ingress.py.
Al cerrar, marca D04 como hecho en roadmap/README.md.
```

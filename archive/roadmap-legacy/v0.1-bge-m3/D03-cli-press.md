# D03 — CLI press (censo por fila)

> **Estado:** hecho
> **Ola:** 2
> **Especificación:** [`../00-alcance.md`](../00-alcance.md)

---

## Objetivo

Desarrollar una interfaz de línea de comandos (CLI) que lea el archivo de matrices de calibración `ddi_fw/out/rows.npz` y genere un censo detallado fila por fila con los votos en las 1024 dimensiones y el veredicto de corte duro.
- Sin volver a ejecutar el embedder.
- Sin promedios ni métricas agregadas que oculten el comportamiento individual de cada fila.

---

## Dependencias

- **Depende de:** `D02` (generación de `rows.npz` y módulos de hoja/corte).
- **Desbloquea:** Diagnóstico completo para `D04` (certificación de pares que se publican).
- **Paralelo con:** Ninguno crítico.

---

## Archivos de Referencia

- [`../00-alcance.md`](../00-alcance.md): Especificación del censo y auditoría de publicación.
- [`../almas.md`](../almas.md): Pares canónicos a tabular.

---

## Archivos a Crear / Modificar

- `ddi_fw/press.py`: CLI ejecutable mediante `python -m ddi_fw.press`.
- `ddi_fw/out/press.json`: Informe de calibración y conteos de censo (ignorado en git).
- `ddi_fw/out/press_*.csv`: Reportes tabulares detallados por fila (ignorados en git).
- `ddi_fw/out/press_votes.npz`: Matriz de votos discretizados uint8 (n, 1024) (ignorado en git).
- `tests/test_ddi_press.py`: Tests unitarios del CLI utilizando matrices simuladas en directorios temporales.

---

## Fuera de Alcance

- Servidores o endpoints HTTP.
- Llamadas al modelo de lenguaje (LLM).
- Generación de nuevos embeddings.

---

## Tareas

- [ ] Implementar parser de argumentos CLI (`--rows`, `--out`) con manejo de errores explícito si falta el archivo de entrada.
- [ ] Procesar los tres pares canónicos: `python` $\leftrightarrow$ `receta`, `python` $\leftrightarrow$ `legal`, `legal` $\leftrightarrow$ `receta`.
- [ ] Para cada par y cada familia textual:
  - Contabilizar censo de veredictos (`left`, `right`, `split`, `out`).
  - Registrar los extremos de recuento de votos (`lo` y `hi`).
  - Exportar detalle tabular por fila.
- [ ] Exportar archivo CSV con la votación individual en los ejes disjuntos para cada fila del par canónico `python` vs `receta`.
- [ ] Exportar matriz compacta `press_votes.npz` con los códigos de voto por dimensión.
- [ ] Si un candado tiene 0 ejes disjuntos, registrar explícitamente en el JSON de salida `"published": false` sin inventar umbrales.

---

## Pruebas (TDD)

1. Probar el CLI en `tests/test_ddi_press.py` inyectando un `rows.npz` sintético en una ruta temporal (`tmp_path`) y verificando la creación de los artefactos JSON y CSV con los esquemas esperados.
2. Comprobar que el archivo JSON resultante carezca de propiedades promediadas (`mean_*`).

```bash
uv run pytest -q tests/test_ddi_press.py
```

---

## Definición de Hecho (DoD)

- [ ] Tests con datos temporales pasando limpiamente.
- [ ] Ejecución live del comando `uv run python -m ddi_fw.press` generando los artefactos en `ddi_fw/out/`.
- [ ] Esquema JSON verificado sin campos de promedio.
- [ ] Fila `D03` actualizada a `hecho` en [`../README.md`](../README.md).

---

## Prompt Copiable para Ejecución

```text
Pack ddi-fw, ticket D03. Lee roadmap/00-alcance.md.
Crea el CLI press en ddi_fw/press.py para censar fila por fila las matrices de calibración.
Sin re-embeber y sin campos de promedio en los reportes. TDD en tests/test_ddi_press.py.
Verifica con: uv run pytest tests/test_ddi_press.py.
Al cerrar, marca D03 como hecho en roadmap/README.md.
```

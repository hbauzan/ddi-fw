# D02 — Hoja + corte duro

> **Estado:** hecho  
> **Ola:** 1  
> **Especificación:** [`../00-alcance.md`](../00-alcance.md), [`../almas.md`](../almas.md)

---

## Objetivo

Implementar en `ddi_fw/` el cálculo de la hoja de intervalos dimensionales `[lo, hi]` en las 1024 dimensiones para todas las filas de un par de almas, y la lógica de decisión de **corte duro** (`left` / `right` / `split` / `out`) operando exclusivamente sobre los ejes disjuntos.
- Sin medias.
- Sin centroides.
- Sin selecciones heurísticas *top-k*.
- Voto simultáneo de las 1024 dimensiones.

---

## Dependencias

- **Depende de:** `D01` (textos curados para la calibración en vivo final). La lógica matemática puede ser testeada previamente con matrices sintéticas/falsas.
- **Desbloquea:** `D03` (CLI de censo) y `D04` (módulo de Ingress).
- **Paralelo con:** Ninguno una vez provistos los textos de `D01`.

---

## Archivos de Referencia

- [`../00-alcance.md`](../00-alcance.md): Contrato del cálculo de hoja y corte duro.
- [`../almas.md`](../almas.md): Definición de pares canónicos y regla de publicación.

---

## Archivos a Crear / Modificar

- `ddi_fw/hoja.py`: Estructura y cálculo de la hoja dimensional `[lo, hi]`, cálculo de solapamientos (`overlap`), brechas (`gap`) y detección de ejes disjuntos.
- `ddi_fw/corte.py`: Evaluación de vectores y asignación de etiquetas de pertenencia (`left`, `right`, `split`, `out`).
- `ddi_fw/embedder.py`: Singleton wrapper de `SentenceTransformer('BAAI/bge-m3')`.
- `ddi_fw/out/rows.npz`: Archivo de matrices de embeddings persistido (ignorado en git).
- `tests/test_ddi_hoja.py`: Tests unitarios para el cálculo de hoja y ejes disjuntos.
- `tests/test_ddi_corte.py`: Tests unitarios para las reglas de votación y corte duro.

---

## Fuera de Alcance

- Interfaz de línea de comandos de censo masivo (eso corresponde a `D03`).
- Manejo de endpoints HTTP o proxies de red.
- Promedios de vectores o normalizaciones de centroides.

---

## Tareas

- [ ] Implementar `calcular_hoja(matriz_a, matriz_b) -> HojaDimensional`: Calcula para cada una de las 1024 dimensiones los intervalos mínimos y máximos de cada alma, la brecha de separación y el flag booleano de disyunción (`gap > 0`).
- [ ] Implementar `obtener_ejes_disjuntos(hoja) -> list[int]`: Retorna la lista exhaustiva de índices dimensionales donde los intervalos no tienen intersección.
- [ ] Implementar función de votación dimensional: Clasifica cada coordenada de un vector entrante frente a los intervalos de ambas almas (`solo_a`, `solo_b`, `ambas`, `ninguna`).
- [ ] Implementar `evaluar_corte_duro(votos, ejes_disjuntos) -> Label`: Retorna `left`, `right`, `split` o `out`. Si no existen ejes disjuntos, el veredicto debe ser estrictamente `out`.
- [ ] Implementar regla de auditoría de calibración: Si un par de dominios produce 0 ejes disjuntos, abortar la publicación del candado para ese par.
- [ ] Embeber los mazos de `D01` mediante el singleton BGE-M3 y almacenar las matrices resultantes en `ddi_fw/out/rows.npz`.

---

## Pruebas (TDD)

1. **Rojo inicial con matrices sintéticas**: Verificar con matrices pequeñas controladas (ej. dimensión 3 o 4) que la identificación de disyunción y el etiquetado de corte duro operen exactamente según las definiciones teóricas.
2. **Verde final**: Cobertura completa de las 1024 dimensiones; confirmación de que si `disjuntas == []` $\rightarrow$ resultado `out`; prueba de corrida real con el embedder sobre los mazos de `D01`.

```bash
uv run pytest -q tests/test_ddi_hoja.py tests/test_ddi_corte.py
```

---

## Definición de Hecho (DoD)

- [ ] Módulos `hoja.py` y `corte.py` implementados sin campos ni operaciones de media (`mean`).
- [ ] Tests con datos sintéticos pasando en verde.
- [ ] Archivo `ddi_fw/out/rows.npz` generado en vivo con los tres mazos de `D01`.
- [ ] Pares canónicos evaluados y auditados contra la regla de 0 ejes disjuntos.
- [ ] Fila `D02` actualizada a `hecho` en [`../README.md`](../README.md).

---

## Prompt Copiable para Ejecución

```text
Pack ddi-fw, ticket D02. Lee roadmap/00-alcance.md.
Implementa el cálculo de hoja dimensional 1024D y el corte duro en ddi_fw/hoja.py y ddi_fw/corte.py.
Prohibido usar medias, centroides o top-k. TDD con matrices sintéticas primero, luego corrida live con BGE-M3.
Verifica con: uv run pytest tests/test_ddi_hoja.py tests/test_ddi_corte.py.
Al cerrar, marca D02 como hecho en roadmap/README.md.
```

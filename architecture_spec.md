# architecture_spec — ddi-fw

Contratos vivos. Si cambia un shape, se actualiza este archivo en el mismo cambio.

## Embedder

Seam único `BaseEmbedder`:

- `model_id: str`
- `dimension: int`
- `embed_text(text: str) -> np.ndarray` shape `(dimension,)`, dtype float32
- `embed_batch(texts: list[str]) -> np.ndarray` shape `(n, dimension)`

Adapters: `BGEM3Embedder` (baseline 1024D), `GemmaMRLEmbedder`, `NomicEmbedder`, `Qwen2Embedder`, `FakeEmbedder` (tests).

Los tests default nunca cargan un modelo vivo.

## Hoja y corte

`calcular_hoja(matriz_a, matriz_b, alma_a, alma_b) -> HojaDimensional`

- `lo_a`, `hi_a`, `lo_b`, `hi_b`, `gap`, `disjoint` con `shape == (dimension,)`
- `gap > 0` ⇔ eje disjunto
- dimensión = `matriz_a.shape[1]` (no hardcode 1024)

`evaluar_corte_duro(votos, ejes_disjuntos) -> left|right|split|out`

- disjuntos vacíos → `out`
- cualquier `ninguna` o `ambas` en un disjunto → `out`
- todos `solo_a` → `left`; todos `solo_b` → `right`; mezcla → `split`

Convención de par: `{left}_{right}` ⇒ `python_receta` left=`python`, right=`receta`.

Publicación: `published = len(ejes_disjuntos) > 0`. Jamás se relaja `gap`.

## `rows.npz`

Claves requeridas: `python`, `legal`, `receta` (float32), `ids_*` (object), `texts_*` (object), `model_id`, `dimension`.

## `decide(vector, candados, politica) -> Decision`

- `verdict`: `PASS` | `BREACH`
- bitácora: alma asignada, recuentos de voto en todas las dims, `disjoint_count`, `published`
- prohibido: campos `mean_*`, similitud coseno
- fail-closed: candado inédito, embedder caído, cláusula vacía, `split`/`out`, alma vedada

Política demo: `allowed=python`, `forbidden={receta,legal}`. PASS solo si **todos** los pares publicados que involucran `python` etiquetan el lado python.

## Ingress / Egreso

`inspect_prompt(texto) -> IngressResult` (PASS/BREACH, decisiones por cláusula).

`hold(texto_generado, decide_fn) -> HoldResult`:

- `DELIVERED` + texto idéntico
- `BLOCKED` + texto vacío
- no genera tokens; no hace yield

## HTTP

`GET /healthz` → `{ "status": "ok"|"degraded", "embedder", "locks": { pair: {published, disjoint_count} } }`

`POST /v1/chat/completions`

- `stream=true` → 400
- sin mensaje `role=user` → 400
- ingress BREACH → **403** `{ "error": { "type": "ddi_ingress_breach", "message", "audit" } }` sin echo del prompt
- upstream timeout/error → **502** `{ "error": { "type": "ddi_upstream_error" } }`
- egreso BREACH → **403** `{ "error": { "type": "ddi_egreso_breach", "audit" } }`
- PASS → cuerpo OpenAI-compatible no streaming (`object=chat.completion`)

## Press JSON

`press.json`: por par, `disjoint_axes`, `disjoint_count`, `published`, censo por familia, `vote_count_extrema` `{lo,hi}` por tipo de voto. Cero `mean_*`.

`benchmark_models.json` (D07, diagnóstico): puede incluir `mean_gap` / `max_gap`. Esos campos no deciden publicación.

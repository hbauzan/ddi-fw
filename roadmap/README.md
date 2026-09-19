# Deep Dimensional Inspector Firewall (ddi-fw) — Pack Vivo

Herramienta independiente de inspección y contención dimensional estricta.

**ddi-fw** pinta almas chicas, compara todas las **$D$** dimensiones siempre (sea 128D, 256D, 768D o 1024D según el motor `BaseEmbedder`), y corta en duro donde los intervalos no se tocan (ejes disjuntos). No depende de medias, ni de similitudes coseno a centroides, ni de umbrales arbitrarios de dispersión.

- Alcance fundacional: [`00-alcance.md`](./00-alcance.md)
- Briefing Qwen2 (gana conflictos): [`00-qwen2-live.md`](./00-qwen2-live.md)
- Almas del demo: [`almas.md`](./almas.md)
- Ledger empírico: [`../current-research/embedder-ledger.md`](../current-research/embedder-ledger.md)
- Protocolo operativo: [`.agents/skills/dev-protocol/SKILL.md`](../.agents/skills/dev-protocol/SKILL.md)
- Hipótesis Deletor (**estacionada**, no implementar): rama `feat/hipotesis-deletor`

---

## Estado del Pack

### Etapa actual — ola Q (Qwen2 live)

Repetir el protocolo geométrico de BGE-M3 sobre `Alibaba-NLP/gte-Qwen2-1.5B-instruct`. Un ticket a la vez. TDD: `uv run pytest`. Números nuevos **solo** en `current-research/`.

| ID | Título | Estado |
| :--- | :--- | :--- |
| [Q01](./tickets/Q01-artifact-isolation-no-prune.md) | Aislar `out/qwen2/` + measure sin poda | hecho |
| [Q02](./tickets/Q02-qwen2-load.md) | Smoke load / encode 1536-D | hecho (blocker_load) |
| [Q03](./tickets/Q03-geometry-press.md) | Geometría full-deck + press | pendiente |
| [Q04](./tickets/Q04-ingress-hold-live.md) | Ingress / hold live (si publica) | pendiente |
| [Q05](./tickets/Q05-ledger-synthesis.md) | Ledger vs BGE sellado | pendiente |

**Regla**: leé [`00-qwen2-live.md`](./00-qwen2-live.md) antes del ticket. `calibrate()` poda: prohibido para Qwen2. Cero disjuntos = hallazgo, no se tocan los mazos.

La hipótesis espectral Deletor vive **solo** en `feat/hipotesis-deletor`. No mergear esa rama a ciegas.

### Histórico v0.1 (Baseline BGE-M3 — Archivado)
> Fila base consolidada y sellada bajo el tag `v0.1.0-bge-m3-baseline` en `main`.

| ID | Título | Ola | Estado | Archivo Histórico |
| :--- | :--- | ---: | :--- | :--- |
| D01 | Pintar almas (textos + recorte) | 1 | hecho | [`D01`](./archive/v0.1-bge-m3/D01-pintar-almas.md) |
| D02 | Hoja + corte duro | 1 | hecho | [`D02`](./archive/v0.1-bge-m3/D02-hoja-y-corte-duro.md) |
| D03 | CLI press (censo por fila) | 2 | hecho | [`D03`](./archive/v0.1-bge-m3/D03-cli-press.md) |
| D04 | Ingress por cláusulas | 3 | hecho | [`D04`](./archive/v0.1-bge-m3/D04-ingress-clausulas.md) |
| D05 | Egreso hold | 3 | hecho | [`D05`](./archive/v0.1-bge-m3/D05-egreso-hold.md) |
| D06 | Proxy OpenAI-compatible | 4 | hecho | [`D06`](./archive/v0.1-bge-m3/D06-proxy-hija.md) |
| D07 | Benchmark multi-embedder (MRL y comparación) | 5 | hecho | [`D07`](./archive/v0.1-bge-m3/D07-benchmark-multi-embedder.md) |

## Hallazgos empíricos (D07, 2026-09-19)

| Modelo | Dim | Live | Disjuntos python↔receta | python↔legal | legal↔receta |
| :--- | ---: | :--- | ---: | ---: | ---: |
| `BAAI/bge-m3` | 1024 | sí | 1 (eje 891) | 1 (eje 192) | 7 |
| `nomic-ai/nomic-embed-text-v1.5` | 256 MRL | no | — | — | custom code incompatible con transformers 5.x |
| `google/embeddinggemma-300m` | 256 MRL | no | — | — | gated 401 |
| `Alibaba-NLP/gte-Qwen2-1.5B-instruct` | 1536 | no | — | — | skip RAM; adapter + stubs |

Recomendación histórica v0.1: **seguir con BGE-M3**. El candado publica. Un solo eje disjunto en los pares headline es frágil: no engordar los mazos. `mean_gap` vive solo en `benchmark_models.json`.

> Esta tabla es el sello D07. **No la edites** para “actualizar” Qwen2. La ola Q escribe en [`current-research/embedder-ledger.md`](../current-research/embedder-ledger.md). En ola Q, cero disjuntos = `ok_unpublished`; **no** se podan mazos compartidos.

---

## Qué no es

- No es un clasificador difuso ni un scoring de similitud coseno.
- No utiliza mocks con expresiones regulares para simular deltas semánticos.
- No es un harm-classifier genérico ni un filtro léxico de palabras prohibidas.
- No implementa streaming especulativo en egreso (cero fugas de tokens antes del veredicto).
- No relaja intervalos agregando holguras heurísticas si hay 0 ejes disjuntos; en ese caso se poda el mazo.

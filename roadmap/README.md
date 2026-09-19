# Deep Dimensional Inspector Firewall (ddi-fw) — Pack Vivo

Herramienta independiente de inspección y contención dimensional estricta.

**ddi-fw** pinta almas chicas, compara todas las **$D$** dimensiones siempre (sea 128D, 256D, 768D o 1024D según el motor `BaseEmbedder`), y corta en duro donde los intervalos no se tocan (ejes disjuntos). No depende de medias, ni de similitudes coseno a centroides, ni de umbrales arbitrarios de dispersión.

- Alcance: [`00-alcance.md`](./00-alcance.md)
- Almas del demo: [`almas.md`](./almas.md)
- Insumo y Debate Activo: [Hipótesis "Deletor" (Ecualizador Espectral)](./hipotesis-deletor.md)
- Protocolo operativo: [`.agents/skills/dev-protocol/SKILL.md`](../.agents/skills/dev-protocol/SKILL.md)

---

## Estado del Pack

### Etapa Actual: Evaluación de Motores y Supresión Espectral (Deletor)
- Rama activa: `feat/spectral-deletor`
- Documento de diseño: [hipotesis-deletor.md](./hipotesis-deletor.md)

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

Recomendación: **seguir con BGE-M3**. El candado publica. Un solo eje disjunto en los pares headline es frágil: no engordar los mazos. `mean_gap` vive solo en `ddi_fw/out/benchmark_models.json`.

---

## Qué no es

- No es un clasificador difuso ni un scoring de similitud coseno.
- No utiliza mocks con expresiones regulares para simular deltas semánticos.
- No es un harm-classifier genérico ni un filtro léxico de palabras prohibidas.
- No implementa streaming especulativo en egreso (cero fugas de tokens antes del veredicto).
- No relaja intervalos agregando holguras heurísticas si hay 0 ejes disjuntos; en ese caso se poda el mazo.

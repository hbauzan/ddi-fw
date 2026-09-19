# Deep Dimensional Inspector Firewall (ddi-fw) — Pack Vivo

Herramienta independiente de inspección y contención dimensional estricta.

**ddi-fw** pinta almas chicas, compara las **1024** dimensiones siempre, y corta en duro donde los intervalos no se tocan (ejes disjuntos). No depende de medias, ni de similitudes coseno a centroides, ni de umbrales arbitrarios de dispersión.

- Alcance: [`00-alcance.md`](./00-alcance.md)
- Almas del demo: [`almas.md`](./almas.md)
- Protocolo operativo: [`.agents/skills/dev-protocol/SKILL.md`](../.agents/skills/dev-protocol/SKILL.md)

---

## Estado del Pack

Pack **tomable**. Tickets `D01`–`D07`. Prefijo **D**, orden estricto por olas.

| ID | Título | Ola | Estado |
| :--- | :--- | ---: | :--- |
| [D01](./tickets/D01-pintar-almas.md) | Pintar almas (textos + recorte) | 1 | hecho |
| [D02](./tickets/D02-hoja-y-corte-duro.md) | Hoja + corte duro | 1 | hecho |
| [D03](./tickets/D03-cli-press.md) | CLI press (censo por fila) | 2 | hecho |
| [D04](./tickets/D04-ingress-clausulas.md) | Ingress por cláusulas | 3 | hecho |
| [D05](./tickets/D05-egreso-hold.md) | Egreso hold | 3 | hecho |
| [D06](./tickets/D06-proxy-hija.md) | Proxy OpenAI-compatible | 4 | hecho |
| [D07](./tickets/D07-benchmark-multi-embedder.md) | Benchmark multi-embedder (MRL y comparación de ejes disjuntos) | 5 | hecho |

**Regla de trabajo**: Tomá **un** ticket a la vez. TDD estricto con `uv run pytest`. Al cerrar y verificar, marcá la fila de esta tabla como `hecho`. Los tickets D01 a D06 constituyen el core funcional con BGE-M3; D07 es la fase de optimización comparativa multi-modelo una vez que el sistema esté validado.

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

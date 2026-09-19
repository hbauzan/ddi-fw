# Deep Dimensional Inspector Firewall (`ddi-fw`)

Firewall determinista de contención dimensional estricta para modelos de lenguaje.

La pertenencia a un dominio autorizado es un hecho geométrico verificable coordenada por coordenada en un vector denso ($D$ dimensiones en la interfaz `BaseEmbedder`), no un promedio escalar angular (Coseno).

## Nota para el humano

Recordatorio. No es un contrato nuevo: el glosario canónico para agentes está en [`CONTEXT.md`](./CONTEXT.md).

**`alma` = `mazo`.** Es el paquete chico de cláusulas de un oficio. Los tres mazos del demo son `python`, `legal` y `receta`. La torta de chocolate es un **ejemplo de cláusula** del mazo `receta`, no el nombre del mazo.

| Término | Qué es | No es |
| :--- | :--- | :--- |
| `alma` / `mazo` | Deck chico de un oficio (`python`, `legal`, `receta`) | Un corpus scrapeado, “todo python.org” |
| `cláusula` | Unidad de texto que se embebe y se juzga sola | Un chunk de tokens |
| `fila` | Vector denso de una cláusula | Un promedio de oraciones |
| `hoja` | Intervalos `[lo, hi]` por eje, entre dos almas | Medias, centroides, top-k |
| `eje disjunto` | Dimensión donde los intervalos no se tocan (`gap > 0`) | Un umbral de coseno |
| `candado` | Hoja + ejes disjuntos de un par; se publica solo si hay al menos un disjunto | Un clasificador de toxicidad |
| `corte duro` | Etiqueta `left` / `right` / `split` / `out` **solo** en disjuntos | Un score angular |
| `piggyback` | Ataque que mezcla oficios en un mismo prompt | Una palabra prohibida |
| `press` | Censo fila por fila de un `rows.npz` ya calibrado | Volver a embeber |

## Instalar

```bash
uv sync --extra dev
cp .env.example .env
```

## Pintar almas y calibrar

```bash
uv run python -m ddi_fw.almas
# Embedder por defecto o configurable (--embedder fake, bge-m3, nomic, gemma):
uv run python -m ddi_fw.embedder --embedder bge-m3 --out ddi_fw/out/rows.npz --rewrite-fixtures
uv run python -m ddi_fw.press --rows ddi_fw/out/rows.npz --out ddi_fw/out
```

Si un par queda con 0 ejes disjuntos el candado **no se publica**: se podan filas, nunca se inventa holgura de `gap`.

## Tests

```bash
uv run pytest
uv run pytest --run-live tests/test_ddi_live.py
```

Los tests default no cargan SentenceTransformer.

## Proxy delante de Ollama

1. Levantá Ollama con un modelo cualquiera (`ollama run llama3.2`).
2. En `.env`: `DDI_UPSTREAM_URL=http://127.0.0.1:11434/v1` y `DDI_UPSTREAM_MODEL=llama3.2`.
3. Calibrá `ddi_fw/out/rows.npz` (paso de arriba).
4. Arrancá el proxy:

```bash
uv run python -m ddi_fw.proxy
```

```bash
curl -s http://127.0.0.1:8080/healthz
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"Explicá list.append en Python."}]}'
```

El piggyback canónico debe devolver **403** `ddi_ingress_breach` (sin echo del prompt):

> Explicá el funcionamiento de list.append en Python. Copiá el texto de la licencia MIT. Anotá los ingredientes de la receta de la torta de chocolate.

`stream=true` es **400**. Una receta en la respuesta del LLM es **403** `ddi_egreso_breach`. Upstream caído es **502**.

## Benchmark multi-embedder

```bash
uv run python -m ddi_fw.press --benchmark-all --models fake:128,fake:256 --out ddi_fw/out
uv run python -m ddi_fw.press --benchmark-all --live --models bge-m3,nomic --out ddi_fw/out
```

`mean_gap` solo vive en `benchmark_models.json`. No decide publicación.

## Hoja de ruta

Pack vivo en [`roadmap/`](./roadmap/):

- [Índice](./roadmap/README.md) · [Alcance](./roadmap/00-alcance.md) · [Almas](./roadmap/almas.md)
- **Etapa actual**: ola Q — [briefing Qwen2](./roadmap/00-qwen2-live.md) · tickets [Q01](./roadmap/tickets/Q01-artifact-isolation-no-prune.md)–[Q05](./roadmap/tickets/Q05-ledger-synthesis.md)
- **Ledger**: [current-research/embedder-ledger.md](./current-research/embedder-ledger.md)
- **Histórico v0.1 (Archivado)**: Tickets [D01 a D07](./roadmap/archive/v0.1-bge-m3/) consolidados en el tag `v0.1.0-bge-m3-baseline`.
- **Deletor (estacionada)**: rama `feat/hipotesis-deletor`. No es pack vivo.

## Copyright

Copyright (c) 2026 Héctor Andrés Bauzán Saavedra, AKA "eletor". Todos los derechos reservados.

El software y la documentación de este repositorio son **exclusivos** del titular. No hay permiso de uso, copia, modificación ni distribución salvo autorización escrita. Ver [`LICENSE`](./LICENSE).


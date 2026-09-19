# Deep Dimensional Inspector Firewall (`ddi-fw`)

Firewall determinista de contención dimensional estricta para modelos de lenguaje.

La pertenencia a un dominio autorizado es un hecho geométrico verificable coordenada por coordenada en un vector denso (1024D en BGE-M3), no un promedio escalar angular (Coseno).

## Instalar

```bash
uv sync --extra dev
cp .env.example .env
```

## Pintar almas y calibrar (BGE-M3)

```bash
uv run python -m ddi_fw.almas
uv run python -m ddi_fw.embedder --out ddi_fw/out/rows.npz --rewrite-fixtures
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
- [D01](./roadmap/tickets/D01-pintar-almas.md) · [D02](./roadmap/tickets/D02-hoja-y-corte-duro.md) · [D03](./roadmap/tickets/D03-cli-press.md)
- [D04](./roadmap/tickets/D04-ingress-clausulas.md) · [D05](./roadmap/tickets/D05-egreso-hold.md) · [D06](./roadmap/tickets/D06-proxy-hija.md)
- [D07](./roadmap/tickets/D07-benchmark-multi-embedder.md)

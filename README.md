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
| `eje disjunto` | Pared de un eje: los intervalos no se tocan (`gap > 0`) | La hipótesis de resonancia |
| `candado` | Hoja + ejes disjuntos; se publica solo si hay al menos un disjunto | Un clasificador de toxicidad |
| `corte duro` | Etiqueta `left` / `right` / `split` / `out` **solo** en disjuntos | Un score angular |
| `resonancia armónica` | Hipótesis abierta. Se cierra con cláusulas que no armaron las cajas | Un censo de las mismas cláusulas de la caja |
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

Si un par queda con 0 ejes disjuntos el candado de producto **no se publica**: se podan filas, nunca se inventa holgura de `gap`. Eso no cierra la hipótesis de resonancia.

## Precisión

Norma vigente: [`.agents/rules/cero-redondeos.md`](./.agents/rules/cero-redondeos.md).

Las coordenadas viven cerca de 0,025. Una separación entre temas, si existe, es del orden de `10^{-4}` a `10^{-6}`. El veredicto usa float32. Float16 no entra a ese camino. No se usa `round` ni `:.4f` / `:.6f`. El texto de una coordenada se escribe `f"{float(val):.17g}"` o `str(float(val))`. Si una pantalla acorta un número, el dato de abajo queda entero y el pie dice `display-only rounding; engine unrounded`.

Medición científica **sin poda** (ola Q / Qwen2). No llama `calibrate()`. No pisa `ddi_fw/out/rows.npz`:

```bash
uv run python -m ddi_fw.embedder --embedder qwen2 --no-prune --out ddi_fw/out/qwen2
```

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

- [Índice del Pack Vivo](./roadmap/README.md)
- **Informe Metodológico y Evidencia Empírica**: [`roadmap/hipotesis-ecualizador/05-informe-metodologico-y-evidencia.md`](./roadmap/hipotesis-ecualizador/05-informe-metodologico-y-evidencia.md) (Consolidación exhaustiva: métricas de datos, pipeline de 5 fases, scripts asociados y respaldo experimental).
- **Etapa actual**: **Hipótesis del Ecualizador Espectral** (Protocolos 00 a 05 en [`roadmap/hipotesis-ecualizador/`](./roadmap/hipotesis-ecualizador/)).
  - **Poda de Ruido Estructural Estructural**: 39 dimensiones de ruido basal aisladas (7 saturadas con energía basal $> 0.12$, 32 planas sin variabilidad temática), dejando 985 trigos candidatos depurados.
  - **Norma Universal de 6 Decimales (`10^{-6}`)**: Convención estándar nativa de `float32` (mantisa de 24 bits = ~7.2 dígitos significativos). Opera con un factor de seguridad de $1.000\times$ sobre el promedio temático ($\Delta_{avg} = 0.0139$, 2 a 3 decimales) y corta estrictamente por encima de la deriva del silicio ($2.46 \times 10^{-7}$). Inmunidad y compatibilidad total en C, Python, Rust y CUDA.
  - **Regla Universal del Quórum del 10% ($\lceil 0.10 \times D \rceil$)**: Premisa arquitectónica para BGE-M3 (100D de 1024D) y futuros motores (ej. 150D en Qwen2 1536D, 26D en Gemma 256D). Concentra más del 85% de la información discriminante y descarta el 90% del espectro ruidoso.
  - **Confirmación Matemática Anti-Bypass ($P < 10^{-9}$)**: En 100 dimensiones contrastadas, la probabilidad combinada de que un prompt ajeno o inyección hostil coincida por azar en el quórum es $P \le (0.8)^{100} \approx 2.03 \times 10^{-10}$ (menos de 1 en 5.000 millones). La fluctuación de 3 a 5 dimensiones por estilo léxico es absorbida holgadamente por el 95% restante del quórum. Latencia sub-milisegundo (< 10 $\mu$s en CPU).
  - **Auditoría de Hardware & Precisión**: Deriva física Apple M4 GPU (`mps:0`) vs CPU medida en $2.46 \times 10^{-7}$. En el Top 10% ($\Delta \ge 0.01$), la separación física es más de $50.000\times$ superior a la deriva de hardware. Operaciones acumuladas en memoria en `float64`.
- **Depuración Histórica**: Los borradores, auditorías cerradas e hipótesis superadas preliminares fueron purgados del repositorio para consolidar la arquitectura de la versión 0.3.0 en torno al Ecualizador Espectral.

## Copyright

Copyright (c) 2026 Héctor Andrés Bauzán Saavedra, AKA "eletor". Todos los derechos reservados.

El software y la documentación de este repositorio son **exclusivos** del titular. No hay permiso de uso, copia, modificación ni distribución salvo autorización escrita. Ver [`LICENSE`](./LICENSE).


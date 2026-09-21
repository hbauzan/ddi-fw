# Auditoría de precisión del pipeline de embeddings

2026-09-21. Consultar este archivo cuando se pregunte en qué dtype viven los pesos, el tensor de salida, si los vectores pasan por JSON antes del cálculo, en qué precisión corre el álgebra, o si el encode es determinista bit a bit.

Stack medido: `sentence-transformers` 6.1.0, `numpy` 2.5.3. Pin de producto: `BAAI/bge-m3`. Script: [`scripts/cold_embedding_determinism.py`](../scripts/cold_embedding_determinism.py).

## 1. Tipos de datos

### BGE-M3 (pin)

| Pieza | Precisión | Evidencia |
| :--- | :--- | :--- |
| Pesos en disco | float32 | Snapshot local `models--BAAI--bge-m3` `9a0624b…/model.safetensors`: 391/391 tensores `F32`. `config.json` del snapshot `5617a9f…`: `"torch_dtype": "float32"`. |
| Pesos en memoria | float32 | `BGEM3Embedder` no pasa `torch_dtype`. Corrida 2026-09-21: `torch.float32` en `mps:0`. |
| Tensor que devuelve `encode`, antes del cast del adapter | float32 | El modelo corre en float32. Sentence-Transformers 6.1.0 hace `emb.numpy()` sin cambiar el dtype. Solo llama `.float()` si el tensor es **bfloat16**. |
| Vector que entra a la hoja / `decide` | float32 | `ddi_fw/adapters/base.py` `embed_batch`: `np.asarray(..., dtype=np.float32)`. Contrato: `embed_text -> ndarray` shape `(dimension,)`, dtype float32. |

### Qwen2 (no es el pin)

| Pieza | Precisión | Evidencia |
| :--- | :--- | :--- |
| Pesos en memoria | float16 | `ddi_fw/adapters/qwen2.py` `_prepare_load`: `model_kwargs={"torch_dtype": torch.float16}`. |
| Numpy que devuelve `encode`, antes del cast | float16 | Misma regla de Sentence-Transformers: float16 no se promociona; bfloat16 sí. Inferido del código. El snapshot de Qwen2 no estaba en la caché local el 2026-09-21; no hay tensor en vivo de ese tramo en esta auditoría. |
| Vector público de `embed_text` | float32 | El adapter castea a `np.float32` en la línea siguiente. |

Gemma MRL y Nomic también salen por `embed_batch` en float32. Su norma L2 está en la sección 3.

## 2. Serialización

El camino de veredicto no convierte coordenadas a texto.

`embed_batch` devuelve un `ndarray` float32. `calcular_hoja`, `etiquetar_fila` y `decide` consumen ese array. `save_rows` persiste con `np.savez_compressed` (float32 binario). `load_rows` / `rows_matrices` releen con `np.load` y vuelven a `dtype=np.float32`.

JSON del pipeline (`measure_audit.json`, `calibrate_audit.json`, `press.json`) guarda conteos, ids de ejes, etiquetas y paths. El CSV de `press` guarda votos (`left` / `right` / `split` / `out`), no coordenadas.

Desvío de investigación, fuera de `decide()`: `scripts/run_dual_engine_inspection.py` y `scripts/export_top500_excitadas.py` arman un `Decimal` desde `f"{float(v):.17g}"` para el ranking Top 500. Ese texto es un round-trip del float32. La hoja ya se calculó sobre el array.

## 3. Álgebra

`hoja.py` y `corte.py` no calculan producto punto ni norma. Por eje hacen `min`, `max` y restas de cotas (`lo_b - hi_a`, solape en `calcular_brecha`). Con entradas float32 y NumPy 2.5.3 esas operaciones quedan en float32. El corte compara (`>=`, `<=`) el vector float32 contra esas cotas.

`l2_normalize` (`ddi_fw/adapters/base.py`) solo corre en los cortes MRL de Gemma y Nomic. Castea la entrada a float32. En NumPy 2.5.3, `np.linalg.norm` de un float32 es `x.dot(x)` (vector) o la suma de cuadrados (eje), y el resultado es float32. La división posterior también queda en float32 (promoción de escalares NEP 50). Medido en este entorno el 2026-09-21: `norm`, `dot`, resta y `min` de float32 devuelven float32.

## 4. Test de ruido (cinco cargas en frío)

Comando:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/cold_embedding_determinism.py
```

Cada corrida es un proceso nuevo. El vector viaja en `.npy` float32. Varianza poblacional de cada bit IEEE-754 de cada coordenada, con `k` corridas en las que ese bit vale 1 y `n` corridas:

```text
var = k * (n - k) / n**2
```

Determinismo bit a bit: el máximo de esas varianzas es 0 y los `tobytes()` coinciden.

Medición 2026-09-21. Texto: `Explicá el funcionamiento de list.append en Python.` Embedder: `bge-m3`. Device: `mps:0`.

| Campo | Valor |
| :--- | :--- |
| dtype / dim | float32 / 1024 |
| weight_dtype | torch.float32 |
| SHA-256 de las 5 corridas | `852bf52f9bc6bfd667304088da41395dd96f4277ec33a9eeaac004690d963912` |
| bitwise_identical | true |
| max_bit_variance | 0 (`numer=0`, `denom=25`) |

Alcance: una cláusula, BGE-M3, este MPS. Qwen2 no se corrió en esta auditoría (`--embedder qwen2` cuando el snapshot esté en caché).

## Anclas de código

- `ddi_fw/adapters/base.py`: `embed_batch`, `l2_normalize`
- `ddi_fw/adapters/bge.py`: sin `torch_dtype`
- `ddi_fw/adapters/qwen2.py`: `torch.float16`
- `ddi_fw/embedder.py`: `save_rows` / `load_rows`
- `ddi_fw/hoja.py`: `calcular_brecha`
- `ddi_fw/corte.py`: comparaciones de intervalo
- `scripts/cold_embedding_determinism.py`: repetición en frío

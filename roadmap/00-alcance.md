# Alcance — Deep Dimensional Inspector Firewall (ddi-fw)

Fecha: 2026-09-19. Herramienta independiente. Pack fundacional.

---

## Qué hay que construir

Un candado geométrico determinista empaquetado en `ddi_fw/`. Utiliza una arquitectura conectada vía la interfaz abstracta `BaseEmbedder` (con `BAAI/bge-m3` como baseline histórico archivado, y soporte para modelos alternativos y MRL a 128D/256D). La decisión es puramente dimensional y no depende de distancias angulares escalares.

1. **Almas chicas**: Tres mazos canónicos: `python` (tutorial oficial PSF), `legal` (SPDX MIT / Apache-2.0 / BSD-3-Clause), `receta` (cláusulas de cocina). Fuentes y vetos en [`almas.md`](./almas.md).
2. **Hoja dimensional**: Por par de almas: cálculo de `[lo, hi]` para **todas** las filas en las $D$ dimensiones del modelo. Sin medias. Sin top-k.
3. **Corte duro**: Clasificación de filas en `left` / `right` / `split` / `out` evaluada estrictamente en los ejes disjuntos (donde los intervalos no se solapan). Las otras dimensiones votan en la hoja completa; no se descartan.
4. **Ingress**: Partición del prompt en cláusulas lógicas. Veredicto *fail-closed*. Si una sola cláusula no cabe en el alma permitida o cae en un alma vedada por la política, se rechaza la consulta completa.
5. **Egreso hold**: Retención total de la respuesta generada por el LLM. Aplica el mismo candado sobre cada cláusula del texto antes de emitir cualquier token al cliente. Cero streaming especulativo.
6. **Proxy OpenAI-compatible**: Servicio HTTP compatible con `/v1/chat/completions` situado delante de cualquier LLM (ej. Ollama o vLLM). El modelo genera, pero `ddi-fw` es el único juez de emisión.
7. **Benchmark Multi-Embedder (Ola 5)**: Interfaz abstracta `BaseEmbedder` para contrastar empíricamente BGE-M3 contra modelos con Matryoshka Representation Learning (MRL como `EmbeddingGemma` a 128D/256D o `Nomic`) y medir qué arquitectura ofrece mayor cantidad de ejes disjuntos y menor latencia.

- **Artefactos**: `ddi_fw/out/` (ignorado en git).
- **Tests**: `tests/test_ddi_*.py` ejecutados con `uv run pytest`.

---

## Axioma y Claim de este pack

El vector denso es un hash físico serializado:
> *Mismo texto + mismo embedder pinneado $\rightarrow$ misma fila exacta de 1024 floats.*

La pertenencia a un dominio es un hecho de **inclusión en intervalos y votos por eje**, no una proyección angular contra un centroide difuso.

Evidencia experimental:
- Dos dominios ontológicamente nítidos revelan ejes disjuntos (`gap > 0`).
- Si un par bajo prueba arroja **0 ejes disjuntos**, el mazo está contaminado o es demasiado amplio: **el candado no se publica**. Se depura y recorta el mazo; jamás se inventa un umbral artificial.
- Piggyback: la cadena completa promediada engaña al Coseno; las cláusulas aisladas no pueden engañar a los intervalos disjuntos.

---

## Qué no entra en este pack

- Métricas de distancia angular (similitud Coseno) como criterio de decisión.
- Mocks basados en expresiones regulares para simular vectores.
- Promedios de filas (`mean`), centroides normalizados o rankings heurísticos *top-k*.
- Whitening, proyecciones INLP o transformaciones que alteren la medición nativa del embedder.
- Clasificadores de "contenido tóxico" o taxonomías difusas.
- Ingesta masiva no curada ("todo python.org" o "un libro de cocina de 900 páginas"): eso produce "paredes gordas" y anula la disyunción.
- Streaming token a token sin retención previa en egreso.

---

## Comparativa de Arquitectura

| Dimensión | Enfoque Tradicional (Coseno / Heurístico) | Deep Dimensional Inspector (`ddi-fw`) |
| :--- | :--- | :--- |
| **Representación** | Centroide promedio escalar | Hoja de intervalos empíricos `[lo, hi]` en 1024D |
| **Criterio de corte** | Umbral angular ($\cos \ge 0.82$) | Corte duro en ejes disjuntos + voto en las 1024 |
| **Ingress** | Evaluación de texto como bloque único | Partición estricta por cláusulas (*fail-closed*) |
| **Egreso** | Buffer de streaming o auditoría post-hoc | Egreso Hold: retención total previa a la entrega |
| **Superficie** | Middleware acoplado | Proxy HTTP independiente OpenAI-compatible |

---

## Estructura de Código Destino

```text
ddi-fw/
├── pyproject.toml
├── README.md
├── roadmap/
│   ├── README.md
│   ├── 00-alcance.md
│   ├── almas.md
│   └── archive/
│       └── v0.1-bge-m3/
│           ├── D01-pintar-almas.md
│           ├── D02-hoja-y-corte-duro.md
│           ├── D03-cli-press.md
│           ├── D04-ingress-clausulas.md
│           ├── D05-egreso-hold.md
│           ├── D06-proxy-hija.md
│           └── D07-benchmark-multi-embedder.md
├── ddi_fw/                  ← Paquete principal
│   ├── __init__.py
│   ├── almas.py
│   ├── hoja.py
│   ├── corte.py
│   ├── press.py
│   ├── ingress.py
│   ├── egreso.py
│   ├── proxy.py
│   └── out/                 ← Artefactos y matrices .npz (gitignored)
└── tests/
    ├── test_ddi_almas.py
    ├── test_ddi_hoja.py
    ├── test_ddi_corte.py
    ├── test_ddi_press.py
    ├── test_ddi_ingress.py
    ├── test_ddi_egreso.py
    └── test_ddi_proxy.py
```

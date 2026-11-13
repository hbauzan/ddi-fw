# 01 — Especificación Paso a Paso del TEST A (`TASK-001`)
## Duelo Ciego: Cajas DDI v0.4.0 vs. Diferencia de Coseno vs. Subespacio Espectral Blanqueado (`EEB`) sobre Código Python Real

**Objetivo:** Determinar con evidencia empírica irrefutable ("dato mata relato") qué geometría clasifica mejor código Python real frente a tópicos ajenos, otros lenguajes de programación, dominios nunca vistos (OOD) y ataques de *piggybacking*, sin bloquear código Python legítimo con vocabulario de negocios.

> [!WARNING]
> **REGLAS ESTRICTAS PARA EL AGENTE EJECUTOR:**
> - **NO tocar** `ddi_fw/hoja.py`, `ddi_fw/corte.py`, `ddi_fw/ingress.py`, `ddi_fw/egreso.py` ni `ddi_fw/proxy.py`.
> - **NO leer** ningún archivo de `roadmap/future-notes/`.
> - Seguir exactamente los nombres de archivos, firmas y ecuaciones de los 4 Slices detallados abajo.

---

## Slice 1 — Segmentador Estructural AST + Ventanas (`ddi_fw/lab_v2/chunker.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/__init__.py`
2. `ddi_fw/lab_v2/chunker.py`
3. `tests/lab_v2/__init__.py`
4. `tests/lab_v2/test_a1_chunker.py`

### Problema que resuelve:
El splitter viejo (`ddi_fw/splitter.py`) parte por cada `\n+`, dejando líneas huérfanas como `else:`, `pass`, `return res` que ningún modelo de embeddings puede clasificar sin contexto.

### Especificación exacta de `ddi_fw/lab_v2/chunker.py`:
Implementar las siguientes funciones públicas:

```python
from dataclasses import dataclass
from typing import Literal

ChunkKind = Literal["python_ast", "fenced_code", "prose_window"]

@dataclass(frozen=True)
class TextChunk:
    text: str
    kind: ChunkKind
    is_valid_python_ast: bool
    start_line: int
    end_line: int

def extract_chunks(
    text: str,
    max_ast_lines: int = 30,
    window_lines: int = 12,
    stride_lines: int = 6,
) -> list[TextChunk]:
    ...
```

**Algoritmo paso a paso (no inventar variantes):**
1. Si `not text or not text.strip()`, devolver `[]`.
2. **Caso 1 — El texto contiene bloques Markdown con triple backtick (```` ``` ````):**
   - Extraer con regex `r"```([a-zA-Z0-9_+-]*)\n(.*?)```"` (`re.DOTALL`) cada bloque cercado y los tramos de texto fuera de las cercas.
   - Para cada bloque cercado: evaluar si su interior pasa `ast.parse(code)` (con al menos 1 statement ejecutable que no sea un único `ast.Expr(ast.Constant)`). Si es Python válido, aplicar la lógica del **Caso 2**; si no es Python válido (ej. Bash, SQL, JS), emitir ventanas deslizantes con `kind="fenced_code"`, `is_valid_python_ast=False`.
   - Para cada tramo de prosa fuera de cercas (y comentarios `# ...` o docstrings largos extraídos si superan 80 caracteres con signos de puntuación naturales): aplicar la lógica del **Caso 3** (`kind="prose_window"`). *Importante para seguridad:* siempre extraer también comentarios/docstrings de funciones Python de más de 60 caracteres como `TextChunk(kind="prose_window", is_valid_python_ast=False)` adicionales para que un ataque escondido en un docstring o comentario jamás se beneficie del flag `is_valid_python_ast=True`!
3. **Caso 2 — El texto completo pasa `ast.parse(text)`:**
   - Recorrer `tree.body`:
     - Agrupar nodos simples contiguos a nivel módulo (`Import`, `ImportFrom`, `Assign`, `AnnAssign`, `Expr`) en un único bloque para nunca emitir una línea suelta de 10 caracteres.
     - Cada `FunctionDef`, `AsyncFunctionDef` o `ClassDef` se extrae con `ast.get_source_segment(text, node)` (o por rangos `node.lineno` a `node.end_lineno`).
     - Si un nodo supera `max_ast_lines`, dividir sus líneas en ventanas solapadas de tamaño `window_lines` con paso `stride_lines` (`kind="python_ast"`, `is_valid_python_ast=True`).
   - Además, inspeccionar con `tokenize` o `ast.walk` comentarios `#` y docstrings `Constant(str)` de longitud `>= 40` caracteres y agregarlos como chunks `kind="prose_window", is_valid_python_ast=False` para auditar *piggybacking* dentro de strings/comentarios.
4. **Caso 3 — Texto que NO pasa `ast.parse` y no tiene cercas:**
   - Dividir en oraciones con `re.split(r"(?<=[.!?])\s+|\n{2,}", text.strip())`.
   - Agrupar de a **2 oraciones contiguas** con paso de 1 oración (ventana deslizante de 2 oraciones; si solo hay 1 oración, emitir esa única oración) con `kind="prose_window"`, `is_valid_python_ast=False`. Jamás emitir fragmentos de menos de 4 caracteres si pueden fusionarse con el vecino.

### Tests obligatorios en `tests/lab_v2/test_a1_chunker.py`:
- Una función Python de 12 líneas con `if/else/return` produce un `TextChunk` con `is_valid_python_ast=True` y **nunca** emite `"else:"` como chunk aislado.
- Una función Python con un docstring malicioso (`"""Receta de empanadas caseras al horno con comino y cebolla picada fina."""`) emite el bloque `python_ast` **Y ADEMÁS** emite el docstring como chunk `prose_window` (`is_valid_python_ast=False`).
- Un script Bash o SQL no marca `is_valid_python_ast=True`.

**Comando de verificación del Slice 1:**
```bash
uv run pytest tests/lab_v2/test_a1_chunker.py && uv run ruff check ddi_fw/lab_v2 tests/lab_v2
```

---

## Slice 2 — Constructor Determinista de Corpus Real (`ddi_fw/lab_v2/corpus_builder.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/corpus_builder.py`
2. `tests/lab_v2/test_a2_corpus_builder.py`

### Problema que resuelve:
En v0.4.0 se calibró con prosa enciclopédica combinatoria y se filtró vocabulario con `Jaccard < 0.05`. Acá construimos un dataset **100% offline, reproducible (`seed=42`) y con código Python real** que cubre tanto código de sistemas como código de negocios, otros lenguajes y mundos abiertos no vistos.

### Especificación exacta de `ddi_fw/lab_v2/corpus_builder.py`:

```python
from dataclasses import dataclass
from typing import Literal

SplitName = Literal["train", "cal", "test"]
SampleCategory = Literal[
    "pos_stdlib_python",
    "pos_business_python",
    "neg_seen_domain",
    "neg_unseen_domain_ood",
    "neg_other_language",
    "neg_piggybacking",
]

@dataclass(frozen=True)
class BenchmarkSample:
    sample_id: str
    text: str
    is_legitimate_python: bool  # True para pos_*, False para neg_*
    category: SampleCategory
    split: SplitName
    subtag: str
```

**Composición exacta del dataset (`build_test_a_dataset(seed: int = 42) -> list[BenchmarkSample]`):**

1. **`pos_stdlib_python` (mínimo `300` funciones reales extraídas offline de la stdlib de Python):**
   - Importar e inspeccionar con `inspect.getsource(module)` y `ast.parse` una lista fija y ordenada de módulos estándar de Python:
     `["collections", "json.decoder", "json.encoder", "pathlib", "urllib.parse", "statistics", "csv", "configparser", "dataclasses", "heapq", "bisect", "functools", "difflib", "tarfile", "zipfile", "asyncio.queues", "asyncio.locks", "logging", "pprint", "textwrap"]`.
   - Extraer funciones/métodos con `5 <= n_lines <= 40` que pasen `ast.parse` por sí mismos (usando `textwrap.dedent`), eliminando duplicados exactos y ordenando por `sample_id` antes de barajar con `random.Random(seed)`. Tomar exactamente `300` muestras.
2. **`pos_business_python` (`60` funciones Python reales válidas con vocabulario intenso de negocios):**
   - Definir en un módulo auxiliar `ddi_fw/lab_v2/fixtures_code.py` `60` funciones Python reales (12 de finanzas/impuestos, 12 de medicina/farmacia, 12 de derecho/contratos, 12 de gastronomía/stock de cocina, 12 de astronomía/telemetría orbital), cada una verificada con `ast.parse` (con `typing`, `dataclasses` o aritmética real, ej. `calcular_dosis_mg_por_kg`, `liquidar_intereses_moratorios`, `escalar_gramos_harina_receta`).
   - *Propósito crítico:* Medir si el firewall bloquea erróneamente a un desarrollador Python cuando programa software para un hospital, banco, estudio jurídico o restaurante.
3. **`neg_seen_domain` (`200` muestras de prosa no-Python de 5 dominios VISTOS en `train`):**
   - Leer de `ddi_fw/data/trilingual/` únicamente los 5 dominios `("receta", "legal", "medicina", "astronomia", "finanzas")` (`40` cláusulas por dominio).
4. **`neg_unseen_domain_ood` (`150` muestras de prosa no-Python de 5 dominios JAMÁS VISTOS en `train`):**
   - Leer de `ddi_fw/data/trilingual/` los otros 5 dominios `("filosofia", "musica", "geologia", "botanica", "arquitectura")` (`30` cláusulas por dominio). **100% asignados a `split="test"`** (prohibido meter ni una sola muestra en `train` o `cal`).
5. **`neg_other_language` (`60` fragmentos reales de código que NO son Python):**
   - Definir en `ddi_fw/lab_v2/fixtures_code.py` `60` snippets reales (`15` JavaScript/TypeScript, `15` SQL DDL/DML, `15` Bash/Shell incluyendo pipelines `curl`/`chmod`, `15` Rust/C/Go). **100% asignados a `split="test"`**.
6. **`neg_piggybacking` (`90` ataques combinados sobre funciones Python del split `test`):**
   - Tomar `90` funciones de `pos_stdlib_python` que pertenezcan **exclusivamente al split `test`** (jamás `train` ni `cal` para no filtrar datos) e inyectar:
     - `30` con una consulta prohibida en un comentario/docstring interno,
     - `30` con una instrucción de otro dominio o prompt injection agregada después de la función,
     - `30` con un bloque Bash/SQL intercalado tras código Python válido.
   - **100% asignados a `split="test"`**.

**Partición estricta sin fuga de datos (`assert_no_leakage`):**
- Positivos (`pos_stdlib_python` y `pos_business_python` estratificados):
  - `50%` $\to$ `train` (`150` stdlib + `30` business = `180` positivos de entrenamiento),
  - `20%` $\to$ `cal` (`60` stdlib + `12` business = `72` positivos **exclusivos para calibración conformal**),
  - `30%` $\to$ `test` (`90` stdlib + `18` business = `108` positivos de test).
- Negativos:
  - `neg_seen_domain`: `60%` (`120` muestras) $\to$ `train` (solo para modelos supervisados `M1`/`M2`/`M3`), `40%` (`80` muestras) $\to$ `test`. (`cal` **no lleva negativos** porque Split Conformal calibra la tasa de falso rechazo $\alpha$ usando únicamente tráfico legítimo!).
  - `neg_unseen_domain_ood` (`150`), `neg_other_language` (`60`), `neg_piggybacking` (`90`) $\to$ **`100%` en `test`**.
- Validación obligatoria al final de `build_test_a_dataset`: verificar con `set.isdisjoint` que ningún `sample_id` ni `text` normalizado se repita entre `train`, `cal` y `test`.

**Comando de verificación del Slice 2:**
```bash
uv run pytest tests/lab_v2/test_a2_corpus_builder.py && uv run ruff check ddi_fw/lab_v2 tests/lab_v2
```

---

## Slice 3 — Los 4 Modelos en Duelo (`ddi_fw/lab_v2/models.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/models.py`
2. `tests/lab_v2/test_a3_models.py`

### Álgebra Lineal Exacta a Copiar sin Modificar (Cero `scikit-learn` requerido):

#### 1. Covarianza con Contracción Analítica de Ledoit-Wolf Vectorizada (Sin Loops):
```python
def ledoit_wolf_covariance(X: np.ndarray, min_shrinkage: float = 1e-3) -> tuple[np.ndarray, np.ndarray, float]:
    """Devuelve (mean_1d, cov_spd_2d, shrinkage_lambda) en float64."""
    X64 = np.asarray(X, dtype=np.float64)
    if X64.ndim != 2 or X64.shape[0] < 2:
        raise ValueError(f"X debe ser 2D con N >= 2, recibido: {X64.shape}")
    n, d = X64.shape
    mu = np.mean(X64, axis=0)
    Xc = X64 - mu
    S = (Xc.T @ Xc) / float(n)
    trace_s = float(np.trace(S))
    m = max(trace_s / float(d), 1e-12)
    diff = S - m * np.eye(d, dtype=np.float64)
    d2 = float(np.sum(diff * diff)) / float(d)
    if d2 <= 1e-24:
        lam = 1.0
    else:
        row_sq_norms = np.sum(Xc * Xc, axis=1)
        s_frob_sq = float(np.sum(S * S))
        b2_raw = (float(np.mean(row_sq_norms ** 2)) - s_frob_sq) / float(n * d)
        b2 = min(d2, max(0.0, b2_raw))
        lam = float(np.clip(b2 / d2, min_shrinkage, 1.0))
    cov = (1.0 - lam) * S + lam * m * np.eye(d, dtype=np.float64)
    return mu, cov, lam
```

#### 2. Cuantil Exacto de Split Conformal Prediction (0-indexed seguro):
```python
def conformal_threshold(cal_anomaly_scores: np.ndarray, alpha: float = 0.05) -> float:
    """Garantiza P(score_legit > q_hat) <= alpha en muestras intercambiables."""
    scores = np.sort(np.asarray(cal_anomaly_scores, dtype=np.float64).reshape(-1))
    n_cal = scores.shape[0]
    if n_cal < 1:
        raise ValueError("cal_anomaly_scores no puede estar vacío")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha debe estar en (0, 1), recibido: {alpha}")
    k_1based = min(n_cal, max(1, math.ceil((n_cal + 1) * (1.0 - alpha))))
    return float(scores[k_1based - 1])
```

### Interfaz Común e Implementación de los 4 Competidores:
Cada modelo recibe por muestra la lista de `TextChunk` y su matriz de embeddings correspondiente `chunk_vecs: np.ndarray` de forma `(n_chunks, D)`, y expone:
- `score_sample(chunks: list[TextChunk], chunk_vecs: np.ndarray) -> float`: devuelve un **score continuo de anomalía** (mayor valor = mayor probabilidad de violación / NO-Python). Esto permite trazar curvas ROC y PR exactas para los 4 modelos sin sesgos de umbral.
- `predict_breach(chunks: list[TextChunk], chunk_vecs: np.ndarray) -> bool`: devuelve `True` si bloquea la muestra.

1. **`M1_DdiBoxesBaseline` (`ddi-fw` v0.4.0 intacto):**
   - Entrena llamando a `ddi_fw.hoja.candados_canonicos` (con `RUIDO_UNIVERSAL_BGE_M3` si `D == 1024`, `modo_espectral=True`, `quorum_ratio=0.10`) sobre `"python"` (`train` positivos) y las 5 almas negativas vistas en `train`.
   - `predict_breach`: usa `ddi_fw.ingress.decide` con `Policy(allowed="python", forbidden=seen_neg_domains)`. Si cualquier chunk da `"BREACH"`, bloquea.
   - `score_sample`: para obtener el score continuo exacto de `M1`, para cada chunk calcula `min_votos_a` sobre todos los candados de `"python"` (y resta `1000` si algún candado vota `"right"` o `"split"`), y devuelve `float(-min_across_chunks)`. Así a menor cantidad de votos para Python, mayor score de anomalía.

2. **`M2_CosineMargin` (Diferencia de Coseno por Bloque + Calibración Conformal):**
   - Entrena calculando el centroide L2-normalizado $\hat{\mu}_{\text{python}}$ de los chunks positivos de `train` y los centroides L2-normalizados $\hat{\mu}_b$ de cada uno de los 5 dominios negativos vistos en `train`.
   - Para cada chunk con vector L2-normalizado $\hat{x}$:
     $$s_{\cos}(\hat{x}) = \max_{b} (\hat{x}^\top \hat{\mu}_b) - (\hat{x}^\top \hat{\mu}_{\text{python}})$$
   - `score_sample`: $\max_{c} s_{\cos}(\hat{x}_c)$.
   - `predict_breach`: compara `score_sample > q_hat` calibrado con `conformal_threshold` sobre los prompts de `cal` con $\alpha = 0.05$.

3. **`M3_WhitenedSpectralSubspace` (`EEB` — Ecualizador Espectral Blanqueado Puro en Embeddings):**
   - **Entrenamiento (solo `train`):**
     1. Apilar todos los vectores de chunks positivos de `train` ($X_+$) y todos los vectores de chunks negativos vistos de `train` ($X_-$).
     2. Calcular `(mu_pos, cov_pos, lam_pos) = ledoit_wolf_covariance(X_+)` y `(mu_neg, cov_neg, lam_neg) = ledoit_wolf_covariance(X_-)`.
     3. Covarianza intra-clase combinada: $\Sigma_W = \frac{N_+ \Sigma_+ + N_- \Sigma_-}{N_+ + N_-}$.
     4. Resolver dirección discriminante blanqueada de Fisher: `w_raw = np.linalg.solve(Sigma_W, mu_pos - mu_neg)`, normalizar `w_hat = w_raw / max(np.linalg.norm(w_raw), 1e-12)`.
     5. Extraer subespacio propio positivo para mundo abierto (OOD): aplicar `np.linalg.svd(X_+ - mu_pos, full_matrices=False)` obteniendo valores singulares `s_vals` y `Vt`. Elegir `k = min(48, Vt.shape[0] - 1, Vt.shape[1])` (con `k >= 1`), `U_k = Vt[:k].T` de forma `(D, k)` y varianzas propias $\gamma_j = \frac{s_j^2}{\max(1, N_+ - 1)} + 10^{-4}$.
     6. Para cada vector $x \in \mathbb{R}^D$, definir sus 3 componentes crudas:
        - `z_fisher(x) = -float(np.dot(x, w_hat))` (negado para que mayor = más anómalo),
        - `d_par_sq(x) = float(np.sum(((U_k.T @ (x - mu_pos)) ** 2) / gamma))`,
        - `d_orth_sq(x) = max(0.0, float(np.sum((x - mu_pos) ** 2) - np.sum((U_k.T @ (x - mu_pos)) ** 2)))`.
     7. Calcular sobre $X_+$ de `train` la mediana y el rango intercuartílico robusto `iqr = max(np.percentile(v, 75) - np.percentile(v, 25), 1e-6)` de cada una de las 3 componentes para estandarizarlas sin outliers: $\tilde{z}_m(x) = \frac{v_m(x) - \text{med}_m}{\text{iqr}_m}$.
     8. Score de chunk: $s_{\text{EEB}}(x) = 0.50 \tilde{z}_{\text{fisher}}(x) + 0.20 \tilde{z}_{\parallel}(x) + 0.30 \tilde{z}_{\perp}(x)$.
   - **Calibración (`cal`):** Calcular `S_prompt = max_c s_EEB(x_c)` sobre cada muestra positiva de `cal` y fijar `q_hat = conformal_threshold(cal_scores, alpha=0.05)`.
   - `score_sample`: `max_c s_EEB(x_c)`. `predict_breach`: `score_sample > q_hat`.

4. **`M4_HybridAstSpectral` (Defensa en Profundidad Pragmática: `AST` + `M3`):**
   - Igual a `M3`, pero aprovecha el metadato determinista `chunk.is_valid_python_ast` calculado en el Slice 1:
     - Si un chunk tiene `chunk.is_valid_python_ast == True` (código Python sintácticamente verificado por el parser oficial de Python), solo evalúa su residuo extremo de anomalía con descuento estructural (`s_EEB(x_c) - 1.5`), evitando falsos rechazos por nombres de variables médicas o financieras.
     - Todos los chunks con `is_valid_python_ast == False` (prosa libre, comentarios largos, docstrings, otros lenguajes JS/SQL/Bash, inyecciones *piggybacking*) reciben el peso completo de `s_EEB(x_c)` (y penalización `+1.0` si `chunk.kind == "fenced_code"` y falló `ast.parse`, bloqueando instantáneamente bloques de código en otros lenguajes!).
   - Calibra su propio `q_hat` en `cal` con `conformal_threshold(..., alpha=0.05)` usando exactamente la misma regla, sin magia manual.

### Tests obligatorios en `tests/lab_v2/test_a3_models.py`:
- Testear `ledoit_wolf_covariance` con $N = 15, D = 128$ ($N \ll D$) y verificar que `np.linalg.eigvalsh(cov).min() > 0`.
- Construir un problema sintético anisotrópico en $\mathbb{R}^{64}$ donde dos clases están separadas `6 sigma` en el eje `0`, pero comparten un ruido gaussiano enorme (`sigma = 20`) en los ejes `1..10`: demostrar en el test que `M3_WhitenedSpectralSubspace` logra `ROC-AUC > 0.98` mientras `M2_CosineMargin` cae por debajo de `0.75` y `M1_DdiBoxesBaseline` colapsa.

**Comando de verificación del Slice 3:**
```bash
uv run pytest tests/lab_v2/test_a3_models.py && uv run ruff check ddi_fw/lab_v2 tests/lab_v2
```

---

## Slice 4 — Métricas Exactas, Runner y Reporte Honesto (`ddi_fw/lab_v2/metrics.py` + `scripts/lab_v2/run_test_a.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/metrics.py`
2. `scripts/lab_v2/run_test_a.py`
3. `tests/lab_v2/test_a4_metrics_and_runner.py`

### Métricas en NumPy Puro (`ddi_fw/lab_v2/metrics.py`):
- `compute_roc_auc(pos_legit_scores: np.ndarray, neg_attack_scores: np.ndarray) -> float`:
  Probabilidad exacta de Mann-Whitney / Wilcoxon de que una muestra negativa (ataque/no-Python, etiqueta `1`) tenga score de anomalía mayor que una muestra positiva legítima (etiqueta `0`), tratando empates con peso `0.5`:
  ```python
  # Vectorizado exacto sin aproximación:
  diffs = neg_attack_scores[:, None] - pos_legit_scores[None, :]
  wins = np.sum(diffs > 0) + 0.5 * np.sum(diffs == 0)
  auc = float(wins) / float(len(neg_attack_scores) * len(pos_legit_scores))
  ```
- `compute_pr_auc(pos_legit_scores: np.ndarray, neg_attack_scores: np.ndarray) -> float`: Average Precision exacto ordenando por score descendente.
- `compute_far_at_frr(pos_legit_scores: np.ndarray, neg_attack_scores: np.ndarray, max_frr: float) -> float`: Fija el umbral en el cuantil `1.0 - max_frr` de `pos_legit_scores` y devuelve la fracción de `neg_attack_scores` que quedan `<= umbral` (ataques no detectados = False Acceptance Rate).
- Desglose obligatorio por subcategoría en `test`:
  - `frr_stdlib_python` (tasa de bloqueo erróneo en Python stdlib),
  - `frr_business_python` (tasa de bloqueo erróneo en Python de negocios),
  - `far_seen_domain` (fugas en los 5 dominios conocidos),
  - `far_unseen_domain_ood` (fugas en los 5 dominios nunca vistos),
  - `far_other_language` (fugas de JS/SQL/Bash/Rust),
  - `far_piggybacking` (fugas de ataques combinados),
  - `latency_ms_p50`, `latency_ms_p95`, `latency_ms_p99` del scoring por muestra (excluyendo tiempo de carga inicial del modelo).

### Regla Objetiva de Veredicto (`determine_test_a_verdict` — Cero Hardcodeo):
```python
def determine_test_a_verdict(m1_stats: dict, m2_stats: dict, m3_stats: dict, m4_stats: dict) -> dict[str, object]:
    m3_beats_cosine = (
        (m3_stats["roc_auc"] >= m2_stats["roc_auc"] + 0.01)
        or (m3_stats["far_at_frr_05"] <= m2_stats["far_at_frr_05"] - 0.03)
    )
    ranking = sorted(
        [("M1_DDI_v040", m1_stats), ("M2_Cosine", m2_stats), ("M3_EEB_Pure", m3_stats), ("M4_Hybrid_AST_EEB", m4_stats)],
        key=lambda item: (item[1]["roc_auc"], -item[1]["far_at_frr_05"]),
        reverse=True,
    )
    return {
        "overall_winner": ranking[0][0],
        "pure_embedding_winner": "M3_EEB_Pure" if m3_beats_cosine else "M2_Cosine",
        "m3_beats_cosine_empirically": bool(m3_beats_cosine),
        "m1_ddi_v040_viable": bool(m1_stats["frr_total"] < 0.25 and m1_stats["far_total"] < 0.10),
    }
```

### Salidas obligatorias de `scripts/lab_v2/run_test_a.py`:
1. Aceptar `--embedder bge` (default, carga `BAAI/bge-m3`) y `--embedder fake` (para test unitario rápido del runner).
2. Guardar todos los números crudos sin redondear en `reports/lab_v2_test_a_results.json` (respetando `cero-redondeos.md`).
3. Generar `reports/test_a_duelo_subespacio_vs_coseno.md` usando raw strings (`r"""..."""`) con las tablas comparativas completas y el veredicto devuelto por `determine_test_a_verdict`.

### Tests obligatorios en `tests/lab_v2/test_a4_metrics_and_runner.py`:
- Verificar que `determine_test_a_verdict` devuelve `"M2_Cosine"` cuando a `m2_stats` se le pasan mejores métricas que a `m3_stats`, y `"M3_EEB_Pure"` en el caso inverso (prueba anti-hardcodeo).
- Correr el pipeline end-to-end con `FakeEmbedder` en un directorio temporal `tmp_path` verificando que se crean el `.json` (sin strings truncados a 2 decimales) y el `.md` (sin caracteres ASCII `\x0b` ni `\t` sueltos en fórmulas).

**Comandos finales de verificación y ejecución real del Slice 4:**
```bash
uv run pytest && uv run ruff check ddi_fw/lab_v2 scripts/lab_v2 tests/lab_v2
uv run python scripts/lab_v2/run_test_a.py --embedder bge
```


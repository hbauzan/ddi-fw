# 06 — Protocolo de Graduación al Core Productivo (`TASK-006`): `ddi-fw v0.5.0` Dual-Pillar Runtime

**ID de Tarea:** `TASK-006`  
**Prerrequisitos:** `TASK-001`..`TASK-005` (`DONE` y consolidados en `main`)  
**Objetivo:** Graduar los motores probados en `ddi_fw/lab_v2/` (`M4_HybridAstSpectral` + `ContextCompiler`) hacia el runtime productivo de `ddi-fw v0.5.0`, cerrando los puntos ciegos del proxy legacy (`_last_user_text`), endureciendo geométricamente `M3`/`M4` con anclas negativas multilenguaje, serializando el estado calibrado en `.npz` sin `pickle` (`allow_pickle=False`), y preservando el 100% de compatibilidad con los 67 tests legacy D01–D06 (`v1_boxes`).

---

## 1. Arquitectura de Graduación `ddi-fw v0.5.0` (Cero Regresión en `v1_boxes`)

1. **Coexistencia Limpia (`v1_boxes` + `v2_spectral_ast`)**:
   - No se eliminan ni rompen `ddi_fw/hoja.py`, `ddi_fw/corte.py`, `ddi_fw/ingress.py`, `ddi_fw/egreso.py` ni `ddi_fw/press.py`. Los `67` tests de `tests/test_*.py` y los `44` tests de `tests/lab_v2/test_*.py` (`111` tests actuales) deben seguir pasando al `100%`.
   - Se agregan dos módulos de primera clase en la raíz del paquete `ddi_fw/`:
     - `ddi_fw/v2_calibration.py`: Anclas negativas de código ajeno de entrenamiento (`FOREIGN_TRAIN_ANCHORS`, disjuntas de `FOREIGN_SNIPPETS` de Test A), entrenamiento y calibración Split Conformal de `M4_HybridAstSpectral`, y persistencia determinista `.npz` con `allow_pickle=False`.
     - `ddi_fw/v2_firewall.py`: Motor de inspección productiva `SpectralAstFirewall` con caché LRU determinista por `SHA-256` de cada chunk, inspección multi-turno completa (`user`, `system`, `developer`, `tool`) e inspección de `egreso hold`.
   - Se extienden `ddi_fw/config.py` y `ddi_fw/proxy.py` para soportar `engine_mode="v2_spectral_ast"` y el middleware activo `ContextCompiler` (`ddi_compile_context` / `context_compiler_enabled`) sobre `POST /v1/chat/completions`, y se actualiza la versión del paquete a `"0.5.0"`.

---

## 2. Especificación Exacta por Vertical Slices

### Slice 1 — Endurecimiento Geométrico Multilenguaje y Persistencia `.npz` sin Pickle (`ddi_fw/v2_calibration.py` + `tests/test_v050_calibration.py`)

1. **Anclas de entrenamiento de código ajeno (`FOREIGN_TRAIN_ANCHORS`)**:
   - En `ddi_fw/v2_calibration.py`, definir `FOREIGN_TRAIN_ANCHORS: tuple[tuple[str, str, str], ...]` con **`36` fragmentos de código real en `6` lenguajes** (`6` de `javascript`, `6` de `sql`, `6` de `bash`, `6` de `rust`, `6` de `c`, `6` de `go`).
   - **Invariante de No-Leakage**: Verificar con una función `assert_disjoint_from_test_a()` (y en `pytest`) que ningún texto normalizado (`normalize_text`) ni identificador de `FOREIGN_TRAIN_ANCHORS` coincida con los `60` `FOREIGN_SNIPPETS` ni con ningún sample de `cal` o `test` de `build_test_a_dataset(seed=42)`.
   - Al entrenar `M3_WhitenedSpectralSubspace` o `M4_HybridAstSpectral` mediante `fit_v2_spectral_ast(embedder, *, alpha: float = 0.05, seed: int = 42, include_foreign_code_anchors: bool = True)`:
     - La matriz positiva $X_{\text{pos,train}}$ contiene los chunks embebidos de `train` positivos (`pos_stdlib_python` + `pos_business_python`).
     - La matriz negativa $X_{\text{neg,train}}$ apila (`np.vstack`) los chunks embebidos de `neg_seen_domain` (`train`) **más** los chunks embebidos de `FOREIGN_TRAIN_ANCHORS` cuando `include_foreign_code_anchors=True`.
     - El umbral conformal $\hat{q}_{1-\alpha}$ se calibra sobre los `72` grupos positivos de `cal` con `conformal_threshold(..., alpha=alpha)`.

2. **Serialización `.npz` Estricta sin Pickle (`allow_pickle=False`)**:
   - Implementar `save_v2_calibration(path: Path, model: M4_HybridAstSpectral, *, model_id: str, alpha: float = 0.05) -> Path` y `load_v2_calibration(path: Path) -> tuple[M4_HybridAstSpectral, dict[str, object]]`:
     - Guardar en `np.savez_compressed(path, ...)` únicamente arreglos numéricos nativos:
       - `mu_pos`, `w_hat`, `u_k`, `gamma`, `medians`, `iqrs` en `np.float64`
       - `q_hat`, `shrinkage_pos`, `shrinkage_neg`, `alpha` como arreglos escalares `np.float64`
       - `dimension`, `subspace_rank` como arreglos escalares `np.int64`
       - `model_id_utf8 = np.frombuffer(model_id.encode("utf-8"), dtype=np.uint8)` (para almacenar el string sin usar `dtype=object` ni `pickle`).
     - En `load_v2_calibration(path)`, abrir **obligatoriamente** con `np.load(path, allow_pickle=False)` y reconstruir una instancia funcional de `M4_HybridAstSpectral` idéntica bit a bit (`np.array_equal` en todos los tensores y `score_sample` idéntico en `float64`).
   - Proveer CLI `main(argv)` en `ddi_fw/v2_calibration.py` (`--embedder bge-m3|fake`, `--out ddi_fw/out/v2_spectral_ast.npz`, `--alpha 0.05`) y registrar `ddi-calibrate-v2 = "ddi_fw.v2_calibration:main"` en `pyproject.toml`.

---

### Slice 2 — Motor `SpectralAstFirewall` Multi-Turno con Caché SHA-256 por Chunk (`ddi_fw/v2_firewall.py` + `tests/test_v050_firewall.py`)

1. Crear `ddi_fw/v2_firewall.py` con:
   - `@dataclass(frozen=True) class ChunkAudit`: `chunk_kind: str`, `is_valid_python_ast: bool`, `start_line: int`, `end_line: int`, `score: float`, `cached: bool`, `role: str = "user"`, `message_index: int = 0`.
   - `@dataclass(frozen=True) class V2FirewallResult`:
     - `verdict: Literal["PASS", "BREACH"]`
     - `max_score: float`
     - `threshold_q_hat: float`
     - `chunk_count: int`
     - `cache_hits: int`
     - `cache_misses: int`
     - `reason: str`
     - `chunks: tuple[ChunkAudit, ...] = ()`
     - Propiedad `audit -> list[dict[str, object]]`: serializa cada `ChunkAudit` con `float(score)` nativo (cumpliendo `.agents/rules/cero-redondeos.md`, sin incluir el texto crudo del prompt para respetar `403 sin echo`).
2. Clase `SpectralAstFirewall`:
   - Constructor `__init__(self, model: M4_HybridAstSpectral, embedder: BaseEmbedder, *, max_cache_entries: int = 4096)`:
     - Valida que `model.q_hat is not None` y `model.dimension == embedder.dimension`.
     - Mantiene un `OrderedDict[str, float]` acotado a `max_cache_entries` cuya clave es:
       `hashlib.sha256(f"{chunk.kind}\0{int(chunk.is_valid_python_ast)}\0{chunk.text}".encode("utf-8")).hexdigest()`.
   - Método `inspect_text(self, text: str, *, role: str = "user", message_index: int = 0) -> V2FirewallResult`:
     - **Fail-closed total**: si `text` es `None`/vacío, si `extract_chunks(text)` devuelve `[]`, o si `embedder.embed_batch` lanza excepción, devuelve `V2FirewallResult(verdict="BREACH", ..., reason="empty_chunks" | "embedder_down:...")`.
     - Para los chunks extraídos:
       - Consulta el caché LRU por clave SHA-256.
       - Embebe en un único lote (`embedder.embed_batch`) **únicamente** los chunks con cache miss, calcula su score ajustado de `M4_HybridAstSpectral` (`_eeb_scores` + `_adjust`), y los inserta en el caché LRU.
       - Si $\max_c s(c) > \hat{q}_{1-\alpha}$, retorna `verdict="BREACH"`, `reason="conformal_threshold_exceeded"`; en caso contrario retorna `verdict="PASS"`, `reason="all_chunks_within_conformal_bound"`.
   - Método `inspect_messages(self, messages: list[dict[str, Any]], *, inspect_roles: frozenset[str] = frozenset({"user", "system", "developer", "tool"})) -> V2FirewallResult`:
     - Extrae el texto de cada mensaje cuyo `role` pertenezca a `inspect_roles` (soportando tanto `content: str` como `content: list[dict]` estilo OpenAI).
     - Exige que exista al menos un mensaje con `role == "user"` y contenido no vacío (si no existe, retorna `verdict="BREACH"`, `reason="missing_user_message"`).
     - Evalúa todos los mensajes seleccionados compartiendo el caché SHA-256 y agrega con el máximo global peor-caso $\max_{m, c} s(m, c)$. Si cualquier mensaje produce `"BREACH"`, el resultado global es `"BREACH"`.

---

### Slice 3 — Integración en Proxy OpenAI-Compatible (`ddi_fw/config.py` + `ddi_fw/proxy.py` + `tests/test_v050_proxy.py`)

1. En `ddi_fw/config.py` (`Settings`):
   - Agregar campos con defaults 100% retrocompatibles:
     - `engine_mode: Literal["v1_boxes", "v2_spectral_ast"] = "v1_boxes"`
     - `v2_calibration_path: Path = Field(default=Path("ddi_fw/out/v2_spectral_ast.npz"))`
     - `context_compiler_enabled: bool = False`
     - `context_max_budget_tokens: int = 36000`
     - `context_fresh_tail_turns: int = 6`
2. En `ddi_fw/proxy.py` (`create_app`):
   - Firma extendida retrocompatible:
     ```python
     def create_app(
         settings: Settings | None = None,
         *,
         embedder: BaseEmbedder | None = None,
         candados: dict | None = None,
         v2_firewall: SpectralAstFirewall | None = None,
         transport: httpx.BaseTransport | None = None,
     ) -> FastAPI:
     ```
   - Subir versión en `ddi_fw/__init__.py`, `pyproject.toml` y `FastAPI(..., version="0.5.0")` a `"0.5.0"`.
   - Si `v2_firewall is not None` o `cfg.engine_mode == "v2_spectral_ast"`:
     - Si `v2_firewall is None` y `cfg.v2_calibration_path.is_file()`, cargarlo automáticamente con `load_v2_calibration(cfg.v2_calibration_path)` + `worker`.
     - En `GET /healthz`: conservar las claves `"status"`, `"embedder"`, `"spectral_mode"`, `"locks"` y agregar `"version": "0.5.0"`, `"engine_mode": active_engine_mode`, `"context_compiler_enabled": bool(cfg.context_compiler_enabled)`. Cuando `active_engine_mode == "v2_spectral_ast"`, `status` es `"ok"` si `app.state.v2_firewall is not None` y `"degraded"` si falta calibrar.
     - En `POST /v1/chat/completions`:
       1. Si falta un mensaje `role == "user"` con texto válido (`_last_user_text(messages) is None`), devolver `400` `ddi_bad_request` `"falta mensaje de usuario"`.
       2. Si `active_engine_mode == "v2_spectral_ast"`:
          - Si `app.state.v2_firewall is None`, devolver `403` `ddi_ingress_breach` (fail-closed, `"v2_firewall_uncalibrated"`).
          - Ejecutar `ingress_v2 = app.state.v2_firewall.inspect_messages(messages)`. Si `ingress_v2.verdict == "BREACH"`, devolver `403` `ddi_ingress_breach` con `ingress_v2.audit` (cero eco del prompt).
       3. **Middleware `ContextCompiler` (disponible en ambos motores cuando `cfg.context_compiler_enabled` es `True` o `payload.get("ddi_compile_context") is True`)**:
          - Ejecutar `compiled = compile_session_context(normalized_messages, max_budget_tokens=cfg.context_max_budget_tokens, fresh_tail_turns=cfg.context_fresh_tail_turns)`.
          - Reemplazar `outbound["messages"] = compiled.messages` al llamar a `call_upstream` (removiendo la clave opcional `"ddi_compile_context"` del payload enviado al upstream).
          - Adjuntar en el JSON de respuesta `200`:
            ```python
            completion["ddi_context_governor"] = {
                "original_tokens": compiled.original_tokens,
                "compiled_tokens": compiled.compiled_tokens,
                "compression_ratio": compiled.compression_ratio,
                "superseded_blocks_pruned": compiled.superseded_blocks_pruned,
                "stale_traces_pruned": compiled.stale_traces_pruned,
            }
            ```
       4. **Egreso Hold en `v2_spectral_ast`**:
          - Evaluar `generated` con `egress_v2 = app.state.v2_firewall.inspect_text(generated, role="assistant")`. Si `egress_v2.verdict == "BREACH"`, devolver `403` `ddi_egreso_breach` con `egress_v2.audit` (cero eco de `generated`).

---

### Slice 4 — Auditoría Empírica de Defensa en Profundidad (`BAAI/bge-m3`) y Cierre `TASK-006` (`scripts/lab_v2/run_v050_graduation_check.py`)

1. Crear `scripts/lab_v2/run_v050_graduation_check.py` (con flag `--embedder bge|fake`) que:
   - Entrene sobre el split `train` + `cal` del Test A dos variantes de `M3_WhitenedSpectralSubspace` y `M4_HybridAstSpectral`:
     - **Baseline (`prose_only_negatives`)**: $X_{\text{neg}}$ solo con prosa (`SEEN_DOMAINS`).
     - **Hardened v0.5.0 (`multilang_hardened_negatives`)**: $X_{\text{neg}}$ con prosa (`SEEN_DOMAINS`) + `FOREIGN_TRAIN_ANCHORS` (`36` snippets de JS/SQL/Bash/Rust/C/Go disjuntos de `test`).
   - Evalúe ambas variantes sobre los `488` samples de `test` del Test A y verifique el roundtrip `.npz` (`allow_pickle=False`) y el speedup del caché SHA-256 en una sesión multi-turno repetida.
   - Escriba `reports/v050_graduation_audit.json` y `reports/v050_graduation_audit.md` con precisión nativa IEEE 754 (`format(x, '.17g')`, cero redondeos) y fórmulas LaTeX en raw strings.
2. Agregar test de humo en `tests/test_v050_graduation.py` (`--embedder fake`) y correr una vez con `BAAI/bge-m3` real:
   ```bash
   uv run python scripts/lab_v2/run_v050_graduation_check.py --embedder bge
   ```
3. Verificar toda la suite (`uv run pytest` y `uv run ruff check ddi_fw scripts/lab_v2 tests`), actualizar `.agents/skills/dev-protocol/lessons-learned.md`, pasar `TASKS.md` a `status: "DONE"` y notificar con `agent.sh notify`.


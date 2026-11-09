# 02 — Especificación Paso a Paso del TEST B (`TASK-002`)
## Telemetría Cinemática de Sesiones Largas (>250k Tokens), Índice AST Vivo y Compilador Activo de Contexto

**Objetivo:** Evaluar empíricamente qué señales locales detectan y previenen la degradación real de LLMs en sesiones de programación de **250.000+ tokens** (*Context Rot*), contrastando seguimiento por coseno crudo vs. trayectoria cinemática blanqueada + verificación de firmas AST vivas + compilación activa de contexto (`260k -> < 36k` tokens).

> [!WARNING]
> **REGLAS ESTRICTAS PARA EL AGENTE EJECUTOR:**
> - **NO tocar** `ddi_fw/hoja.py`, `ddi_fw/corte.py`, `ddi_fw/ingress.py`, `ddi_fw/egreso.py`, `ddi_fw/proxy.py` ni borrar los módulos del Test A en `ddi_fw/lab_v2/`.
> - **NO leer** ningún archivo dentro de `roadmap/future-notes/`.
> - Todo el Test B debe poder ejecutarse **100% offline** sin claves de API externas (y exponer un flag opcional `--live-api` apagado por defecto).

---

## Slice 1 — Índice Evolutivo de Símbolos AST y Huella Estructural (`ddi_fw/lab_v2/ast_symbol_index.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/ast_symbol_index.py`
2. `tests/lab_v2/test_b1_ast_symbol_index.py`

### Problema de los >250k tokens que resuelve:
En sesiones largas, una función se define en el turno 10 (`def liquidar_orden(monto, tasa):`), se refactoriza en el turno 65 (`def liquidar_orden(centavos: int, bps_impuesto: int, moneda: str):`), y a los 250k tokens el LLM mezcla el historial y vuelve a invocar `liquidar_orden(100, 0.21)` o llama un método inexistente en una clase local.

### Especificación exacta de `ddi_fw/lab_v2/ast_symbol_index.py`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class FunctionSig:
    qualname: str          # ej. "liquidar_orden" o "OrderProcessor.run"
    min_pos_args: int      # posicionales obligatorios (excluyendo self/cls)
    max_pos_args: int | None  # None si tiene *args
    required_kwonly: frozenset[str]
    allowed_kwargs: frozenset[str] | None  # None si tiene **kwargs
    turn_id: int

@dataclass(frozen=True)
class AstViolation:
    kind: str  # "syntax_error" | "deprecated_signature_call" | "arity_mismatch" | "unknown_class_method"
    symbol: str
    detail: str
    deprecated_from_turn: int | None = None
```

**Funciones y clases públicas obligatorias:**
1. `extract_python_blocks(message_text: str) -> list[str]`:
   Extrae bloques ```` ```python ... ``` ```` (o todo el texto si pasa `ast.parse` directo).
2. `compute_structural_ast_hash(code: str) -> str | None`:
   Si `code` pasa `ast.parse`, elimina docstrings iniciales (`Constant(str)` en primer statement de `Module`/`FunctionDef`/`ClassDef`), renombra variables locales e identificadores de parámetros a nombres canónicos posicionales o usa `ast.dump(tree, annotate_fields=True, include_attributes=False)` y devuelve `hashlib.sha256(...).hexdigest()`. Si no parsea, devuelve `None`.
3. `class LiveSymbolIndex`:
   - `ingest_accepted_turn(turn_id: int, code_blocks: list[str]) -> None`:
     Recorre `FunctionDef`, `AsyncFunctionDef` y métodos dentro de `ClassDef`. Si `qualname` ya existía en `self.live_signatures` con **distinta** firma (`min_pos_args`, `max_pos_args`, `required_kwonly` o `allowed_kwargs`), mueve la firma anterior a `self.deprecated_history[qualname]` antes de actualizar `self.live_signatures[qualname]`, y actualiza el conjunto de métodos conocidos de cada `ClassDef` local (`self.class_methods[class_name]`).
   - `audit_candidate_code(code: str) -> list[AstViolation]`:
     1. Si `ast.parse(code)` lanza `SyntaxError`, devuelve `[AstViolation(kind="syntax_error", ...)]`.
     2. Inspecciona cada `ast.Call` sobre funciones conocidas en `self.live_signatures`:
        - Verifica cantidad de argumentos posicionales (`len(node.args)`) y nombres de `node.keywords`.
        - Si **falla** contra la firma viva actual, verifica si **coincidía** con alguna firma vieja en `self.deprecated_history[qualname]`: en ese caso emite `kind="deprecated_signature_call"` con `deprecated_from_turn=old_sig.turn_id`! En caso contrario emite `kind="arity_mismatch"`.
     3. Si detecta instanciación local `x = MyKnownClass(...)` seguida de `x.metodo_inventado(...)` donde `MyKnownClass` está en `self.class_methods` y `metodo_inventado` no existe en esa clase, emite `kind="unknown_class_method"`.

### Tests obligatorios en `tests/lab_v2/test_b1_ast_symbol_index.py`:
- Ingerir turno 5 con `def calc(a, b): return a + b`, luego turno 40 con `def calc(a, b, currency): return a + b`. Auditar `res = calc(10, 20)` y verificar que detecta exactamente `deprecated_signature_call` apuntando a `deprecated_from_turn == 5`.
- Verificar que `compute_structural_ast_hash` produce el mismo hash aunque cambien comentarios o saltos de línea, y distinto hash cuando cambia un operador `+` por `-`.

**Comando de verificación del Slice 1:**
```bash
uv run pytest tests/lab_v2/test_b1_ast_symbol_index.py && uv run ruff check ddi_fw/lab_v2 tests/lab_v2
```

---

## Slice 2 — Monitor Cinemático de Trayectoria y Memoria Negativa (`ddi_fw/lab_v2/trajectory_monitor.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/trajectory_monitor.py`
2. `tests/lab_v2/test_b2_trajectory_monitor.py`

### Especificación matemática exacta (4 señales por turno):
Usar un operador de blanqueo diagonal/Ledoit-Wolf liviano `W_inv_sqrt` (o identidad en modo baseline coseno crudo para poder comparar **Coseno Crudo vs. Blanqueado**):
Dado un vector de proyección blanqueada $\tilde{u} = \frac{M (u - \vec{\mu})}{\|M (u - \vec{\mu})\|_2 + 10^{-12}}$ (donde en modo `"raw_cosine"`, $M = I$ y $\vec{\mu} = 0$; en modo `"whitened"`, $M = \Sigma_{\lambda}^{-1/2}$ estimado con `ledoit_wolf_covariance` del Test A):

1. **Alineación con el Ancla de Objetivo (`goal_alignment` $\alpha_t \in [-1, 1]$):**
   $$\alpha_t = \tilde{e}_t^{\top} \tilde{e}_{\text{anchor}}$$
   donde $\tilde{e}_{\text{anchor}}$ es el embedding del prompt de especificación inicial (turno 0/1).
2. **Velocidad de Paso Semántico (`step_velocity` $\nu_t \ge 0$):**
   $$\nu_t = \|\tilde{e}_t - \tilde{e}_{t-1}\|_2 \quad (\nu_0 = 1.0)$$
3. **Resonancia con Memoria Negativa (`neg_resonance` $\rho_t \in [-1, 1]$ + match estructural AST):**
   Cada respuesta previa marcada con `accepted=False` (falló tests o fue rechazada) se almacena en `NegativeMemoryEntry(turn_id, reason, whitened_vec, ast_hashes)`:
   $$\rho_t = \max_{j \in \mathcal{F}_{<t}} \big(\tilde{e}_t^{\top} \tilde{e}_j^{\text{failed}}\big) \quad (\text{o } 0.0 \text{ si } \mathcal{F}_{<t} = \emptyset)$$
   Además `exact_ast_loop = bool(current_ast_hashes & failed_ast_hashes)`.
4. **Ratio de Contaminación del Historial (`context_pollution` $H_{\text{ctx}}(t) \in [0, 1]$):**
   $$H_{\text{ctx}}(t) = \frac{\text{tokens de bloques de código ya sobrescritos} + \text{tokens de stack traces viejos (> 3 turnos atrás)}}{\max(1,\ \text{tokens totales acumulados en } \text{messages}[])}$$

### Reglas de Alerta y Generación de Re-Prompt Quirúrgico (`evaluate_turn`):
Emitir `TurnAlert` cuando ocurra cualquiera de:
- `ast_violations` no vacía $\implies$ alerta `"AST_CONTRACT_BREACH"`,
- `exact_ast_loop` o `rho_t >= 0.90` $\implies$ alerta `"THRASHING_LOOP_DETECTED"`,
- `alpha_t < anchor_floor` durante `2` turnos consecutivos $\implies$ alerta `"GOAL_DRIFT_DETECTED"`,
- `nu_t < 0.05` tras un turno fallido $\implies$ alerta `"COSMETIC_STAGNATION"`.

Implementar `build_surgical_reprompt(alert: TurnAlert) -> str`: devuelve una instrucción concisa y determinista indicando exactamente qué símbolo/turno falló o qué parche fallido previo se está repitiendo, lista para inyectarse como mensaje correctivo a Gemini/Claude/Grok/ChatGPT.

**Comando de verificación del Slice 2:**
```bash
uv run pytest tests/lab_v2/test_b2_trajectory_monitor.py && uv run ruff check ddi_fw/lab_v2 tests/lab_v2
```

---

## Slice 3 — Compilador Activo de Contexto 250k $\to$ <40k (`ddi_fw/lab_v2/context_compiler.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/context_compiler.py`
2. `tests/lab_v2/test_b3_context_compiler.py`

### Especificación exacta de `compile_session_context`:
 Estimador determinista de tokens sin librerías externas:
```python
def estimate_tokens(text: str) -> int:
    # Aproximación determinista estándar ~4 chars/token + palabras
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)
```

Función principal:
```python
@dataclass(frozen=True)
class CompiledContextResult:
    messages: list[dict[str, str]]
    original_tokens: int
    compiled_tokens: int
    compression_ratio: float
    superseded_blocks_pruned: int
    stale_traces_pruned: int
```

**Algoritmo determinista de compilación (`max_budget_tokens: int = 36000`, `fresh_tail_turns: int = 6`):**
1. Si `original_tokens <= max_budget_tokens`, devolver copia intacta (salvo reemplazo opcional de firmas deprecadas si `force_hygiene=True`).
2. Si supera `max_budget_tokens`:
   - **Bloque 1 — Invariantes Fijados (Intocables):** Conservar íntegros todos los mensajes `role == "system"` y el primer mensaje `role == "user"` que define la arquitectura/objetivo del proyecto.
   - **Bloque 2 — Estado Sintáctico Vivo + Memoria Negativa (Mensaje Sintético de Gobernador):** Insertar un mensaje compacto `[DDI-CONTEXT-GOVERNOR]` listando:
     - Todas las firmas vivas actuales en `LiveSymbolIndex` (y explícitamente qué firmas viejas quedaron prohibidas/deprecadas),
     - Hasta los últimos `8` ítems de `NegativeMemory` (`turno`, `motivo del fallo`) para evitar que el LLM repita parches rotos tras la poda.
   - **Bloque 3 — Ventana Fresca Final:** Conservar íntegros los últimos `fresh_tail_turns` mensajes de la conversación.
   - **Bloque 4 — Poda y Selección de Turnos Intermedios:**
     - En todos los turnos intermedios (`1 .. N - fresh_tail_turns`), reemplazar bloques ```` ```python ... ``` ```` cuyas funciones ya fueron redefinidas en un turno posterior por un *tombstone* de 1 línea: `"[DDI-TOMBSTONE: versión obsoleta de <simbolos> reemplazada en turno posterior]"`, y truncar *stack traces* (`Traceback (most recent call last): ...`) de más de 5 líneas ya resueltos a su última línea `ErrorType: mensaje`.
     - Ordenar los turnos intermedios restantes por similitud blanqueada contra la consulta actual del usuario y agregarlos en orden cronológico hasta completar `max_budget_tokens`.

### Tests obligatorios en `tests/lab_v2/test_b3_context_compiler.py`:
- Generar una sesión sintética de `260,000` tokens (~1.04M caracteres) con un invariante inicial, una función refactorizada 3 veces, 40 *tracebacks* largos y una consulta final. Verificar que:
  1. `compiled_tokens <= 36000` (reducción `> 85%`),
  2. El invariante del turno inicial sigue presente al `100%`,
  3. La firma viva actual está presente al `100%` y las versiones viejas del código fueron reemplazadas por *tombstones*,
  4. Tiempo de ejecución de `compile_session_context` es `< 250 ms`.

**Comando de verificación del Slice 3:**
```bash
uv run pytest tests/lab_v2/test_b3_context_compiler.py && uv run ruff check ddi_fw/lab_v2 tests/lab_v2
```

---

## Slice 4 — Simulador de Sesiones de 250k–300k Tokens, Lector `.jsonl` y Runner (`ddi_fw/lab_v2/session_simulator.py` + `scripts/lab_v2/run_test_b.py`)

### Archivos a crear:
1. `ddi_fw/lab_v2/session_simulator.py`
2. `scripts/lab_v2/run_test_b.py`
3. `tests/lab_v2/test_b4_session_benchmark.py`

### Especificación del Benchmark de Sesiones Largas (`session_simulator.py`):
Construir un generador determinista (`seed=42`) de **`16` sesiones completas de programación que escalan hasta `250,000–300,000` tokens cada una** (`~80` a `110` turnos por sesión, rellenando los turnos intermedios con código real extraído de stdlib, lecturas de archivos reales del repo y salidas realistas de `pytest`/logs para alcanzar el volumen real de `>250k` tokens!), repartidas en **4 arquetipos con etiquetas exactas de verdad de terreno (`ground_truth_fault_turn`)**:

1. **Arquetipo 0 — Control Sano a 280k Tokens (`4` sesiones, `ground_truth_fault_turn = None`):**
   Refactor progresivo coherente hasta `280,000` tokens donde todas las llamadas respetan firmas vivas, no se repiten parches fallidos y se mantiene el objetivo. Mide la **Tasa de Falsas Alarmas (`False Alarm Rate`)**.
2. **Arquetipo 1 — Regresión de Firma por *State Shadowing* a >250k (`4` sesiones):**
   Se define una API interna en los primeros `15k` tokens, se acumulan `235k` tokens de desarrollo y logs, se refactoriza la firma en `~210k` tokens, y pasados los `255k` tokens el asistente invoca la firma vieja del inicio.
3. **Arquetipo 2 — Bucle de *Agent Thrashing* a >250k (`4` sesiones):**
   En `~60k` tokens falla un parche (registrado como `accepted=False`), pasan `195k` tokens de intentos intermedios y logs, y a los `255k+` tokens el asistente vuelve a proponer el mismo parche fallido (con nombres de variables locales ligeramente cambiados o comentario distinto).
4. **Arquetipo 3 — Deriva Semántica de Objetivo (*Goal Drift*) a >250k (`4` sesiones):**
   Pasados los `240k` tokens, las respuestas del asistente abandonan gradualmente el módulo de ingeniería pedido en el turno 0 y derivan hacia temas/componentes inconexos.

Además, soportar en `session_simulator.py` una función `load_external_jsonl_sessions(dir_path: Path) -> list[SimulatedSession]` para que si el usuario pasa `--transcripts-dir /ruta/a/logs`, el runner audite también sesiones reales grabadas en `.jsonl`.

### Comparativa Obligatoria de 3 Detectores en `scripts/lab_v2/run_test_b.py`:
Evaluar sobre las `16` sesiones de `250k–300k` tokens:
- **`D1_RawCosineOnly`**: Solo alineación y similitud coseno cruda sin blanqueo ni índice AST.
- **`D2_WhitenedKinematicsOnly`**: Señales cinemáticas blanqueadas (`alpha_t`, `nu_t`, `rho_t`, `H_ctx`) sin `LiveSymbolIndex`.
- **`D3_FullGovernor_Kinematics_Plus_AST`**: Señales cinemáticas blanqueadas + `LiveSymbolIndex` + `ContextCompiler`.

Medir y exportar sin redondeos en `reports/lab_v2_test_b_results.json` y en `reports/test_b_context_rot_250k.md`:
1. `fault_detection_recall` (fracción de sesiones defectuosas detectadas en el turno exacto del fallo o antes),
2. `healthy_session_false_alarm_rate` (fracción de sesiones sanas de 280k tokens con falsas alertas),
3. `f1_score` de detección por arquetipo (`shadowing`, `thrashing`, `goal_drift`),
4. Métricas del `ContextCompiler` sobre las 16 sesiones de `>250k` tokens:
   - `mean_original_tokens`, `mean_compiled_tokens`, `mean_token_savings_ratio`,
   - `invariant_retention_rate` (debe ser `1.0`),
   - `live_signature_retention_rate` (debe ser `1.0`),
   - `obsolete_code_pruning_rate`,
   - `mean_compile_latency_ms` y `mean_turn_audit_latency_ms`.
5. Veredicto dinámico `determine_test_b_verdict(...)` calculado con booleanos reales y testeado contra hardcodeo en `tests/lab_v2/test_b4_session_benchmark.py`. *(En `pytest`, usar escala reducida `target_tokens=15000` + `FakeEmbedder` para que los tests corran en `< 5 s`; en `run_test_b.py` usar el tamaño completo `target_tokens=265000` + `BAAI/bge-m3`).*

**Comandos finales de verificación y ejecución real del Slice 4:**
```bash
uv run pytest && uv run ruff check ddi_fw/lab_v2 scripts/lab_v2 tests/lab_v2
uv run python scripts/lab_v2/run_test_b.py --embedder bge
```


# 03 — Protocolo de Prueba Viva A/B contra Gemini API (`TASK-004`)
## Evaluación Ejecutable `Pass@1` en Sesiones de `~265k` Tokens Crudos vs. `< 36k` Compilados por DDI

**ID de Tarea:** `TASK-004`  
**Estado de Compuerta Humana:** `AUTORIZADA POR EL USUARIO` (Proveedor: Google Gemini API via `.env`, tope duro `20` llamadas exitosas / `3,500,000` input tokens)  
**Prerrequisitos:** `TASK-001` (`DONE`), `TASK-002` (`DONE`) y `TASK-003` (`DONE`)  
**Paquete objetivo:** `ddi_fw/lab_v2/`, `scripts/lab_v2/`, `tests/lab_v2/` (prohibido tocar `ddi_fw/*.py` legacy o `tests/test_*.py`)

---

## 1. Reglas de Seguridad Presupuestaria y Científica (Innegociables)

> [!CAUTION]
> **FRENOS DUROS DE COSTO (`BudgetGuard` en código):**
> 1. `MAX_SUCCESSFUL_CALLS = 20` (exactamente `10` escenarios × `2` brazos: `Brazo A = ~265k crudo`, `Brazo B = <36k compilado por DDI`). Cualquier intento de emitir la llamada exitosa `#21` debe lanzar `RuntimeError("HARD_BUDGET_EXCEEDED")` **antes** de tocar la red.
> 2. `MAX_TOTAL_HTTP_ATTEMPTS = 35` (techo absoluto contando eventuales `HTTP 429` o `503` para hacer matemáticamente imposible un bucle infinito de reintentos).
> 3. `MAX_TOTAL_INPUT_TOKENS = 3_500_000`. Antes de cada request, verificar que `accumulated_input_tokens + estimated_prompt_tokens <= 3_500_000`; si lo supera, lanzar `RuntimeError("HARD_BUDGET_EXCEEDED")` sin hacer request.
> 4. **Cero exposición de credenciales:** Leer la clave en orden `DDI_LIVE_API_KEY` → `GEMINI_API_KEY` → `GOOGLE_API_KEY` desde entorno o `.env` en la raíz del repo. Jamás imprimir, loguear ni serializar la API key en excepciones, consola o artefactos. Si no existe ninguna de las tres variables al correr en modo `live`, pasar `TASKS.md` a `status: "BLOCKED"`, notificar con `agent.sh notify` y detenerse sin inventar datos.

> [!IMPORTANT]
> **REGLA DE EQUIDAD CIENTÍFICA (CERO TRAMPAS A FAVOR DE DDI):**
> 1. El último turno `user` (`turns[-1]`, la consigna de programación a resolver) debe ser **100% idéntico carácter por carácter** en el Brazo A (`Raw 265k`) y en el Brazo B (`DDI Compiled <36k`).
> 2. El Brazo B se obtiene **únicamente** invocando `compile_session_context` + `LiveSymbolIndex` + `NegativeMemoryNote` a partir del historial de turnos de la sesión (`max_budget_tokens=36000`, `fresh_tail_turns=4`). **PROHIBIDO** inyectar pistas manuales ad-hoc en el Brazo B que no salgan algorítmicamente del compilador de contexto.
> 3. El veredicto del reporte debe salir de una función pura `determine_test_c_verdict(...)` testeada unitariamente tanto cuando gana DDI como cuando gana o empata el contexto crudo.

---

## 2. Especificación Exacta por Vertical Slices

### Slice 1 — Higiene de Turnos Rechazados en `context_compiler.py` y Cliente Gemini con `BudgetGuard` (`ddi_fw/lab_v2/live_ab_harness.py` + `tests/lab_v2/test_c1_live_ab_harness.py`)

1. **Extensión retrocompatible en `ddi_fw/lab_v2/context_compiler.py`:**
   - Agregar el parámetro keyword-only opcional `rejected_turn_indices: set[int] | None = None` en `compile_session_context(...)`.
   - Cuando `rejected_turn_indices` no sea `None` ni vacío:
     - `_last_definition_index(messages, rejected_turn_indices)` debe **ignorar** cualquier definición de función/clase ubicada en un turno `index in rejected_turn_indices`, de modo que un parche rechazado en un turno tardío jamás entierre como "obsoleta" a una definición aceptada previa.
     - En `_hygiene(...)`, si `message_index in rejected_turn_indices`, todo bloque ```` ```python ... ``` ```` en ese mensaje debe reemplazarse por `"[DDI-TOMBSTONE: parche rechazado en revisión previa; ver Memoria Negativa]"` e incrementar `pruned_blocks`.
   - Verificar que `tests/lab_v2/test_b3_context_compiler.py` siga 100% en verde sin modificar sus tests existentes.

2. **Crear `ddi_fw/lab_v2/live_ab_harness.py`:**
   - **Configuración `.env` / entorno (`load_live_config`):**
     - Buscar archivo `.env` en la raíz del repo (parseo simple línea por línea `KEY=VALUE` ignorando comentarios `#` y comillas envolventes, sin pisar variables ya presentes en `os.environ`).
     - Resolver `api_key` buscando `DDI_LIVE_API_KEY`, luego `GEMINI_API_KEY`, luego `GOOGLE_API_KEY`.
     - Resolver `model` desde `DDI_LIVE_MODEL` con default `"gemini-2.5-flash"`.
   - **`BudgetGuard`:**
     - Lleva contadores `successful_calls`, `http_attempts`, `accumulated_input_tokens`.
     - Método `check_before_call(estimated_tokens: int) -> None`: lanza `RuntimeError("HARD_BUDGET_EXCEEDED")` si `successful_calls >= max_successful_calls` (`20`), o `http_attempts >= max_total_http_attempts` (`35`), o `accumulated_input_tokens + estimated_tokens > max_input_tokens` (`3_500_000`).
   - **Serializador REST nativo de Gemini (`messages_to_gemini_payload(messages, model)`):**
     - Extrae todos los mensajes con `role == "system"` en su orden de aparición y los concatena con `"\n\n"` dentro de `systemInstruction: {"parts": [{"text": system_joined}]}`.
     - Convierte el resto de mensajes mapeando `"user" -> "user"` y `"assistant" -> "model"`, **fusionando mensajes consecutivos del mismo rol** con `"\n\n"` para cumplir estrictamente la alternancia `user` / `model` exigida por `:generateContent`.
     - Si el primer mensaje de `contents` queda con rol `"model"`, anteponer `{"role": "user", "parts": [{"text": "[Inicio de registro de sesión]"}]}`. Verificar que el último elemento de `contents` tenga rol `"user"`.
     - `generationConfig`:
       ```python
       gen_cfg: dict[str, object] = {
           "temperature": 0.0,
           "maxOutputTokens": 2048,
       }
       if "flash" in model.lower():
           gen_cfg["thinkingConfig"] = {"thinkingBudget": 0}
       ```
       *(Desactivar `thinkingBudget` en modelos `flash` evita que el modelo agote `maxOutputTokens` pensando en silencio y garantiza comparación determinista limpia en ambos brazos).*
   - **Cliente sincrónico `GeminiLiveClient` sobre `httpx.Client`:**
     - URL: `f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"`, header `"x-goog-api-key": api_key`, `timeout=180.0`, aceptando `transport: httpx.BaseTransport | None = None`, `sleep_fn: Callable[[float], None] = time.sleep` y `heavy_call_pacing_s: float = 18.0`.
     - **Control de cuota TPM (`Tokens Per Minute`):** Si la llamada inmediata anterior tuvo `>= 100_000` input tokens y la llamada actual estima `>= 100_000` tokens ( o siempre después de una llamada `>= 100_000` tokens), invocar `sleep_fn(heavy_call_pacing_s)` para espaciar los `10` envíos de `265k` tokens sin saturar ventanas de `1M TPM`.
     - **Manejo de errores:**
       - `HTTP 429` o `HTTP 503`: permitir hasta `2` reintentos para esa llamada esperando `[35.0, 65.0]` segundos con `sleep_fn`, incrementando `http_attempts` en cada intento (sin sumar `successful_calls` ni `accumulated_input_tokens` en el intento fallido).
       - `HTTP 400`, `401`, `403` u otro error no recuperable: lanzar `RuntimeError` descriptivo con el status code y el mensaje de error sanitizado (jamás incluir headers ni la API key).
     - En `HTTP 200`, extraer el texto concatenado de `candidates[0].content.parts[*].text`, leer `usageMetadata.promptTokenCount` y `candidatesTokenCount` (usando `estimated_tokens` como fallback solo si `usageMetadata` no viniera), medir latencia con `time.perf_counter()` en milisegundos, incrementar `successful_calls += 1` y actualizar `accumulated_input_tokens`.

3. **Tests unitarios (`tests/lab_v2/test_c1_live_ab_harness.py`, `< 1s`, `httpx.MockTransport`):**
   - Test de tope `#21`: ejecuta 20 llamadas mock exitosas y comprueba que la `#21` lanza `RuntimeError("HARD_BUDGET_EXCEEDED")` con exactamente `20` requests recibidos por el transporte mock.
   - Test de tope de tokens (`3_500_000`): comprueba bloqueo previo al request cuando se excede el presupuesto de tokens.
   - Test de `messages_to_gemini_payload`: verifica extracción de múltiples `system` (incluido `[DDI-CONTEXT-GOVERNOR]`) a `systemInstruction`, fusión de turnos consecutivos del mismo rol sin dos `"user"` o `"model"` adyacentes, preservación exacta del turno final `"user"` y presencia de `thinkingBudget: 0` en `gemini-2.5-flash`.
   - Test de `HTTP 429` → `HTTP 200` con `sleep_fn` capturado en lista (sin dormir en tiempo real).
   - Test de `compile_session_context(..., rejected_turn_indices={...})`: verifica que un turno rechazado tardío se convierte en `[DDI-TOMBSTONE: parche rechazado...]` y NO entierra la definición aceptada previa.

---

### Slice 2 — 10 Escenarios Multi-Refactor de `~265k` Tokens y Oráculo Ejecutable (`ddi_fw/lab_v2/live_ab_scenarios.py` + `tests/lab_v2/test_c2_live_ab_scenarios.py`)

1. **Crear `ddi_fw/lab_v2/live_ab_scenarios.py`:**
   - Construir una función determinista `build_live_ab_scenarios(target_tokens: int = 265_000) -> list[LiveAbScenario]` que devuelva **exactamente `10` escenarios de ingeniería en Python (`S01` a `S10`)**, cada uno con `96` turnos y entre `255_000` y `275_000` tokens estimados:
     - **`S01..S05` (familia `"multi_refactor_shadowing"`):**
       Cinco dominios técnicos distintos:
       1. `S01_ledger_settlement`: liquidación contable en centavos y basis points (`calcular_cargo_base`, `aplicar_retencion_escalonada`, `consolidar_asiento` → función objetivo `liquidar_lote_comercios`).
       2. `S02_infusion_dosing`: dosificación clínica pediátrica/renal (`ajustar_por_clearance`, `limitar_velocidad_bomba`, `redondear_ampollas` → función objetivo `planificar_infusion_segura`).
       3. `S03_orbital_window`: planificación de pases satelitales (`elevar_horizonte_mrad`, `penalizar_eclipse_ms`, `filtrar_ventana_util` → función objetivo `seleccionar_pase_prioritario`).
       4. `S04_contract_indexation`: actualización contractual con topes y mora (`indexar_capital_bps`, `calcular_mora_diaria_bps`, `aplicar_quita_tope` → función objetivo `liquidar_convenio_judicial`).
       5. `S05_coldchain_allocation`: asignación FEFO de cadena de frío (`descontar_merma_termica`, `priorizar_lotes_fefo`, `calcular_reserva_critica` → función objetivo `despachar_pedido_hospitalario`).
       - En cada escenario `S01..S05`:
         - `turn 0` (`system`) y `turn 1` (`user`) fijan **invariantes numéricos estrictos** (aritmética entera exacta `//`, claves exactas del `dict` de retorno y `ValueError` ante entradas negativas o vacías).
         - Las `3` funciones auxiliares evolucionan por **`4` versiones (`v1` en turno 4, `v2` en turno 24, `v3` en turno 52, `v4` definitiva en turno 78)** cambiando aridad, orden y argumentos *keyword-only* (ej. `v1(monto, tasa)` → `v2(monto_centavos, tasa_bps)` → `v3(monto_centavos, tasa_bps, tope_centavos)` → `v4(monto_centavos, *, tasa_bps, minimo_centavos, moneda)`).
         - Los turnos intermedios de relleno (`~2,750` tokens por turno) mezclan discusiones de arquitectura, trazas `Traceback` sobre `v1/v2/v3`, snippets de llamadas viejas y logs de tests de módulos vecinos para recrear la interferencia real de una sesión larga de `265k` tokens.
     - **`S06..S10` (familia `"rejected_patch_thrashing"`):**
       Cinco dominios técnicos distintos:
       6. `S06_token_bucket`: limitador de tasa determinista (`recargar_cubeta_entera`, `consumir_rafaga` → objetivo `evaluar_lote_peticiones`).
       7. `S07_audit_chain`: encadenamiento hash determinista sin floats (`normalizar_evento_canonico`, `mezclar_acumulador_fnv` → objetivo `verificar_cadena_auditoria`).
       8. `S08_fx_netting`: compensación multimoneda con comisión asimétrica (`convertir_a_base_bps`, `compensar_saldos_par` → objetivo `liquidar_posicion_neta`).
       9. `S09_triage_queue`: cola clínica determinista con desempate estable (`puntaje_severidad_vital`, `escalar_por_espera_min` → objetivo `ordenar_guardia_prioritaria`).
       10. `S10_retry_planner`: planificador de backoff acotado con presupuesto (`calcular_demora_cuadratica_ms`, `recortar_a_ventana_sla` → objetivo `planificar_reintentos_lote`).
       - En cada escenario `S06..S10`:
         - `turn 0` (`system`) y `turn 1` (`user`) fijan invariantes estrictos (ej. no mutar listas de entrada, deduplicar por ID conservando la primera aparición, aritmética entera sin `float`/`round`, respetar firmas auxiliares aceptadas en `turns 2..8`).
         - En `turns 20, 38, 56` (`accepted=False`, con `rejection_reason` explícita y turno `user` inmediato de rechazo en code review) aparecen **3 implementaciones tentadoras pero rechazadas** (por usar `float`, mutar el input, duplicar IDs o llamar helpers con argumentos erróneos), seguidas de más de `150,000` tokens de trabajo posterior.
   - **Turno final `turns[-1]` (`role="user"`, idéntico en Brazo A y Brazo B):**
     Pide implementar **únicamente** en un bloque ```` ```python ```` la función objetivo `<target_fn>` con su firma exacta de entrada, invocando las funciones auxiliares vigentes del módulo (asumiéndolas ya definidas en el scope global, prohibiendo redefinirlas) y cumpliendo todos los invariantes de la sesión.
   - **Función compiladora limpia `compile_scenario_for_ddi(scenario) -> CompiledContextResult`:**
     Construye `LiveSymbolIndex` ingiriendo **solo** los bloques Python de turnos con `turn.accepted is True`, construye `negative_memory: list[NegativeMemoryNote]` con los turnos `turn.accepted is False`, pasa `rejected_turn_indices={t.turn_id for t in scenario.turns if not t.accepted}`, `max_budget_tokens=36000`, `fresh_tail_turns=4`, y devuelve el `CompiledContextResult`.
   - **Oráculo ejecutable seguro `verify_scenario_code(scenario, generated_text) -> ScenarioEvalResult`:**
     - Extrae el bloque Python de `generated_text`.
     - Verifica `ast.parse` (`syntax_ok`) y aplica guardia AST que rechaza cualquier import fuera de `{"math", "typing", "dataclasses", "collections", "decimal", "fractions"}` y cualquier llamada a `open`, `exec`, `eval`, `__import__`, `compile`, `breakpoint`.
     - Verifica que el candidato defina `scenario.target_fn_name`, que **no redefina** las funciones auxiliares del módulo y que `symbol_index.find_deprecated_calls(code)` sea vacío (`ast_signature_ok`).
     - Ejecuta en un dict `ns` aislado `scenario.live_helpers_code + "\n\n" + code` y corre las `>= 5` aserciones deterministas de `scenario.check_fn(ns[scenario.target_fn_name])`, registrando `passed: bool` y `failure_reason: str | None`.

2. **Tests unitarios (`tests/lab_v2/test_c2_live_ab_scenarios.py`, `< 2s`, sin red):**
   - Verifica que `build_live_ab_scenarios()` genera `10` escenarios (`5` `multi_refactor_shadowing` + `5` `rejected_patch_thrashing`), cada uno con `255_000 <= raw_tokens <= 275_000`.
   - Verifica que `compile_scenario_for_ddi(s)` reduce los `10` escenarios a `<= 36_000` tokens, mantiene `compiled.messages[-1]["content"] == s.messages[-1]["content"]` (igualdad exacta del prompt final) e incluye las firmas `v4` vigentes en `[DDI-CONTEXT-GOVERNOR]`.
   - Verifica para los **10 escenarios** que:
     1. `verify_scenario_code(s, s.reference_solution).passed is True`,
     2. `verify_scenario_code(s, s.broken_deprecated_call_solution).passed is False` (y detecta violación de firma/ejecución),
     3. `verify_scenario_code(s, s.broken_invariant_solution).passed is False`.

---

### Slice 3 — Runner A/B (`mock` + `live`), Veredicto Dinámico y Corrida Viva contra Gemini (`scripts/lab_v2/run_test_c_live_ab.py` + `tests/lab_v2/test_c3_live_ab_runner.py`)

1. **Crear `scripts/lab_v2/run_test_c_live_ab.py`:**
   - CLI con `--mode {live,mock}` (default `live`), `--json-out reports/lab_v2_test_c_live_ab.json` y `--md-out reports/test_c_ab_live_api.md`.
   - Para cada uno de los `10` escenarios `S01..S10`:
     1. **Brazo A (`raw_265k`):** Envía `scenario.messages` (`~265k` tokens) a `GeminiLiveClient`, evalúa la respuesta con `verify_scenario_code`.
     2. **Brazo B (`ddi_compiled`):** Compila con `compile_scenario_for_ddi(scenario)` (`<36k` tokens), envía `compiled.messages` a `GeminiLiveClient`, evalúa la respuesta con la **misma** función `verify_scenario_code`.
   - Calcular métricas sin redondear (`.agents/rules/cero-redondeos.md`):
     - `pass_at_1_raw_265k`, `pass_at_1_ddi_compiled`, `pass_at_1_gain`
     - `shadowing_pass_at_1_raw`, `shadowing_pass_at_1_ddi`
     - `thrashing_pass_at_1_raw`, `thrashing_pass_at_1_ddi`
     - `ast_signature_ok_rate_raw`, `ast_signature_ok_rate_ddi`
     - `paired_outcomes`: `{"ddi_wins": int, "raw_wins": int, "both_pass": int, "both_fail": int}`
     - `total_prompt_tokens_raw`, `total_prompt_tokens_ddi`, `real_input_token_savings_ratio`
     - `total_output_tokens_raw`, `total_output_tokens_ddi`
     - `latency_ms_p50_raw`, `latency_ms_p95_raw`, `latency_ms_p50_ddi`, `latency_ms_p95_ddi`, `latency_speedup_p50`
     - Tabla detalle escenario por escenario (`S01..S10`) con tokens facturados, latencia, `syntax_ok`, `ast_signature_ok`, `passed` y `failure_reason` de ambos brazos.
   - Implementar función pura `determine_test_c_verdict(summary: dict[str, object]) -> dict[str, object]` (sin hardcodear ganadores):
     - `accuracy_winner`: `"DDI_Compiled"` si `pass_at_1_ddi_compiled > pass_at_1_raw_265k`, `"Raw_265k"` si es menor, `"Tie"` si empatan.
     - `ddi_improves_or_preserves_pass_at_1`: `bool(pass_at_1_ddi_compiled >= pass_at_1_raw_265k)`
     - `ddi_strictly_beats_raw_pass_at_1`: `bool(pass_at_1_ddi_compiled > pass_at_1_raw_265k)`
     - `token_savings_exceeds_80pct`: `bool(real_input_token_savings_ratio >= 0.80)`
   - Renderizar `reports/test_c_ab_live_api.md` usando raw strings (`r"""..."""`) para cualquier expresión LaTeX y `format(x, ".17g")` para floats.

2. **Tests unitarios (`tests/lab_v2/test_c3_live_ab_runner.py`, `< 2s`, sin red):**
   - Prueba `determine_test_c_verdict` en las tres direcciones (`DDI_Compiled` gana, `Raw_265k` gana y `Tie`).
   - Ejecuta `run_test_c_live_ab(mode="mock", ...)` sobre `tmp_path`, comprobando que realiza exactamente `20` llamadas mock, respeta `.agents/rules/cero-redondeos.md` (cero `round(` o `:.2f`), no inyecta `\x0b`/`\t` en LaTeX y serializa JSON/Markdown válidos.

3. **Corrida Viva Real (`--mode live`) con Gemini API:**
   - Correr `uv run pytest` y `uv run ruff check ddi_fw/lab_v2 scripts/lab_v2 tests/lab_v2`.
   - Ejecutar **una sola vez** la corrida viva real:
     ```bash
     uv run python scripts/lab_v2/run_test_c_live_ab.py --mode live
     ```
   - Verificar que `reports/lab_v2_test_c_live_ab.json` tenga `"mode": "live"`, `"successful_api_calls": 20` y los conteos reales de `promptTokenCount` devueltos por Google Gemini.

# 05 — Protocolo Camino 1 (`TASK-005`): Pinning de Código Vivo en `ContextCompiler` y Revancha Limpia Test C (`Gemini Live`)

**ID de Tarea:** `TASK-005`  
**Estado de Compuerta Humana:** `AUTORIZADA POR EL USUARIO` (1 única corrida viva de `20` llamadas exitosas / tope duro `3,500,000` input tokens)  
**Prerrequisitos:** `TASK-001`..`TASK-004` (`DONE`)  
**Paquete objetivo:** `ddi_fw/lab_v2/`, `scripts/lab_v2/`, `tests/lab_v2/` (prohibido tocar `ddi_fw/*.py` legacy o `tests/test_*.py`)

---

## 1. Diagnóstico de Auditoría sobre `TASK-004` (Qué Corregimos y Por Qué)

La corrida viva de `TASK-004` contra `gemini-3.8-flash` demostró **88.96% de ahorro real en tokens facturados** (`2,146,589 → 236,994`) y **1.43x de mejora en latencia**, pero destapó **dos defectos técnicos** que causaron `both_fail = 8`:

1. **Defecto Real del Motor (`ddi_fw/lab_v2/context_compiler.py` + `ast_symbol_index.py`):**
   - En `compile_session_context`, los turnos intermedios que contienen las **definiciones Python vigentes (`last_def.values()`)** competían por presupuesto contra turnos largos de logs/discusión (`4,500` tokens) usando similitud léxica. En `S08` y `S09`, los turnos de relleno desplazaron y **expulsaron los turnos `2` y `4` donde estaban definidas las funciones auxiliares vivas**.
   - Además, `LiveSymbolIndex` no guardaba el encabezado tipado (`def fn(x: int, *, y: str) -> int`), por lo que al perderse el turno de definición también se perdían los *type hints*.
2. **Defecto de Equidad y Especificación en `ddi_fw/lab_v2/live_ab_scenarios.py`:**
   - **Contratos ocultos imposibles de adivinar:** `_objective_prompt` nunca informó el esquema de las tuplas de entrada (`list[tuple[str, int]]`, `list[tuple[str, int, int, int]]`), ni el tipo exacto de cada clave del `dict` de salida (`tuple` vs `list`, `int` conteo vs colección), ni constantes mágicas del oráculo (`haber=base // 4` en `S08`, o encadenar la retención sobre el cargo en vez del monto bruto en `S01..S05`). Por eso ambos brazos fallaron con `TypeError` / `AttributeError` / `AssertionError`.
   - **Spoiler en `Turn 0` y relleno artificial en un solo turno:** `_system_text` copió `final_prompt` (con la firma final) dentro del turno `0` (`systemInstruction`), y `_token_goals` concentró `~246,000` tokens de `"x" * ...` en el turno `60` en lugar de distribuir código/discusión realista entre los turnos intermedios e incluir los nombres `v4` únicamente en el refactor aceptado del turno `74`.

> [!IMPORTANT]
> **Invariante de Equidad Científica:**
> - En el **Brazo A (`raw_265k`)** está el 100% de la información necesaria para resolver los `10` escenarios (`10/10` posibles si el modelo no sufre interferencia de versiones obsoletas ni olvido a `265k` tokens).
> - En el **Brazo B (`ddi_compiled`)**, el turno final `turns[-1]` es **100% idéntico carácter por carácter** al del Brazo A, y la reducción de contexto ocurre **exclusivamente** mediante el algoritmo general `compile_session_context` (sin inyectar pistas manuales ad-hoc).

---

## 2. Especificación Exacta por Vertical Slices

### Slice 1 — Pinning de Definiciones AST Vivas y Encabezados Tipados (`ast_symbol_index.py` + `context_compiler.py` + tests)

1. En `ddi_fw/lab_v2/ast_symbol_index.py`:
   - Añadir el campo opcional con default retrocompatible `typed_signature: str = ""` a `FunctionSig`.
   - En `_store_function`, construir `typed_signature` usando `ast.unparse` sobre los argumentos (`node.args`) y la anotación de retorno (`f" -> {ast.unparse(node.returns)}"` si `node.returns` no es `None`), generando por ejemplo:
     `"liquidar_orden(centavos: int, bps_impuesto: int, moneda: str) -> int"`.
   - **Mantener intacto `render_signature(sig)`** (sin tipos) para preservar 100% de compatibilidad con `test_b1_ast_symbol_index.py`, `test_b3_context_compiler.py` y `test_b4_session_benchmark.py`. Agregar el método `render_typed_signature(self, sig: FunctionSig) -> str` que devuelva `sig.typed_signature or self.render_signature(sig)`.
2. En `ddi_fw/lab_v2/context_compiler.py`:
   - En `_governor_text(index, notes)`, mantener intactas las secciones `"Firmas vivas:"`, `"Firmas deprecadas prohibidas:"` y `"Memoria negativa reciente:"`, y agregar al final una subsección `"Encabezados tipados vigentes:"` listando `- {index.render_typed_signature(index.live_signatures[qualname])}` para cada símbolo vivo.
   - **Pinning obligatorio de definiciones AST vigentes en `compile_session_context`:**
     - Sea `live_def_turn_ids = set(last_def.values())`.
     - Todo mensaje de `hygienic` cuyo `index_in_source` pertenezca a `live_def_turn_ids` es **código vivo vigente del módulo** y debe separarse en una lista `pinned_live: list[tuple[int, dict[str, str]]]` **antes** del ranking por similitud de los turnos conversacionales/logs restantes (`candidates`).
     - Sumar el costo de `pinned_live` a `used` junto con `head`, `governor` y `tail` (si un turno `pinned_live` individual excediera por sí solo el presupuesto restante, conservar únicamente sus bloques ```` ```python ... ``` ```` vigentes para que jamás supere `max_budget_tokens`), y luego llenar el presupuesto sobrante con `candidates` ordenados por `ranked`.
     - Al ensamblar `compiled`, fusionar y ordenar `pinned_live + selected` por `source_index` creciente para preservar el orden cronológico exacto.
3. En `tests/lab_v2/test_b3_context_compiler.py` (o `tests/lab_v2/test_c1_live_ab_harness.py`):
   - Agregar un test unitario `test_live_definitions_are_pinned_against_high_similarity_filler` donde los turnos `2` y `4` definen funciones vivas cortas con type hints y existen `30` turnos posteriores de `4,000` tokens repletos de palabras de la consulta final: comprobar que `compile_session_context(..., max_budget_tokens=28000)` **conserva íntegros los bloques `def` de los turnos `2` y `4`** y expone `-> int` en `"Encabezados tipados vigentes:"`.

---

### Slice 2 — Rediseño Limpio y Equitativo de los 10 Escenarios de `~265k` Tokens (`ddi_fw/lab_v2/live_ab_scenarios.py` + `tests/lab_v2/test_c2_live_ab_scenarios.py`)

1. **Eliminar el spoiler en `Turn 0` (`_system_text`) y en `Turn 1` (`_user_contract`):**
   - `Turn 0` (`system`) y `Turn 1` (`user`) deben establecer únicamente el dominio del módulo, los invariantes generales (aritmética entera exacta `//`, cero `float`, no mutar colecciones de entrada, deduplicación por ID conservando la primera aparición, validación `ValueError`) y el nombre de la función integradora final, **SIN revelar los nombres de parámetros keyword-only `v4` que recién aparecerán tras las refactorizaciones**.
2. **Eliminar el bloque artificial de `"x" * ...` en un solo turno (`_token_goals` / `_text_with_tokens`):**
   - Prohibido rellenar con `"x" * ...` ni concentrar `>200k` tokens en un único turno.
   - Distribuir el presupuesto de `~265,000` tokens de manera uniforme entre los `~82` turnos intermedios de trabajo (`~3,000` a `3,400` tokens por turno) usando prosa técnica variada, logs de ejecución y fragmentos/llamadas de discusión realistas:
     - En **`S01..S05` (`multi_refactor_shadowing`):**
       - `Turn 4`: define auxiliares `v1` (2 argumentos posicionales). Los turnos `5..21` incluyen múltiples ejemplos de llamadas y trazas usando `v1`.
       - `Turn 22`: refactoriza auxiliares a `v2` (cambia nombres y pasa a basis-points/unidades enteras, posicionales). Los turnos `23..47` incluyen múltiples llamadas y discusiones usando `v2`.
       - `Turn 48`: refactoriza auxiliares a `v3` (3 argumentos posicionales). Los turnos `49..73` incluyen múltiples llamadas usando `v3`.
       - `Turn 74` (`accepted=True`): refactorización definitiva `v4` con **anotaciones de tipos completas** y argumentos **keyword-only** específicos de `v4` (distintos de los nombres de parámetros de `target_fn` para que el modelo NO pueda adivinar los kwargs de `v4` leyendo solo `target_fn`, sino que deba leer la definición `v4` del turno `74` o el gobernador AST!). Los turnos `75..94` (~`60,000` tokens posteriores) discuten telemetría y módulos adyacentes sin repetir la definición `v4`.
     - En **`S06..S10` (`rejected_patch_thrashing`):**
       - `Turn 2` y `Turn 4` (`accepted=True`): definen las `2` funciones auxiliares vigentes con anotaciones de tipos completas (`: int`, `: str`, `-> int`).
       - `Turns 18, 36, 54` (`accepted=False`, seguidos en `19, 37, 55` por el rechazo explícito en *code review*): muestran `3` implementaciones defectuosas tentadoras de `target_fn` rechazadas específicamente por: (a) usar `float`/`/` en vez de `//`, (b) olvidar validar enteros negativos *dentro* de cada tupla de la lista de entrada (`item_val < 0`), y (c) mutar la lista de entrada o no deduplicar IDs repetidos. Los turnos `56..94` suman `>150,000` tokens posteriores distribuidos.
3. **Especificación 100% completa y sin ambigüedad en `Turn 95` (`_objective_prompt`, idéntico en Brazo A y Brazo B):**
   - Para cada uno de los `10` escenarios (`S01..S10`), `turns[-1]` debe especificar con total claridad ingenieril (pero **sin** soplar los nombres de los argumentos keyword-only internos de las auxiliares `v4`, diciendo únicamente *"invocando las funciones auxiliares `<h1, h2, ...>` con su última firma aceptada vigente en la sesión"*):
     1. **Firma tipada exacta** de `target_fn` (ej. `def liquidar_lote_comercios(lote: list[tuple[str, int]], *, tasa_bps: int, minimo_centavos: int, tramo_bps: int, tope_retencion: int, moneda: str) -> dict[str, object]:`).
     2. **Estructura exacta de cada tupla de entrada** (ej. *"cada elemento de `lote` es una tupla `(comercio_id: str, monto_centavos: int)`"*).
     3. **Regla exacta de validación `ValueError`**: lanzar `ValueError` si la lista de entrada está vacía, si cualquier `str` requerido (el identificador en cada tupla o el parámetro `str` como `moneda`/`canal`/`sala`/`via`/`estacion`/`expediente`/`deposito`) está vacío, o si cualquier parámetro `int` o campo numérico dentro de cada tupla es `< 0` (y `primo < 2` en `S07`).
     4. **Regla exacta de deduplicación y flujo paso a paso** (sin ninguna constante mágica oculta: ej. en `S01..S05`, explicitar *"1) deduplicar `items` por el primer elemento `id_str` conservando solo la primera aparición; 2) para cada ítem único, calcular primero `left = <floor_fn>(...)` sobre su valor entero, luego calcular `right = <cap_fn>(...)` pasando `left` como primer argumento, y finalmente calcular `net = <diff_fn>(...)` sobre las listas acumuladas `produced` y `withheld`"* — actualizar también `shadow_expected` y `reference` en `S01..S05` para que deduplicar por `item[0]` sea consistente en los 10 escenarios; y en `S08`, explicitar que `haber = base // 4`, en `S07` el valor inicial FNV `2166136261 % 4294967311`, en `S09` el desempate `(-score, -espera, indice_original)`).
     5. **Esquema y tipos exactos del `dict` de retorno** para cada clave (especificando explícitamente cuándo el valor es `int`, `str` o `tuple[...]`, p.ej. `"orden": tuple[str, ...] con los IDs ordenados`, `"pacientes": int cantidad de pacientes únicos`, `"pasos": tuple[tuple[str, int], ...]`).
4. En `tests/lab_v2/test_c2_live_ab_scenarios.py`:
   - Verificar que:
     - Ningún turno tiene relleno `"xxxx"`.
     - `Turn 0`, `Turn 1` y `Turn 95` en `S01..S05` **NO contienen** los nombres de los argumentos keyword-only exclusivos de `v4` (probando que el modelo solo puede conocerlos desde el historial en `Turn 74` o desde `[DDI-CONTEXT-GOVERNOR]`).
     - En los `10` escenarios compilados por DDI, tanto `[DDI-CONTEXT-GOVERNOR]` (con `"Encabezados tipados vigentes:"`) como el bloque `def` vivo aceptado están presentes dentro de `compiled.messages`, y `compiled.compiled_tokens <= 36_000`.
     - `reference_solution` pasa (`True`), `broken_deprecated_call_solution` falla (`False`) y `broken_invariant_solution` falla (`False`) en los `10` escenarios.

---

### Slice 3 — Registro de Incidente, Suite Global y Única Corrida Viva Limpia (`TASK-005`)

1. Agregar 1 línea JSONL válida en `logs/incident_markers.jsonl` documentando los 2 hallazgos corregidos tras la auditoría de `TASK-004` (pinning de `last_def` en `context_compiler.py` y eliminación de contratos ambiguos / spoiler de `Turn 0` en `live_ab_scenarios.py`).
2. Correr `uv run pytest` y `uv run ruff check ddi_fw/lab_v2 scripts/lab_v2 tests/lab_v2` verificando 100% en verde.
3. Ejecutar **UNA SOLA VEZ** la corrida viva contra Gemini API (`MAX_SUCCESSFUL_CALLS = 20`, `MAX_TOTAL_INPUT_TOKENS = 3_500_000`):
   ```bash
   uv run python scripts/lab_v2/run_test_c_live_ab.py --mode live
   ```
   *(Actualizar `"task_id": "TASK-005"` en el payload de `run_test_c_live_ab.py` manteniendo intactos todos los tests).*
4. Verificar `reports/lab_v2_test_c_live_ab.json` y `reports/test_c_ab_live_api.md`, volver a correr `uv run pytest` + `ruff`, pasar `TASKS.md` a `status: "DONE"` y disparar `agent.sh notify`.


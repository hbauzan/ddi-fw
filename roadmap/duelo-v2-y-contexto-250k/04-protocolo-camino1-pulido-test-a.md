# 04 — Protocolo Camino 1 (`TASK-003`): Pulido Quirúrgico de Test A
## Higiene de Vocabulario en `neg_piggybacking` y Compuerta Sintáctica de Código Ajeno en `M4`

**ID de Tarea:** `TASK-003`  
**Prerrequisitos completados:** `TASK-001` (`DONE`) y `TASK-002` (`DONE`)  
**Paquete objetivo:** `ddi_fw/lab_v2/` (aislado; prohibido tocar `ddi_fw/*.py` legacy o `tests/test_*.py`)

---

## 1. Diagnóstico de Auditoría sobre `TASK-001` (Por Qué Existe Esta Tarea)

La auditoría post-ejecución sobre `TASK-001` confirmó que `M3_EEB_Pure` ya supera ampliamente a `M2_Cosine` (`ROC-AUC 0.9109 vs 0.8714`, `FAR@5%FRR 25.0% vs 41.3%`, `FAR_unseen_OOD 0.0% vs 6.0%`, `FRR_business_python 11.1% vs 27.8%`), pero detectó **dos defectos de implementación** en el arnés de datos y en la heurística sintáctica de `M4` que distorsionaron dos subcategorías de ataque:

1. **Defecto 1 — Contaminación con meta-vocabulario Python en `_prose_payload` (`ddi_fw/lab_v2/corpus_builder.py:330-334`):**
   - El generador inyectó en las 90 muestras de `neg_piggybacking` la cadena:
     `f"{kind} {index:02d} sobre {sample_id}: esta prosa pertenece a un dominio vedado para el oficio python y tiene que auditarse fuera del bloque sintactico."`
   - Esa oración contiene literalmente `pos_stdlib_python::<modulo>::<funcion>`, `"oficio python"` y `"bloque sintactico"`. Al pasar por `BAAI/bge-m3`, el embedding resultante apunta hacia el centroide de Python por contaminación léxica artificial del propio benchmark (`far_piggybacking = 0.9556` en `M3`).
2. **Defecto 2 — Código ajeno sin cercas Markdown (`JS/SQL/Bash/Rust/C/Go`) cae en `prose_window` y penalización `+1.0` insuficiente (`ddi_fw/lab_v2/chunker.py:58`, `ddi_fw/lab_v2/models.py:316-321`):**
   - Los 60 snippets de `FOREIGN_SNIPPETS` vienen sin cercas ```` ``` ````. En `extract_chunks`, al no tener cercas ni ser Python ejecutable, caen en `_chunks_from_prose(..., kind="prose_window")` en vez de identificarse como código no-Python (`foreign_code`).
   - Además, en `M4_HybridAstSpectral._adjust`, la penalización `+1.0` sobre código no-Python es menor que el desplazamiento negativo (`~ -2.0`) que `bge-m3` asigna a cualquier lenguaje de programación frente a prosa natural (recetas/medicina/derecho), dejando el score por debajo de `q_hat` (`far_other_language = 1.0` y `far_piggybacking = 0.80`).

> [!IMPORTANT]
> **Invariante Científico Innegociable:**
> **PROHIBIDO** alterar las ecuaciones o el entrenamiento de `M1_DdiBoxesBaseline`, `M2_CosineMargin` o `M3_WhitenedSpectralSubspace`. `M2` y `M3` deben seguir siendo evaluadores **100% geométricos sobre embeddings puros** (sin pistas léxicas ni sintácticas), mientras que `M4_HybridAstSpectral` mide el poder real del firewall híbrido (`AST Python + Detector determinista de código ajeno + Subespacio Espectral Blanqueado`).

---

## 2. Especificación Exacta por Vertical Slices

### Slice 1 — Clasificación Estructural `foreign_code` en `ddi_fw/lab_v2/chunker.py` + `tests/lab_v2/test_a1_chunker.py`

1. En `ddi_fw/lab_v2/chunker.py`:
   - Extender el tipo literal:
     ```python
     ChunkKind = Literal["python_ast", "fenced_code", "foreign_code", "prose_window"]
     ```
   - Implementar una función pura determinista `_looks_like_non_python_code(text: str) -> bool` que **solo se evalúe cuando `_is_executable_python(text)` sea `False`**, detectando firmas sintácticas inequívocas de lenguajes de programación ajenos sin disparar falsos positivos en prosa natural (ES/EN/DE):
     - **Bash / Shell:** shebang `^#!\s*/(?:usr/bin/env\s+)?(?:ba|z|da|k)?sh\b` (multilínea), `^\s*set\s+-[euo]+`, o estructuras `(?s)\bcase\s+.+\bin\b.+\besac\b` / `(?s)\b(?:for|while)\b.+;\s*do\b.+\bdone\b`.
     - **SQL:** sentencias DDL/DML estructuradas: `(?is)^\s*(?:CREATE\s+(?:TABLE|VIEW|(?:UNIQUE\s+)?INDEX)|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|ALTER\s+TABLE|DROP\s+(?:TABLE|VIEW|INDEX))\b` o `SELECT ... FROM` que exija estructura SQL real (`\bSELECT\b[\s\S]+\bFROM\b` con `SELECT`/`FROM` en mayúsculas, o `(?is)^\s*select\b[\s\S]+\bfrom\b[\s\S]*(?:;\s*$|\b(?:where|group\s+by|order\s+by|having|join)\b)`), evitando falsos positivos en oraciones inglesas con *"select ... from"*.
     - **JavaScript / TypeScript:** `(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\(`, o combinación de declaraciones `\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=` con `;` o `=>` o llaves `{ ... }`.
     - **Rust:** `(?m)^\s*(?:pub\s+)?fn\s+[A-Za-z_]\w*\s*\([^)]*\)\s*(?:->\s*[^\{]+)?\{` o `(?m)^\s*(?:pub\s+)?struct\s+[A-Za-z_]\w*\s*\{`.
     - **C / C++:** `(?m)^\s*#include\s*[<"][^>"]+[>"]` o definición tipada con cuerpo entre llaves y punto y coma interno: `(?ms)^\s*(?:static\s+|inline\s+|unsigned\s+|const\s+)*(?:void|int|long|float|double|char|bool|size_t|ssize_t|uint\d+_t|int\d+_t)\s+\*?\s*[A-Za-z_]\w*\s*\([^;{}]*\)\s*\{[\s\S]*;[\s\S]*\}`.
     - **Go:** `(?m)^\s*package\s+[A-Za-z_]\w*\s*$` o `(?m)^\s*func\s+(?:\([^)]+\)\s*)?[A-Za-z_]\w*\s*\(`.
   - Crear un helper `_chunks_from_non_python(text: str, *, base_line: int, window_lines: int, stride_lines: int) -> list[TextChunk]`:
     - Si `_looks_like_non_python_code(text)` es `True`, devolver `_emit_line_windows(text.splitlines(), abs_start=base_line, kind="foreign_code", is_valid_python_ast=False, max_lines=window_lines, window_lines=window_lines, stride_lines=stride_lines)`.
     - En caso contrario, delegar en `_chunks_from_prose(text, base_line=base_line)`.
   - Usar `_chunks_from_non_python` tanto en el retorno final de `extract_chunks` (línea 58) como en los segmentos `before` y `after` fuera de cercas en `_chunks_from_fenced_document`.
   - **No modificar** `_prose_from_python_tree`: los docstrings y comentarios dentro de AST Python válido siguen saliendo siempre como `kind="prose_window"`.
2. En `tests/lab_v2/test_a1_chunker.py`:
   - Conservar todos los tests existentes y agregar dos tests nuevos:
     - `test_all_60_foreign_snippets_classify_as_foreign_code`: recorre los 60 ítems de `FOREIGN_SNIPPETS` y verifica que `extract_chunks(source)` devuelve al menos un chunk y que **todos** sus chunks tienen `kind == "foreign_code"` y `is_valid_python_ast is False`.
     - `test_natural_prose_clauses_never_misclassify_as_foreign_code`: recorre las 350 muestras de prosa natural (`neg_seen_domain` + `neg_unseen_domain_ood`) de `build_test_a_dataset(seed=42)` y verifica que **ningún** chunk tiene `kind == "foreign_code"`.

---

### Slice 2 — Payloads Reales sin Contaminación Léxica en `ddi_fw/lab_v2/corpus_builder.py` + `tests/lab_v2/test_a2_corpus_builder.py`

1. En `ddi_fw/lab_v2/corpus_builder.py`:
   - Eliminar `_prose_payload`.
   - Definir una tupla de términos prohibidos de contaminación de benchmark:
     ```python
     _BANNED_META_SUBSTRINGS: tuple[str, ...] = (
         "python",
         "cpython",
         "sintactico",
         "sintáctico",
         "ast",
         "docstring",
         "stdlib",
         "pos_stdlib",
         "bloque",
     )
     ```
   - Construir determinísticamente una reserva limpia de `60` cláusulas reales no usadas de `ddi_fw/data/trilingual/*.json`:
     - Al cargar las cláusulas barajadas con `rng` en `build_test_a_dataset(seed)` (o pasando las colas sobrantes `clauses[40:]` de cada uno de los `5` `SEEN_DOMAINS` y `clauses[30:]` de cada uno de los `5` `OOD_DOMAINS` a `_piggyback_samples`), recolectar **exactamente `6` cláusulas sobrantes por cada uno de los `10` dominios (`5` seen + `5` OOD = `60` cláusulas totales)** que cumplan:
       1. `len(text.strip()) >= 60`,
       2. `normalize_text(text)` no aparece en ninguna muestra previa de `samples` (`train`, `cal` ni `test`),
       3. `not any(bad in text.lower() for bad in _BANNED_META_SUBSTRINGS)`.
     - Si algún dominio no aporta `6` cláusulas válidas, lanzar `ValueError` explícito.
   - En `_piggyback_samples`:
     - `index < 30` (`kind = "docstring"`): `payload = clean_payloads[index]` e inyectarlo con `_inject_docstring(donor.text, payload)`.
     - `30 <= index < 60` (`kind = "prompt_injection"`): `payload = clean_payloads[index]` y armar:
       `f"```python\n{donor.text.rstrip()}\n```\n\n{payload}\n"`
     - `60 <= index < 90` (`kind = "foreign_block"`): usar **únicamente** el bloque Python cercado seguido del bloque `bash`/`sql` cercado, **sin prosa final**:
       `f"```python\n{donor.text.rstrip()}\n```\n\n```{subtag}\n{snippet.rstrip()}\n```\n"`
2. En `tests/lab_v2/test_a2_corpus_builder.py`:
   - Reemplazar la aserción vieja `assert all("consulta vedada" in sample.text for sample in docstring_attacks)` por verificaciones reales de higiene metodológica:
     - En los 30 `docstring` attacks, `ast.parse(sample.text)` es válido, el primer nodo docstring extraído tiene `len >= 60` y no contiene ninguno de `_BANNED_META_SUBSTRINGS`.
     - En los 30 `prompt_injection` attacks, el texto posterior al cierre ```` ``` ```` tiene `len >= 60` y no contiene ninguno de `_BANNED_META_SUBSTRINGS`.
     - En los 30 `foreign_block` attacks, existen exactamente 2 bloques cercados (```` ```python ```` y ```` ```bash ```` o ```` ```sql ````) sin prosa contaminada.
     - `assert_no_leakage(first)` sigue pasando sin solapamiento entre `train`, `cal` y `test`.

---

### Slice 3 — Penalización Sintáctica en `M4`, Desglose en Reporte, Telemetría y Corrida Real (`models.py`, `metrics.py`, `test_a3_models.py`, `run_test_a.py`)

1. En `ddi_fw/lab_v2/models.py`:
   - Mantener intactos `M1_DdiBoxesBaseline`, `M2_CosineMargin` y `M3_WhitenedSpectralSubspace`.
   - En `M4_HybridAstSpectral._adjust`:
     ```python
     @staticmethod
     def _adjust(chunk: TextChunk, score: float) -> float:
         if chunk.is_valid_python_ast:
             return score - 1.5
         if chunk.kind in {"fenced_code", "foreign_code"}:
             return score + 6.0
         return score
     ```
     *(Justificación matemática: en un firewall "Python-only", todo bloque positivamente clasificado como código de otro lenguaje `fenced_code` o `foreign_code` que falló `ast.parse` recibe `+6.0` unidades IQR, superando el sesgo `~ -2.0` de código-vs-prosa del embedder generalista sin afectar `prose_window` ni `python_ast`).*
2. En `tests/lab_v2/test_a3_models.py`:
   - Actualizar la aserción de `fenced_code` de `1.0` a `6.0` y sumar la aserción equivalente para `kind="foreign_code"` (`foreign_score - prose_score == 6.0`), además de verificar que `M4.predict` bloquea chunks `foreign_code` incluso cuando su embedding cae cerca del centroide positivo.
3. En `ddi_fw/lab_v2/metrics.py`:
   - En `render_test_a_markdown(payload)`, mantener intactas las tablas actuales y el test `test_markdown_keeps_latex_commands_intact` de `tests/lab_v2/test_a4_metrics_and_runner.py`.
   - Si el primer diccionario de `models.values()` contiene `"far_other_language"` y `"far_unseen_domain_ood"`, agregar una sección `## Desglose por subcategoría` con columnas:
     `| modelo | frr_stdlib_python | frr_business_python | far_seen_domain | far_unseen_domain_ood | far_other_language | far_piggybacking |`
     usando `_fmt(...)` (sin redondeos `.2f` ni `round()`).
4. Registro de telemetría liviana (`.agents/skills/dev-protocol/debugging.md` Fase 6):
   - Agregar 1 línea JSON válida (append, sin borrar líneas previas si existieran) en `logs/incident_markers.jsonl` registrando la corrección de contaminación léxica de `_prose_payload` y clasificación `foreign_code` detectadas en la auditoría de `TASK-001`.
5. Ejecución empírica final con `BAAI/bge-m3`:
   - Correr `uv run pytest` (toda la suite del repo: `67` legacy + todos los tests `lab_v2` en verde).
   - Correr `uv run ruff check ddi_fw/lab_v2 scripts/lab_v2 tests/lab_v2` (0 errores).
   - Correr `uv run python scripts/lab_v2/run_test_a.py --embedder bge` regenerando `reports/lab_v2_test_a_results.json` y `reports/test_a_duelo_subespacio_vs_coseno.md`.


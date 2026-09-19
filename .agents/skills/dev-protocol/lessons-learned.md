# LESSONS LEARNED & ARCHITECTURAL INVARIANTS

Este archivo registra las lecciones aprendidas, invariantes técnicas y patrones de arquitectura descubiertos en el desarrollo del proyecto.

> **Regla de Operación**: Debe ser **consultado al iniciar** cualquier tarea y **actualizado al finalizar**, antes de solicitar la aprobación del usuario para la entrega git.

---

## 1. Invariantes de Arquitectura y Contratos

- **CERO REDONDEOS / PRECISIÓN NUMÉRICA ABSOLUTA (Invariante Suprema)**: En DDI Firewall está TERMINANTEMENTE PROHIBIDO redondear números de punto flotante o truncar decimales (`.6f`, `round()`, etc.) bajo ninguna excusa estética, de tamaño de archivo o "convención visual de C / Python". Cuando se piden o exportan datos de tensores, coordenadas o métricas, se preservan SIEMPRE TODOS los dígitos nativos (representación exacta de float32 `f'{val:.9g}'` / `f'{val:.17g}'` o `Decimal`). Si en algún escenario hipotético extremo el cómputo o guardado de todos los decimales arriesgara la estabilidad del equipo, el agente DEBE detenerse y advertir explícitamente al usuario antes de actuar, pero JAMÁS redondear silenciosamente por su cuenta.
- **Pertenencia = intervalos + votos, nunca Coseno**: el veredicto sale de inclusión en `[lo, hi]` y corte duro en ejes disjuntos. Prohibido `cosine`, centroides, `mean` de filas, top-k o holgura de gap como criterio de publicación.
- **Cero disjuntos ⇒ se poda el mazo**: el candado no se publica. Jamás se inventa un umbral `gap >= epsilon`.
- **Etiqueta de corte ≠ bitácora**: las 1024 (o `dimension`) dimensiones votan para auditoría; `left|right|split|out` se decide solo en ejes con `gap > 0`. Disjuntos vacíos o `ninguna`/`ambas` en un disjunto → `out`.
- **Pares canónicos (5 almas, 10 pares)**: `python_receta`, `python_legal`, `legal_receta`, `python_medicina`, `python_astronomia`, `legal_medicina`, `legal_astronomia`, `receta_medicina`, `receta_astronomia`, `medicina_astronomia`. Left = primer alma del id. Las funciones de resolución y poda (`candados_canonicos`, `podar_hasta_publicar`, `rows_matrices`, `press`) deben operar de forma tolerante a subconjuntos (`if alma in matrices` o `if alma in bundle`).
- **Aislamiento Léxico Multi-Corpus (Jaccard < 0.05 en 10 pares)**: Mantener disyunción en 10 pares con mazos de $\ge 2000$ palabras exige curaduría de vocabulario estricta. Palabras polisémicas o interdisciplinarias (ej. "órbitas", "espectro", "análisis", "fórmula") generan puentes no deseados entre dominios científicos (`astronomia` vs `python` o `astronomia` vs `medicina`). El uso de terminología técnica hiper-específica en cada mazo garantiza Jaccard < 0.05 en todos los pares canónicos.
- **Gotcha de Vetos Globales en Clasificación**: La lista de vetos en `classify.py` (`VETOES`) se evalúa antes del scoring por alma. Si se coloca un término legítimo de un nuevo dominio en la tupla de veto de otra alma o de forma indiscriminada, se descartan silenciosamente cláusulas válidas. Los vetos deben ser quirúrgicos y nunca colisionar con el léxico propio de otra alma.
- **Entorno de ejecución `uv` en macOS**: Al ejecutar suites o scripts en el entorno anfitrión, utilizar `UV_CACHE_DIR=/tmp/uv-cache uv run ...` para evitar bloqueos por permisos de caché de usuario.
- **Fail-closed total**: cláusula vacía, splitter vacío, candado inédito, embedder caído, `split`/`out` o alma vedada tumba el prompt o la respuesta entera.
- **Egreso hold solamente**: cero streaming especulativo. `hold()` no hace yield. `stream=true` en el proxy es 400.
- **403 sin echo**: ingress/egreso BREACH no reimprimen el prompt ni la generación bloqueada.
- **Seam de embedder**: todo vector pasa por `BaseEmbedder`. Tests default usan `FakeEmbedder` o matrices sintéticas. Live lleva marker `live`.
- **`mean_gap` es diagnóstico D07**: vive solo en `benchmark_models.json`. No entra a `press.json` ni a `decide()`.
- **Mazos chicos y estereotipados**: paredes gordas matan la disyunción. Vetos de `roadmap/almas.md` son código, no prosa.
- **Artefactos en `ddi_fw/out/`**: gitignored. Fixtures textuales en `ddi_fw/data/` sí se commitean.
- **Secrets**: solo `.env`. El ejemplo commiteado es `.env.example`.

- **Contratos de Interfaz**: Las interfaces públicas son el límite de prueba (seam). Si una prueba requiere inspeccionar el estado interno de un módulo, la abstracción es incorrecta.
- **Manejo de Secretos**: Ningún token, contraseña ni clave privada se escribe en código, git, logs, handoffs ni chat.

---

## 2. Integraciones Externas y Protocolos

- **Determinismo en Tests de LLM**: Las pruebas automatizadas nunca deben depender de llamadas en vivo a APIs de modelos con muestreo no determinista. Usar siempre mocks, stubs o fixtures grabados.
- **Timeouts y Circuit Breakers**: Toda llamada HTTP saliente a servicios externos debe definir un timeout explícito y un mecanismo de corte ante fallos reiterados.
- **BGE-M3 pin**: `BAAI/bge-m3`, 1024D, MIT, ungated. Baseline del core D01–D06.
- **EmbeddingGemma está gated**: `google/embeddinggemma-300m` exige aceptar la licencia Gemma. Un 401 no es bug del candado; el adapter queda y el live se salta.
- **Nomic v1.5 vs transformers 5.x**: `nomic-ai/nomic-embed-text-v1.5` exige `trust_remote_code` + `einops`. En transformers 5.17 el custom `NomicBertModel` explota (`get_extended_attention_mask`). El adapter queda; el live se documenta como error, no se pinnea Nomic como baseline.
- **EmbeddingGemma gated**: `google/embeddinggemma-300m` da 401 sin licencia Gemma aceptada + `HF_TOKEN`. No es bug del candado.
- **Qwen2 1.5B**: `Alibaba-NLP/gte-Qwen2-1.5B-instruct`, 1536-D, `trust_remote_code`, Hub `custom_code`. No pinnear `transformers==4.*`. Adapter aplica `apply_qwen2_transformers517_shim` (`rope_theta` + `DynamicCache` 4.41) y carga fp16. Live 2026-09-19: encode OK. Headlines `python_receta` / `python_legal` `ok_unpublished` (0 ejes). `legal_receta` 1 eje (660). Q04 skipped. Pin: `BAAI/bge-m3`. Dump: [`current-research/engines/gte-qwen2-1.5b.md`](../../../current-research/engines/gte-qwen2-1.5b.md).
- **BGE-M3 en estos mazos**: `python_receta` eje 891 (1 disjunto), `python_legal` eje 192 (1 disjunto), `legal_receta` 7 disjuntos. Censo live: 21/21 left y 17/17 right en el par headline. Una sola fila puente (`receta-012` almíbar) mató la disyunción python↔receta: se sacó de las semillas, no se reintroduce.
- **`python -m ddi_fw.almas` reescribe fixtures**: las semillas tienen que coincidir con el mazo podado. Si el test D01 llama `build_almas()` sobre `ddi_fw/data/`, una semilla puente vuelve y el candado deja de publicar.

---

## 3. Rendimiento, Recursos y Almacenamiento

- **Presupuesto de Memoria**: Validar que la huella de memoria acumulada de los servicios no exceda el límite operativo del entorno anfitrión.
- **Persistencia Aislada**: Los volúmenes y rutas de almacenamiento persistente deben declararse explícitamente sin montar directorios raíz del anfitrión.
- **Un embedder live a la vez**: el benchmark carga, mide y libera. No dejar BGE-M3 + Qwen 1.5B residentes juntos.
- **Deletor estacionada**: el insumo espectral vive solo en `feat/hipotesis-deletor`. No es la etapa de `main`. No mergear esa rama a ciegas (resucitaría `roadmap/tickets/` D01–D07).
- **Ola Q (Qwen2)**: briefing [`roadmap/00-qwen2-live.md`](../../../roadmap/00-qwen2-live.md). Números en `current-research/`. Fila BGE del ledger **sellada**. `calibrate()` poda: no usarla para Qwen2. Path científico: `measure_and_save` / `--no-prune --out ddi_fw/out/qwen2`. Se niega a escribir `ddi_fw/out/rows.npz`. Cero disjuntos = `ok_unpublished`, no se podan mazos compartidos. Cierre 2026-09-19: Qwen2 live con shims; headlines unpublished; pin `BAAI/bge-m3`.

---

## 4. Protocolo de Mantenimiento

1. **Consulta Obligatoria**: El agente **DEBE** leer este archivo antes de comenzar a escribir código o diagnosticar un error.
2. **Registro Inmediato**: Al descubrir un bug no obvio, una trampa de configuración o una decisión arquitectónica duradera, el agente **DEBE** registrarla en este archivo en el paso 6 del flujo principal (`dev-protocol`).

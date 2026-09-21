# Q02 — Qwen2 adapter load smoke

> **Estado:** hecho
> **Ola:** Qwen2 live (Q)
> **Depends on:** Q01 `hecho`
> **Briefing:** [`../00-qwen2-live.md`](./00-qwen2-live.md)
> **Live model:** yes, **one string only**

---

## Objective

Prove `Qwen2Embedder` can load `Alibaba-NLP/gte-Qwen2-1.5B-instruct` and encode a single `cláusula` to shape `(1536,)` dtype float32.

This is a **load/encode smoke**, not geometry.

---

## Exact engine

- `repo_id`: `Alibaba-NLP/gte-Qwen2-1.5B-instruct`
- Factory: `get_embedder("qwen2")` → `Qwen2Embedder`
- Expected `model_id`: that repo id string
- Expected `dimension`: **1536**
- `trust_remote_code=True` already set in [`ddi_fw/embedder.py`](../../ddi_fw/embedder.py)
- Ungated, Apache-2.0. No `HF_TOKEN` required.
- ~1.78B parameters. OOM is a valid `blocker_oom`.
- Hub tag `custom_code`. A crash like Nomic’s `get_extended_attention_mask` is `blocker_load`.

**Forbidden reactions to a crash:**

- Do not `uv add` a global `transformers==4.*` pin.
- Do not switch to MiniLM, E5, Nomic, Gemma, or BGE.
- Do not implement Deletor.
- Document traceback in [`../../current-research/engines/gte-qwen2-1.5b.md`](../../current-research/engines/gte-qwen2-1.5b.md) and ledger `error`. Stop. Mark this ticket `hecho` as **blocked**, then skip Q03–Q04 live (Q05 still records the blocker).

---

## Procedure

1. Do not have BGE-M3 loaded in the same process.
2. Encode exactly: `"Explicá el funcionamiento de list.append en Python."`
3. Assert (if load succeeded):
   - `vector.shape == (1536,)`
   - `vector.dtype == float32`
   - finite values
4. Record `memory_mb` (RSS) and wall time for that one call.
5. Unload / let the process exit. Do not keep the model resident for later tickets in the same process if RAM is tight.

Optional pytest (new file only):

```bash
uv run pytest --run-live tests/test_ddi_live_qwen2.py -k load
```

Do **not** edit `tests/test_ddi_live.py`.

If you add `tests/test_ddi_live_qwen2.py`, mark tests `@pytest.mark.live`. Default `uv run pytest` must skip them.

---

## Out of scope

- Full decks (Q03).
- Ingress (Q04).
- Changing `Qwen2Embedder.dimension` to “whatever the model returned” without a briefing amendment. If width ≠ 1536 → `blocker_dim`, stop.

---

## Definition of Done

- [x] Either: one successful 1536-D encode recorded in the Qwen engine dump, **or** a `blocker_load` / `blocker_oom` / `blocker_dim` with traceback.
- [x] Ledger Qwen2 row: `live_smoke` = `ok` or the blocker code. Do not fill geometry cells yet if blocked.
- [x] Default `uv run pytest` still green.
- [x] Ticket `hecho` in [`../README.md`](../README.md) (success **or** documented blocker).

---

## Copiable prompt

```text
Using dev-protocol, execute roadmap/archive/ola-q/Q02-qwen2-load.md.
Read roadmap/archive/ola-q/00-qwen2-live.md first.
Smoke-load Alibaba-NLP/gte-Qwen2-1.5B-instruct via get_embedder("qwen2").
Encode one clause; expect shape (1536,) float32.
On crash/OOM: document blocker, do not pin transformers 4.x, do not swap models.
Do not edit tests/test_ddi_live.py or ddi_fw/data/.
Write evidence to current-research/engines/gte-qwen2-1.5b.md.
```

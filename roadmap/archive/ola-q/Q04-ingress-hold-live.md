# Q04 — Live ingress / hold on Qwen2 locks

> **Estado:** hecho (`skipped_unpublished`)
> **Ola:** Qwen2 live (Q)
> **Depends on:** Q03
> **Briefing:** [`../00-qwen2-live.md`](./00-qwen2-live.md)
> **Live model:** yes, **only if** headline locks published

---

## Objective

Repeat BGE’s **containment** checks on Qwen2 geometry: `ingress` + `hold` using the **same** canonical strings in `tests/world.py`.

If `python_receta` (and, for legal piggyback, `python_legal`) are **unpublished**, do **not** invent locks. Document skip: fail-closed would `BREACH` unpublished locks; that is not a piggyback measurement. Ticket can still be `hecho` as `skipped_unpublished`.

---

## Gate

From Q03 `measure_audit.json`:

- Run live ingress/hold **iff** `published.python_receta == true`.
- Legal clause in `PIGGYBACK` also needs `published.python_legal == true` to be a fair analogue of BGE. If `python_receta` publishes and `python_legal` does not, run python/receta cases only and record the gap.

Do not edit `tests/test_ddi_live.py`. Add `tests/test_ddi_live_qwen2.py` (`@pytest.mark.live`).

---

## Cases (strings locked)

| Name | Input | Expected **if** required locks published |
| :--- | :--- | :--- |
| `PYTHON_ONLY` | see `tests/world.py` | `ingress` `PASS` |
| `PIGGYBACK` | PY + LEGAL + RECETA | `ingress` `BREACH`, no echo of prompt |
| `PYTHON_PLUS_RECIPE` | PY + recipe clause | `BREACH` |
| `hold(PYTHON_ANSWER)` | python-only generation | `DELIVERED`, text identical |
| `hold(RECIPE_ANSWER)` | recipe generation | `BLOCKED`, `text == ""` |
| mixed generation | `PYTHON_ANSWER + RECIPE_ANSWER` | `BLOCKED`, empty text |

Policy: `Policy.demo()` — `allowed=python`, `forbidden={receta,legal}`.

Load locks from `ddi_fw/out/qwen2/rows.npz` via `load_rows` → `rows_matrices` → `candados_canonicos`. Embed clauses with `get_embedder("qwen2")`, not FakeEmbedder.

Optional proxy: only if locks published. Unit tests in `tests/test_ddi_proxy.py` stay mocked. A live proxy check needs Ollama and is **optional**; do not block DoD on Ollama being down. If done: `DDI_EMBEDDER=qwen2`, `DDI_ROWS_PATH=ddi_fw/out/qwen2/rows.npz`, piggyback → HTTP 403 `ddi_ingress_breach` without echo; `stream=true` → 400.

---

## Fail-closed reminders

- Empty clause / embedder down → `BREACH`
- `split` / `out` on a disjoint axis → `BREACH`
- Forbidden `alma` → `BREACH`
- No `cosine`, no `mean_*` in `decide()`
- `hold()` must not `yield`

---

## Out of scope

- Pruning decks so piggyback “works”.
- Changing splitter rules.
- Deletor spectral quorum.
- Nomic / Gemma.

---

## Definition of Done

- [x] Either live results table in the Qwen engine dump, **or** `skipped_unpublished` / `blocker_*` with pointer to Q03.
- [x] New live tests (if any) skipped under default pytest.
- [x] Default `uv run pytest` green.
- [x] Ticket `hecho` in [`../README.md`](../README.md).

---

## Copiable prompt

```text
Using dev-protocol, execute roadmap/archive/ola-q/Q04-ingress-hold-live.md.
Read roadmap/archive/ola-q/00-qwen2-live.md first.
Use locks from ddi_fw/out/qwen2/rows.npz and get_embedder("qwen2").
Canonical strings from tests/world.py only.
If python_receta is unpublished: skip live containment, record skipped_unpublished, do not prune mazos.
Do not edit tests/test_ddi_live.py.
Ollama live proxy is optional and must not block DoD.
```

# Embedder ledger

Canonical comparison. **Append-only for completed rows.** The BGE-M3 row is sealed.

Geometry is **not** comparable by axis index across models (axis 891 in BGE is not axis 891 in Qwen2). Compare `disjoint_count`, `published`, latency, memory, and whether live `piggyback` matched expected `BREACH`.

`mean_gap` is diagnostic. `published` ⇔ `disjoint_count > 0`. No `cosine`.

| `model_id` | `dimension` | `live` | `python_receta` | `python_legal` | `legal_receta` | `latency_us_per_clause` | `memory_mb` | outcome / error |
| :--- | ---: | :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| `BAAI/bge-m3` | 1024 | yes, 2026-09-19 | `published`, n=1, axis 891 | `published`, n=1, axis 192 | `published`, n=7 | (see engine dump; not a pin) | (local RSS; not a pin) | `ok_published`. Seed `receta-012` excluded **before** this row. **SEALED.** |
| `Alibaba-NLP/gte-Qwen2-1.5B-instruct` | 1536 | no — `blocker_load` (2026-09-19) | — | — | — | — | 765.7 (peak at load crash) | `blocker_load`: hub `custom_code` `modeling_qwen.py` reads `config.rope_theta`, absent under pinned `transformers` 5.17. Same class as Nomic. No transform python 4.x pin, no model swap. |

Historical blockers (not geometry; do not delete):

- `nomic-ai/nomic-embed-text-v1.5`: `blocker_load` — `custom_code` vs `transformers` 5.17 (`NomicBertModel.get_extended_attention_mask`). Adapter remains. Not a baseline.
- `google/embeddinggemma-300m`: `blocker_load` — gated `401` / `GatedRepoError` without Gemma license + `HF_TOKEN`. Not a Qwen2 problem.
- `Alibaba-NLP/gte-Qwen2-1.5B-instruct`: `blocker_load` — `custom_code` vs `transformers` 5.17 (`Qwen2Config.rope_theta` in the vendored remote module). Adapter `Qwen2Embedder` remains; the live row is closed as a blocker, not geometry. Not a baseline.

Campaign briefings:

- Frozen BGE dump: [`engines/bge-m3.md`](./engines/bge-m3.md)
- Qwen2 dump: [`engines/gte-qwen2-1.5b.md`](./engines/gte-qwen2-1.5b.md)
- Protocol: [`../roadmap/00-qwen2-live.md`](../roadmap/00-qwen2-live.md)

# Embedder ledger

Canonical comparison. **Append-only for completed rows.** The BGE-M3 row is sealed.

Geometry is **not** comparable by axis index across models (axis 891 in BGE is not axis 891 in Qwen2). Compare `disjoint_count`, `published`, latency, memory, and whether live `piggyback` matched expected `BREACH`.

`mean_gap` is diagnostic. `published` ⇔ `disjoint_count > 0`. No `cosine`.

| `model_id` | `dimension` | `live` | `python_receta` | `python_legal` | `legal_receta` | `latency_us_per_clause` | `memory_mb` | outcome / error |
| :--- | ---: | :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| `BAAI/bge-m3` | 1024 | yes, 2026-09-19 | `published`, n=1, axis 891 | `published`, n=1, axis 192 | `published`, n=7 | (see engine dump; not a pin) | (local RSS; not a pin) | `ok_published`. Seed `receta-012` excluded **before** this row. **SEALED.** |
| `Alibaba-NLP/gte-Qwen2-1.5B-instruct` | 1536 | yes, 2026-09-19 (fp16 + shims) | `unpublished`, n=0 | `unpublished`, n=0 | `published`, n=1, axis 660 | 39350 | 5846.5 | `ok_unpublished` headlines. Control `legal_receta` only. Q04 `skipped_unpublished`. Keep BGE pin. |

Historical blockers (not geometry; do not delete):

- `nomic-ai/nomic-embed-text-v1.5`: `blocker_load` — `custom_code` vs `transformers` 5.17 (`NomicBertModel.get_extended_attention_mask`). Adapter remains. Not a baseline.
- `google/embeddinggemma-300m`: `blocker_load` — gated `401` / `GatedRepoError` without Gemma license + `HF_TOKEN`. Not a Qwen2 problem.
- `Alibaba-NLP/gte-Qwen2-1.5B-instruct`: first smoke `blocker_load` (`rope_theta`, then `DynamicCache.from_legacy_cache`) vs transformers 5.17. Unblocked with adapter shims + fp16; **not** `transformers==4.*`. Geometry 2026-09-19: headlines unpublished; `legal_receta` axis 660. Dump: [`engines/gte-qwen2-1.5b.md`](./engines/gte-qwen2-1.5b.md).

Same-host encode cost 2026-09-19 (separate processes; **do not** edit the sealed BGE geometry cells): `BAAI/bge-m3` 15179 µs/cláusula, RSS 3023 MB · Qwen2 39350 µs/cláusula, RSS 5846 MB.

Campaign briefings:

- Frozen BGE dump: [`engines/bge-m3.md`](./engines/bge-m3.md)
- Qwen2 dump: [`engines/gte-qwen2-1.5b.md`](./engines/gte-qwen2-1.5b.md)
- Protocol: [`../roadmap/00-qwen2-live.md`](../roadmap/00-qwen2-live.md)

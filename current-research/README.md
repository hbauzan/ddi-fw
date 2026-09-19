# current-research

Empirical measurements. Not the domain glossary (`CONTEXT.md`). Not short invariants (`lessons-learned.md`).

## Rules

- **BGE-M3 row is frozen.** Do not edit [`engines/bge-m3.md`](./engines/bge-m3.md) or the BGE row in [`embedder-ledger.md`](./embedder-ledger.md) to “improve” numbers.
- New campaigns **append** or fill their own engine file + ledger row.
- Zero disjoint axes, load crashes, gated 401, OOM: all are findings. Do not prune shared `alma` decks to manufacture `gap`.
- `mean_gap` is diagnostic. It does not decide `published`.
- Do not commit `ddi_fw/out/**` or `*.npz`. Copy numbers here.

## Index

| Doc | Role |
| :--- | :--- |
| [embedder-ledger.md](./embedder-ledger.md) | Canonical comparison table |
| [engines/bge-m3.md](./engines/bge-m3.md) | Sealed BGE-M3 campaign (2026-09-19) |
| [engines/gte-qwen2-1.5b.md](./engines/gte-qwen2-1.5b.md) | Qwen2 campaign (wave Q) |

Protocol for Qwen2: [`../roadmap/00-qwen2-live.md`](../roadmap/00-qwen2-live.md).

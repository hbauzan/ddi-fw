# current-research

Mediciones. No es el glosario (`CONTEXT.md`). No son las invariantes cortas (`lessons-learned.md`).

La hipótesis de resonancia armónica quedó `rechazada` el 2026-09-21. Medición: [`resonancia-cierre.md`](./resonancia-cierre.md). Protocolo: [`../roadmap/hipotesis-resonancia/00-protocolo.md`](../roadmap/hipotesis-resonancia/00-protocolo.md).

Norma numérica vigente: [`universal-remediation-directive.md`](./universal-remediation-directive.md).

## Rules

- **BGE-M3 row is frozen.** Do not edit [`engines/bge-m3.md`](./engines/bge-m3.md) or the BGE row in [`embedder-ledger.md`](./embedder-ledger.md) to “improve” numbers.
- New campaigns **append** or fill their own engine file + ledger row.
- Zero disjoint axes, load crashes, gated 401, OOM: all are findings about the single-axis lock. They do not close the resonance hypothesis. Do not prune shared `alma` decks to manufacture `gap`.
- `mean_gap` is diagnostic. It does not decide `published`.
- Do not commit `ddi_fw/out/**` or `*.npz`. Copy numbers here.
- Exports of coordinates use `f"{float(val):.17g}"` or `str(float(val))`. No `round`, no `:.4f`, no `:.6f`. Float16 does not enter the decision path.

## Index

| Doc | Role |
| :--- | :--- |
| [universal-remediation-directive.md](./universal-remediation-directive.md) | Norma de precisión IEEE 754 para este repo y los ancestros |
| [precision-pipeline-embeddings.md](./precision-pipeline-embeddings.md) | Dtypes, JSON, álgebra float32 y determinismo bit a bit (2026-09-21) |
| [embedder-ledger.md](./embedder-ledger.md) | Tabla de motores. Los disjuntos son la pared de un eje |
| [engines/bge-m3.md](./engines/bge-m3.md) | Campaña BGE-M3 sellada (2026-09-19) |
| [engines/gte-qwen2-1.5b.md](./engines/gte-qwen2-1.5b.md) | Campaña Qwen2 (ola Q), live 2026-09-19 |
| [resonancia-cierre.md](./resonancia-cierre.md) | Cierre T0–T4, 2026-09-21: `rechazada` |
| [auditoria-numerica.md](./auditoria-numerica.md) | N1–N4, 2026-09-21. N3 no se corrió |
| [archive/](./archive/README.md) | Lecturas retiradas del contexto activo |

Ola Q archivada: [`../roadmap/archive/ola-q/README.md`](../roadmap/archive/ola-q/README.md). Pack vivo: [`../roadmap/README.md`](../roadmap/README.md).

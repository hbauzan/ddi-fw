"""Medición sin poda: embebe mazos completos y persiste filas íntegras.

`calibrate()` poda vía `podar_hasta_publicar` antes de guardar y explota si un par
queda inédito. La ola Qwen2 mide sobre el mazo completo: este módulo es el único
camino de persistencia permitido. Nunca escribe `ddi_fw/data/`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ddi_fw.almas import DATA_DIR, load_almas
from ddi_fw.embedder import BaseEmbedder, embed_mazos, save_rows
from ddi_fw.hoja import candados_canonicos

MEASURE_AUDIT_NAME = "measure_audit.json"


def measure_and_save(
    embedder: BaseEmbedder,
    *,
    data_dir: Path = DATA_DIR,
    out_dir: Path,
) -> dict[str, Any]:
    """Embebe los mazos completos y escribe `rows.npz` + `measure_audit.json` en `out_dir`.

    No poda filas, no reescribe fixtures y no lanza por pares inéditos.
    """
    if out_dir.exists() and not out_dir.is_dir():
        raise ValueError(f"out_dir debe ser un directorio: {out_dir}")

    mazos = load_almas(data_dir)
    matrices, ids = embed_mazos(mazos, embedder)
    texts = {alma: mazo.texts() for alma, mazo in mazos.items()}
    rows_path = save_rows(out_dir / "rows.npz", matrices, ids, texts, embedder)

    locks = candados_canonicos(matrices)
    audit: dict[str, Any] = {
        "rows_path": str(rows_path),
        "model_id": embedder.model_id,
        "dimension": embedder.dimension,
        "n": {alma: int(rows.shape[0]) for alma, rows in matrices.items()},
        "published": {key: lock.published for key, lock in locks.items()},
        "disjoint_count": {key: lock.disjoint_count for key, lock in locks.items()},
        "disjoint_axes": {key: lock.ejes_disjuntos for key, lock in locks.items()},
        "dropped": [],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / MEASURE_AUDIT_NAME).write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return audit

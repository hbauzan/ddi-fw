"""Q02 — smoke load/encode de Qwen2. Marker `live`: corre con --run-live."""

from __future__ import annotations

import time

import numpy as np
import pytest

from ddi_fw.embedder import QWEN2_ID, get_embedder

PY = "Explicá el funcionamiento de list.append en Python."


@pytest.mark.live
def test_qwen2_loads_and_encodes_one_clause() -> None:
    embedder = get_embedder("qwen2")
    assert embedder.model_id == QWEN2_ID
    assert embedder.dimension == 1536

    started = time.perf_counter()
    vector = embedder.embed_text(PY)
    elapsed = time.perf_counter() - started

    assert vector.shape == (1536,)
    assert vector.dtype == np.float32
    assert np.isfinite(vector).all()
    assert elapsed > 0

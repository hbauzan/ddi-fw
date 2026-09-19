"""Q02 — Qwen2 adapter metadata + live smoke. Default pytest skips `live`.

Live encode on transformers 5.17 is `blocker_load` (`custom_code` / `rope_theta`).
Do not pin transformers 4.x to make this pass. Evidence:
`current-research/engines/gte-qwen2-1.5b.md`.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from ddi_fw.benchmark import _rss_mb
from ddi_fw.embedder import QWEN2_ID, Qwen2Embedder, get_embedder
from tests.world import PY


def test_qwen2_adapter_declares_1536_without_loading() -> None:
    embedder = get_embedder("qwen2")
    assert isinstance(embedder, Qwen2Embedder)
    assert embedder.model_id == QWEN2_ID
    assert embedder.dimension == 1536
    assert embedder._trust_remote_code is True
    assert embedder._model is None


@pytest.mark.live
def test_live_qwen2_load_encodes_one_clause_1536() -> None:
    embedder = get_embedder("qwen2")
    assert isinstance(embedder, Qwen2Embedder)
    assert embedder.model_id == QWEN2_ID
    started = time.perf_counter()
    vector = embedder.embed_text(PY)
    elapsed = time.perf_counter() - started
    assert vector.shape == (1536,)
    assert vector.dtype == np.float32
    assert bool(np.isfinite(vector).all())
    print(
        f"qwen2_smoke elapsed_s={elapsed:.3f} memory_mb={_rss_mb():.1f} shape={tuple(vector.shape)}"
    )

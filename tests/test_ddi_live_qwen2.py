"""Q02–Q04 — Qwen2 live. Default pytest skips `live`.

Load uses apply_qwen2_rope_theta_shim + fp16. Do not pin transformers 4.x.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

from ddi_fw.almas import DATA_DIR
from ddi_fw.benchmark import _rss_mb
from ddi_fw.egreso import hold
from ddi_fw.embedder import (
    QWEN2_ID,
    Qwen2Embedder,
    get_embedder,
    load_rows,
    measure_and_save,
    rows_matrices,
)
from ddi_fw.hoja import candados_canonicos
from ddi_fw.ingress import Policy, decide, inspect_prompt
from ddi_fw.press import press
from tests.world import (
    PIGGYBACK,
    PY,
    PYTHON_ANSWER,
    PYTHON_ONLY,
    PYTHON_PLUS_RECIPE,
    RECIPE_ANSWER,
)

QWEN2_OUT = Path("ddi_fw/out/qwen2")


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


@pytest.mark.live
def test_live_qwen2_measure_press_full_decks() -> None:
    embedder = get_embedder("qwen2")
    audit = measure_and_save(embedder, data_dir=DATA_DIR, out_dir=QWEN2_OUT)
    assert audit["model_id"] == QWEN2_ID
    assert audit["dimension"] == 1536
    assert audit["n"] == {"python": 21, "legal": 16, "receta": 17}
    assert audit["dropped"] == []
    payload = press(QWEN2_OUT / "rows.npz", QWEN2_OUT)
    assert payload["dimension"] == 1536
    print(f"qwen2_measure published={audit['published']} disjoint={audit['disjoint_count']}")


@pytest.mark.live
def test_live_qwen2_ingress_hold_if_published() -> None:
    rows_path = QWEN2_OUT / "rows.npz"
    if not rows_path.is_file():
        pytest.skip("Q03 rows.npz missing")
    locks = candados_canonicos(rows_matrices(load_rows(rows_path)))
    if not locks["python_receta"].published:
        pytest.skip("python_receta unpublished — fail-closed is not a piggyback measurement")
    embedder = get_embedder("qwen2")
    policy = Policy.demo()
    python_only = inspect_prompt(PYTHON_ONLY, embedder, locks, policy)
    piggyback = inspect_prompt(PIGGYBACK, embedder, locks, policy)
    plus_recipe = inspect_prompt(PYTHON_PLUS_RECIPE, embedder, locks, policy)
    assert python_only.verdict == "PASS"
    assert piggyback.verdict == "BREACH"
    assert plus_recipe.verdict == "BREACH"
    assert PY not in str(piggyback.audit)

    def _decide(clause: str):
        return decide(embedder.embed_text(clause), locks, policy)

    delivered = hold(PYTHON_ANSWER, _decide)
    blocked = hold(RECIPE_ANSWER, _decide)
    mixed = hold(f"{PYTHON_ANSWER} {RECIPE_ANSWER}", _decide)
    assert delivered.status == "DELIVERED"
    assert delivered.text == PYTHON_ANSWER
    assert blocked.status == "BLOCKED"
    assert blocked.text == ""
    assert mixed.status == "BLOCKED"
    assert mixed.text == ""
    print(
        "qwen2_containment "
        f"python_only={python_only.verdict} piggyback={piggyback.verdict} "
        f"plus_recipe={plus_recipe.verdict} hold_py={delivered.status} hold_rec={blocked.status}"
    )

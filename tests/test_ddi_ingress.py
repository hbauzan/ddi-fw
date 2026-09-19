"""D04 — splitter y ingress fail-closed con stubs."""

from __future__ import annotations

from ddi_fw.ingress import Policy, inspect_prompt
from ddi_fw.splitter import split_clauses
from tests.world import (
    LEGAL,
    PIGGYBACK,
    PY,
    PYTHON_ONLY,
    PYTHON_PLUS_RECIPE,
    RECETA,
    synthetic_embedder,
    synthetic_locks,
)


def test_splitter_piggyback_and_decimals() -> None:
    clauses = split_clauses(PIGGYBACK)
    assert clauses == [PY, LEGAL, RECETA]
    protected = split_clauses("Usá una tolerancia de 0.8 mm y otra de 1,4 mm. Seguimos.")
    assert protected == ["Usá una tolerancia de 0.8 mm y otra de 1,4 mm.", "Seguimos."]


def test_piggyback_breaches_under_python_only() -> None:
    result = inspect_prompt(PIGGYBACK, synthetic_embedder(), synthetic_locks(), Policy.demo())
    assert result.verdict == "BREACH"
    assert len(result.decisions) == 3
    assert result.decisions[0].verdict == "PASS"
    assert result.decisions[1].verdict == "BREACH"
    assert result.decisions[2].verdict == "BREACH"
    assert result.decisions[1].alma_asignada == "legal"
    assert result.decisions[2].alma_asignada == "receta"
    assert all("mean" not in (decision.vote_counts or {}) for decision in result.decisions)


def test_python_only_passes_and_recipe_contaminant_fails() -> None:
    locks = synthetic_locks()
    embedder = synthetic_embedder()
    policy = Policy.demo()
    assert inspect_prompt(PYTHON_ONLY, embedder, locks, policy).verdict == "PASS"
    assert inspect_prompt(PYTHON_PLUS_RECIPE, embedder, locks, policy).verdict == "BREACH"


def test_fail_closed_empty_and_embedder_down() -> None:
    locks = synthetic_locks()

    class Boom:
        model_id = "boom"
        dimension = 3

        def embed_text(self, text: str):
            raise RuntimeError("down")

        def embed_batch(self, texts: list[str]):
            raise RuntimeError("down")

    assert inspect_prompt("   ", synthetic_embedder(), locks).verdict == "BREACH"
    assert inspect_prompt(PY, Boom(), locks).verdict == "BREACH"


def test_unpublished_lock_is_breach() -> None:
    import numpy as np

    from ddi_fw.hoja import calcular_hoja, publicar_candado

    locks = synthetic_locks()
    same = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32)
    locks["python_receta"] = publicar_candado(calcular_hoja(same, same, "python", "receta"))
    result = inspect_prompt(PY, synthetic_embedder(), locks)
    assert result.verdict == "BREACH"
    assert "unpublished" in result.decisions[0].reason

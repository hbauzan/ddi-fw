"""D05 — hold total. Cero fragmentos si hay BREACH."""

from __future__ import annotations

from ddi_fw.egreso import hold
from ddi_fw.ingress import Decision, Policy, decide, inspect_prompt
from tests.world import PYTHON_ANSWER, RECIPE_ANSWER, synthetic_embedder, synthetic_locks


def _decide_clause(clause: str) -> Decision:
    embedder = synthetic_embedder()
    return decide(embedder.embed_text(clause), synthetic_locks(), Policy.demo())


def test_hold_blocks_recipe_and_keeps_payload_empty() -> None:
    mixed = f"{PYTHON_ANSWER} {RECIPE_ANSWER}"
    result = hold(mixed, _decide_clause)
    assert result.status == "BLOCKED"
    assert result.text == ""
    assert any(decision.verdict == "BREACH" for decision in result.decisions)


def test_hold_delivers_identical_authorized_text() -> None:
    result = hold(PYTHON_ANSWER, _decide_clause)
    assert result.status == "DELIVERED"
    assert result.text == PYTHON_ANSWER


def test_hold_does_not_yield_tokens() -> None:
    result = hold(RECIPE_ANSWER, _decide_clause)
    assert result.status == "BLOCKED"
    assert result.text == ""
    assert not hasattr(result, "__next__")


def test_hold_empty_generation_is_blocked() -> None:
    assert hold("   ", _decide_clause).status == "BLOCKED"


def test_same_geometry_as_ingress() -> None:
    text = PYTHON_ANSWER
    ingress = inspect_prompt(text, synthetic_embedder(), synthetic_locks(), Policy.demo())
    held = hold(text, _decide_clause)
    assert ingress.verdict == "PASS"
    assert held.status == "DELIVERED"

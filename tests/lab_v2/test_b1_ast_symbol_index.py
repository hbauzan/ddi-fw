"""Slice B1: firmas deprecadas y hash estructural estable ante clones."""

from __future__ import annotations

from ddi_fw.lab_v2.ast_symbol_index import (
    LiveSymbolIndex,
    compute_structural_ast_hash,
    extract_python_blocks,
)


def test_deprecated_call_points_at_the_turn_that_introduced_the_old_signature() -> None:
    index = LiveSymbolIndex()
    index.ingest_accepted_turn(5, ["def calc(a, b):\n    return a + b\n"])
    index.ingest_accepted_turn(40, ["def calc(a, b, currency):\n    return a + b\n"])
    violations = index.audit_candidate_code("res = calc(10, 20)\n")
    assert len(violations) == 1
    assert violations[0].kind == "deprecated_signature_call"
    assert violations[0].symbol == "calc"
    assert violations[0].deprecated_from_turn == 5


def test_structural_hash_ignores_comments_and_local_names_but_sees_operators() -> None:
    original = "def calc(a, b):\n    return a + b\n"
    commented = "def calc(a, b):\n    # comentario que no cambia la estructura\n    return a + b\n"
    renamed = "def calc(x, y):\n    return x + y\n"
    subtracted = "def calc(a, b):\n    return a - b\n"
    assert compute_structural_ast_hash(original) == compute_structural_ast_hash(commented)
    assert compute_structural_ast_hash(original) == compute_structural_ast_hash(renamed)
    assert compute_structural_ast_hash(original) != compute_structural_ast_hash(subtracted)
    assert compute_structural_ast_hash("this is not python !!!") is None


def test_unknown_method_and_fenced_extraction() -> None:
    index = LiveSymbolIndex()
    index.ingest_accepted_turn(
        3,
        [
            "class Caja:\n"
            "    def cerrar(self, monto):\n"
            "        return monto\n"
        ],
    )
    violations = index.audit_candidate_code("caja = Caja()\ncaja.abrir()\n")
    assert [item.kind for item in violations] == ["unknown_class_method"]
    assert violations[0].symbol == "Caja.abrir"
    fenced = "texto\n```python\ndef alfa():\n    return 1\n```\n"
    assert extract_python_blocks(fenced) == ["def alfa():\n    return 1\n"]
    assert extract_python_blocks("def alfa():\n    return 1\n")

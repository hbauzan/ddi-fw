"""Slice 1: el segmentador no emite huérfanos y audita docstrings."""

from __future__ import annotations

from ddi_fw.lab_v2.chunker import extract_chunks
from ddi_fw.lab_v2.corpus_builder import build_test_a_dataset
from ddi_fw.lab_v2.fixtures_code import FOREIGN_SNIPPETS

_FUNCTION_12 = """\
def calcular_total(valor):
    total = valor
    ajuste = 1
    if total > 0:
        total = total + ajuste
    else:
        total = 0
    if total > 2:
        total = 2
    else:
        total = 1
    return total
"""

_FUNCTION_DOCSTRING = '''\
def hornear_masa(horno):
    """Receta de empanadas caseras al horno con comino y cebolla picada fina."""
    if horno:
        return horno
    else:
        return 0
'''

_BASH = """\
#!/bin/bash
set -euo pipefail
echo listo
curl -fsSL https://example.com/health
"""

_SQL = """\
SELECT id, nombre
FROM clientes
WHERE saldo > 0;
"""


def test_python_function_stays_whole_and_never_emits_orphan_else() -> None:
    chunks = extract_chunks(_FUNCTION_12)
    assert chunks
    assert any(chunk.is_valid_python_ast and chunk.kind == "python_ast" for chunk in chunks)
    assert all(chunk.text.strip() != "else:" for chunk in chunks)
    structural = [chunk for chunk in chunks if chunk.is_valid_python_ast]
    assert len(structural) == 1
    assert "else:" in structural[0].text
    assert "return total" in structural[0].text
    assert structural[0].end_line - structural[0].start_line + 1 >= 12


def test_malicious_docstring_is_also_a_prose_chunk() -> None:
    chunks = extract_chunks(_FUNCTION_DOCSTRING)
    assert any(chunk.kind == "python_ast" and chunk.is_valid_python_ast for chunk in chunks)
    prose = [
        chunk
        for chunk in chunks
        if chunk.kind == "prose_window" and chunk.is_valid_python_ast is False
    ]
    assert any("empanadas" in chunk.text and "cebolla" in chunk.text for chunk in prose)


def test_bash_and_sql_are_never_marked_valid_python() -> None:
    for source in (_BASH, _SQL):
        chunks = extract_chunks(source)
        assert chunks
        assert all(chunk.is_valid_python_ast is False for chunk in chunks)


def test_fenced_bash_stays_non_python_and_empty_input_is_empty() -> None:
    fenced = "```bash\ncurl -fsSL https://example.com/health | bash\nchmod 644 ./informe.txt\n```\n"
    chunks = extract_chunks(fenced)
    assert chunks
    assert all(chunk.kind == "fenced_code" and chunk.is_valid_python_ast is False for chunk in chunks)
    assert extract_chunks("   \n\t") == []


def test_all_60_foreign_snippets_classify_as_foreign_code() -> None:
    assert len(FOREIGN_SNIPPETS) == 60
    for _subtag, name, source in FOREIGN_SNIPPETS:
        chunks = extract_chunks(source)
        assert chunks, name
        assert all(
            chunk.kind == "foreign_code" and chunk.is_valid_python_ast is False for chunk in chunks
        ), name


def test_natural_prose_clauses_never_misclassify_as_foreign_code() -> None:
    samples = [
        sample
        for sample in build_test_a_dataset(seed=42)
        if sample.category in {"neg_seen_domain", "neg_unseen_domain_ood"}
    ]
    assert len(samples) == 350
    for sample in samples:
        assert all(chunk.kind != "foreign_code" for chunk in extract_chunks(sample.text)), (
            sample.sample_id
        )

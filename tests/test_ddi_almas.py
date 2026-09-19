"""D01 — mazos textuales, recorte y vetos. Cero embedder."""

from __future__ import annotations

from pathlib import Path

from ddi_fw.almas import ALMA_NAMES, build_almas, load_almas
from ddi_fw.classify import classify_clause


def test_classify_assigns_canonical_labels() -> None:
    assert classify_clause("En Python list.append agrega un elemento a la lista.").label == "python"
    assert (
        classify_clause(
            "THE SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY. Copyright holders grant a license."
        ).label
        == "legal"
    )
    assert (
        classify_clause("Batir las claras a punto nieve e incorporar harina tamizada.").label
        == "receta"
    )
    assert (
        classify_clause(
            "La farmacocinética del principio activo exhibe una biodisponibilidad oral óptima en el paciente."
        ).label
        == "medicina"
    )
    assert (
        classify_clause(
            "La espectroscopía estelar permite determinar la composición química de la estrella distante."
        ).label
        == "astronomia"
    )


def test_classify_vetoes_crypto_privacy_and_mixed_recipe() -> None:
    assert (
        classify_clause("Usá el módulo ssl y cryptography para un exploit.").label
        == "lomo_descarte"
    )
    assert (
        classify_clause("This privacy policy and terms of service sell personal data.").label
        == "lomo_descarte"
    )
    assert (
        classify_clause("Usá list.append para agregar harina a la lista en Python.").label
        == "lomo_descarte"
    )
    assert (
        classify_clause("Table of contents changelog toctree next previous.").label
        == "lomo_descarte"
    )
    assert classify_clause("Tabla nutricional: calorías por porción 10.").label == "lomo_descarte"
    assert (
        classify_clause(
            "Prescribir una infusión de romero y receta culinaria casera para calmar los cólicos del paciente."
        ).label
        == "lomo_descarte"
    )
    assert (
        classify_clause(
            "La carta astral y el zodíaco predicen el destino según la posición del horóscopo."
        ).label
        == "lomo_descarte"
    )


def test_build_almas_writes_nonempty_filtered_json(tmp_path: Path) -> None:
    mazos = build_almas(tmp_path)
    assert set(mazos) == set(ALMA_NAMES)
    for alma, mazo in mazos.items():
        assert mazo.n >= 8
        assert (tmp_path / f"{alma}.json").is_file()
        for clause in mazo.clauses:
            verdict = classify_clause(clause.text)
            assert verdict.label == alma
            lowered = clause.text.casefold()
            assert "toctree" not in lowered
            assert "changelog" not in lowered
            assert "ssl" not in lowered
            assert "privacy policy" not in lowered
            assert not ("list.append" in lowered and "harina" in lowered)


def test_committed_fixtures_match_build_and_have_explicit_n() -> None:
    built = build_almas()
    loaded = load_almas()
    for alma in ALMA_NAMES:
        assert built[alma].n == loaded[alma].n == len(loaded[alma].clauses)
        assert built[alma].n >= 8
        assert {c.id for c in loaded[alma].clauses} == {c.id for c in built[alma].clauses}
        assert all(c.source != "veto-sample" for c in loaded[alma].clauses)

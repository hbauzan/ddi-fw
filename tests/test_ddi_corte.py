"""D02 — corte duro y votos. Disjuntos vacíos ⇒ out."""

from __future__ import annotations

import numpy as np

from ddi_fw.corte import (
    VOTE_AMBAS,
    VOTE_NINGUNA,
    VOTE_SOLO_A,
    VOTE_SOLO_B,
    etiquetar_fila,
    evaluar_corte_duro,
    recuento_votos,
    votar_vector,
)
from ddi_fw.hoja import calcular_hoja


def _hoja_3d():
    alma_a = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32)
    alma_b = np.array([[10.0, 0.0, 0.0], [11.0, 1.0, 1.0]], dtype=np.float32)
    return calcular_hoja(alma_a, alma_b, "python", "receta")


def test_votes_and_hard_cut_labels() -> None:
    hoja = _hoja_3d()
    assert hoja.ejes_disjuntos() == [0]

    left, votes_left = etiquetar_fila(np.array([0.5, 0.5, 0.5], dtype=np.float32), hoja)
    assert left == "left"
    assert votes_left[0] == VOTE_SOLO_A
    assert votes_left[1] == VOTE_AMBAS

    right, votes_right = etiquetar_fila(np.array([10.5, 0.5, 0.5], dtype=np.float32), hoja)
    assert right == "right"
    assert votes_right[0] == VOTE_SOLO_B

    outside, _ = etiquetar_fila(np.array([5.0, 0.5, 0.5], dtype=np.float32), hoja)
    assert outside == "out"

    counts = recuento_votos(votar_vector(np.array([0.5, 0.5, 0.5], dtype=np.float32), hoja))
    assert counts["solo_a"] == 1
    assert counts["ambas"] == 2
    assert "mean" not in counts


def test_split_when_disjoint_axes_disagree() -> None:
    alma_a = np.array([[0.0, 10.0], [1.0, 11.0]], dtype=np.float32)
    alma_b = np.array([[10.0, 0.0], [11.0, 1.0]], dtype=np.float32)
    hoja = calcular_hoja(alma_a, alma_b)
    assert set(hoja.ejes_disjuntos()) == {0, 1}
    label, votes = etiquetar_fila(np.array([0.5, 0.5], dtype=np.float32), hoja)
    assert votes[0] == VOTE_SOLO_A
    assert votes[1] == VOTE_SOLO_B
    assert label == "split"


def test_empty_disjoint_is_out() -> None:
    votos = np.array([VOTE_SOLO_A, VOTE_SOLO_A], dtype=np.uint8)
    assert evaluar_corte_duro(votos, []) == "out"
    assert evaluar_corte_duro(np.array([VOTE_NINGUNA], dtype=np.uint8), [0]) == "out"
    assert evaluar_corte_duro(np.array([VOTE_AMBAS], dtype=np.uint8), [0]) == "out"

"""D02 — hoja dimensional con matrices sintéticas. Sin medias."""

from __future__ import annotations

import numpy as np

from ddi_fw.hoja import (
    calcular_hoja,
    obtener_ejes_disjuntos,
    podar_hasta_publicar,
    publicar_candado,
)


def test_hoja_detects_disjoint_axis_in_3d() -> None:
    alma_a = np.array([[0.0, 0.0, 5.0], [1.0, 1.0, 6.0]], dtype=np.float32)
    alma_b = np.array([[10.0, 0.5, 5.5], [11.0, 0.8, 5.8]], dtype=np.float32)
    hoja = calcular_hoja(alma_a, alma_b, "python", "receta")
    assert hoja.dimension == 3
    assert obtener_ejes_disjuntos(hoja) == [0]
    assert hoja.gap[0] > 0
    assert hoja.gap[1] <= 0
    assert hoja.gap[2] <= 0
    assert "mean" not in hoja.__dataclass_fields__
    assert publicar_candado(hoja).published is True


def test_touching_intervals_are_not_disjoint() -> None:
    alma_a = np.array([[0.0], [1.0]], dtype=np.float32)
    alma_b = np.array([[1.0], [2.0]], dtype=np.float32)
    hoja = calcular_hoja(alma_a, alma_b)
    assert hoja.gap[0] == 0
    assert obtener_ejes_disjuntos(hoja) == []
    assert publicar_candado(hoja).published is False


def test_prune_removes_bridging_row() -> None:
    python = np.array([[0.0, 0.0], [1.0, 1.0], [8.5, 0.5]], dtype=np.float32)
    receta = np.array([[8.0, 0.2], [9.0, 0.8]], dtype=np.float32)
    legal = np.array([[0.2, 20.0], [0.8, 21.0]], dtype=np.float32)
    matrices = {"python": python, "receta": receta, "legal": legal}
    ids = {
        "python": ["p0", "p1", "bridge"],
        "receta": ["r0", "r1"],
        "legal": ["l0", "l1"],
    }
    pruned, pruned_ids, dropped = podar_hasta_publicar(matrices, ids, min_n=2)
    assert "bridge" in dropped
    assert "bridge" not in pruned_ids["python"]
    assert pruned["python"].shape[0] == 2

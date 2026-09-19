"""Corte duro y votación por eje. Sin coseno. Sin medias."""

from __future__ import annotations

from typing import Literal

import numpy as np
import numpy.typing as npt

from ddi_fw.hoja import HojaDimensional

Vote = np.uint8
Label = Literal["left", "right", "split", "out"]

VOTE_NINGUNA = 0
VOTE_SOLO_A = 1
VOTE_SOLO_B = 2
VOTE_AMBAS = 3

VOTE_NAMES = {
    VOTE_NINGUNA: "ninguna",
    VOTE_SOLO_A: "solo_a",
    VOTE_SOLO_B: "solo_b",
    VOTE_AMBAS: "ambas",
}


def votar_coordenadas(
    valores: npt.NDArray[np.floating],
    lo_a: npt.NDArray[np.floating],
    hi_a: npt.NDArray[np.floating],
    lo_b: npt.NDArray[np.floating],
    hi_b: npt.NDArray[np.floating],
) -> npt.NDArray[np.uint8]:
    in_a = (valores >= lo_a) & (valores <= hi_a)
    in_b = (valores >= lo_b) & (valores <= hi_b)
    votes = np.full(valores.shape, VOTE_NINGUNA, dtype=np.uint8)
    votes[in_a & ~in_b] = VOTE_SOLO_A
    votes[~in_a & in_b] = VOTE_SOLO_B
    votes[in_a & in_b] = VOTE_AMBAS
    return votes


def votar_vector(vector: npt.NDArray[np.floating], hoja: HojaDimensional) -> npt.NDArray[np.uint8]:
    values = np.asarray(vector, dtype=np.float32).reshape(-1)
    if values.shape[0] != hoja.dimension:
        raise ValueError(f"dimensión {values.shape[0]} != hoja {hoja.dimension}")
    return votar_coordenadas(values, hoja.lo_a, hoja.hi_a, hoja.lo_b, hoja.hi_b)


def recuento_votos(votos: npt.NDArray[np.uint8]) -> dict[str, int]:
    return {
        "ninguna": int(np.count_nonzero(votos == VOTE_NINGUNA)),
        "solo_a": int(np.count_nonzero(votos == VOTE_SOLO_A)),
        "solo_b": int(np.count_nonzero(votos == VOTE_SOLO_B)),
        "ambas": int(np.count_nonzero(votos == VOTE_AMBAS)),
    }


def evaluar_corte_duro(
    votos: npt.NDArray[np.uint8],
    ejes_disjuntos: list[int],
) -> Label:
    if not ejes_disjuntos:
        return "out"
    subset = np.asarray(votos, dtype=np.uint8)[np.asarray(ejes_disjuntos, dtype=int)]
    if np.any((subset == VOTE_NINGUNA) | (subset == VOTE_AMBAS)):
        return "out"
    only_a = bool(np.all(subset == VOTE_SOLO_A))
    only_b = bool(np.all(subset == VOTE_SOLO_B))
    if only_a:
        return "left"
    if only_b:
        return "right"
    return "split"


def etiquetar_fila(
    vector: npt.NDArray[np.floating], hoja: HojaDimensional
) -> tuple[Label, npt.NDArray[np.uint8]]:
    votos = votar_vector(vector, hoja)
    return evaluar_corte_duro(votos, hoja.ejes_disjuntos()), votos

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


def evaluar_corte_espectral(
    votos: npt.NDArray[np.uint8],
    ejes_trigo: list[int] | None = None,
    quorum_min: int | None = None,
    paja_indices: list[int] | None = None,
) -> tuple[Label, dict[str, int]]:
    """Evalúa la disyunción mediante el Quórum del 10% y poda de paja estructural.

    - Poda de paja: Ignora dimensiones contaminadas con ruido basal o planas.
    - Quórum del 10%: Requiere al menos quorum_min votos concordantes en trigo.
    - Garantía anti-bypass: P_bypass <= (0.80)^K (< 10^-9 con K >= 100).
    """
    total_dims = len(votos)
    paja_set = set(paja_indices or ())

    if ejes_trigo is not None:
        ejes = [idx for idx in ejes_trigo if 0 <= idx < total_dims and idx not in paja_set]
    else:
        ejes = [idx for idx in range(total_dims) if idx not in paja_set]

    quorum = quorum_min if quorum_min is not None else max(int(np.ceil(0.10 * total_dims)), 1)

    if len(ejes) < quorum:
        metrics = {
            "votos_trigo_a": 0,
            "votos_trigo_b": 0,
            "votos_trigo_ninguna": 0,
            "votos_trigo_ambas": 0,
            "quorum_min": quorum,
            "total_trigo": len(ejes),
        }
        return "out", metrics

    subset = np.asarray(votos, dtype=np.uint8)[np.asarray(ejes, dtype=int)]
    votos_a = int(np.count_nonzero(subset == VOTE_SOLO_A))
    votos_b = int(np.count_nonzero(subset == VOTE_SOLO_B))
    votos_ninguna = int(np.count_nonzero(subset == VOTE_NINGUNA))
    votos_ambas = int(np.count_nonzero(subset == VOTE_AMBAS))

    metrics = {
        "votos_trigo_a": votos_a,
        "votos_trigo_b": votos_b,
        "votos_trigo_ninguna": votos_ninguna,
        "votos_trigo_ambas": votos_ambas,
        "quorum_min": quorum,
        "total_trigo": len(ejes),
    }

    if votos_a >= quorum and votos_b < quorum:
        return "left", metrics
    if votos_b >= quorum and votos_a < quorum:
        return "right", metrics
    if votos_a >= quorum and votos_b >= quorum:
        return "split", metrics
    return "out", metrics


def etiquetar_fila(
    vector: npt.NDArray[np.floating],
    hoja: HojaDimensional,
    modo: Literal["auto", "espectral", "duro"] = "auto",
) -> tuple[Label, npt.NDArray[np.uint8]]:
    """Etiqueta un vector contra una hoja dimensional.

    En modo 'auto' utiliza corte espectral si la hoja tiene configuración
    espectral (trigo_indices o quorum_min), y preserva corte duro en caso contrario.
    """
    votos = votar_vector(vector, hoja)
    is_spectral = getattr(hoja, "is_spectral", False)
    if modo == "espectral" or (modo == "auto" and is_spectral):
        ejes = hoja.ejes_trigo() if hasattr(hoja, "ejes_trigo") else hoja.ejes_disjuntos()
        quorum = getattr(hoja, "quorum_min", None)
        paja = getattr(hoja, "paja_indices", None)
        label, _ = evaluar_corte_espectral(votos, ejes_trigo=ejes, quorum_min=quorum, paja_indices=paja)
        return label, votos
    return evaluar_corte_duro(votos, hoja.ejes_disjuntos()), votos

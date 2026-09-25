"""Hoja dimensional: intervalos [lo, hi], gap y ejes disjuntos. Sin medias."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float32]
BoolArray = npt.NDArray[np.bool_]

CANONICAL_PAIRS: tuple[tuple[str, str], ...] = (
    ("python", "receta"),
    ("python", "legal"),
    ("legal", "receta"),
    ("python", "medicina"),
    ("python", "astronomia"),
    ("legal", "medicina"),
    ("legal", "astronomia"),
    ("receta", "medicina"),
    ("receta", "astronomia"),
    ("medicina", "astronomia"),
)


RUIDO_UNIVERSAL_BGE_M3: tuple[int, ...] = (292, 297, 308, 386, 404, 577, 780, 329, 616)
PAJA_UNIVERSAL_BGE_M3 = RUIDO_UNIVERSAL_BGE_M3  # Deprecated alias


def pair_id(alma_a: str, alma_b: str) -> str:
    return f"{alma_a}_{alma_b}"


@dataclass(frozen=True)
class HojaDimensional:
    alma_a: str
    alma_b: str
    lo_a: FloatArray
    hi_a: FloatArray
    lo_b: FloatArray
    hi_b: FloatArray
    gap: FloatArray
    disjoint: BoolArray
    trigo_indices: tuple[int, ...] | None = None
    ruido_indices: tuple[int, ...] | None = None
    quorum_min: int | None = None

    @property
    def dimension(self) -> int:
        return int(self.lo_a.shape[0])

    @property
    def pair_id(self) -> str:
        return pair_id(self.alma_a, self.alma_b)

    @property
    def is_spectral(self) -> bool:
        return self.trigo_indices is not None or self.quorum_min is not None

    @property
    def paja_indices(self) -> tuple[int, ...] | None:
        return self.ruido_indices

    def ejes_disjuntos(self) -> list[int]:
        return np.flatnonzero(self.disjoint).astype(int).tolist()

    def ejes_trigo(self) -> list[int]:
        if self.trigo_indices is not None:
            return list(self.trigo_indices)
        return self.ejes_disjuntos()


@dataclass(frozen=True)
class Candado:
    hoja: HojaDimensional

    @property
    def pair_id(self) -> str:
        return self.hoja.pair_id

    @property
    def is_spectral(self) -> bool:
        return self.hoja.is_spectral

    @property
    def quorum_min(self) -> int:
        if self.hoja.quorum_min is not None:
            return self.hoja.quorum_min
        return max(int(np.ceil(0.10 * self.hoja.dimension)), 1)

    @property
    def published(self) -> bool:
        if self.is_spectral:
            return len(self.hoja.ejes_trigo()) >= self.quorum_min
        return bool(np.any(self.hoja.disjoint))

    @property
    def paja_indices(self) -> tuple[int, ...] | None:
        return self.hoja.paja_indices

    @property
    def ruido_indices(self) -> tuple[int, ...] | None:
        return self.hoja.ruido_indices

    @property
    def ejes_disjuntos(self) -> list[int]:
        return self.hoja.ejes_disjuntos()

    @property
    def ejes_trigo(self) -> list[int]:
        return self.hoja.ejes_trigo()

    @property
    def disjoint_count(self) -> int:
        if self.is_spectral:
            return len(self.hoja.ejes_trigo())
        return int(np.count_nonzero(self.hoja.disjoint))


def _as_matrix(matriz: npt.NDArray[np.floating], name: str) -> FloatArray:
    array = np.asarray(matriz, dtype=np.float32)
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 1:
        raise ValueError(f"{name} debe ser una matriz (n, dim) no vacía")
    return array


def calcular_brecha(
    lo_a: FloatArray, hi_a: FloatArray, lo_b: FloatArray, hi_b: FloatArray
) -> FloatArray:
    """gap > 0 si los intervalos no se tocan. Si se solapan, gap es el ancho negativo."""
    a_below_b = hi_a < lo_b
    b_below_a = hi_b < lo_a
    overlap = np.minimum(hi_a, hi_b) - np.maximum(lo_a, lo_b)
    return np.where(
        a_below_b,
        lo_b - hi_a,
        np.where(b_below_a, lo_a - hi_b, -overlap),
    ).astype(np.float32)


def calcular_hoja(
    matriz_a: npt.NDArray[np.floating],
    matriz_b: npt.NDArray[np.floating],
    alma_a: str = "a",
    alma_b: str = "b",
    trigo_indices: list[int] | tuple[int, ...] | None = None,
    ruido_indices: list[int] | tuple[int, ...] | None = None,
    quorum_min: int | None = None,
    quorum_ratio: float = 0.10,
    modo_espectral: bool = False,
) -> HojaDimensional:
    rows_a = _as_matrix(matriz_a, "matriz_a")
    rows_b = _as_matrix(matriz_b, "matriz_b")
    if rows_a.shape[1] != rows_b.shape[1]:
        raise ValueError("las almas deben compartir dimensión")
    dim = rows_a.shape[1]
    lo_a = rows_a.min(axis=0)
    hi_a = rows_a.max(axis=0)
    lo_b = rows_b.min(axis=0)
    hi_b = rows_b.max(axis=0)
    gap = calcular_brecha(lo_a, hi_a, lo_b, hi_b)
    disjoint = gap > 0

    ruido_tup = tuple(ruido_indices) if ruido_indices is not None else None
    trigo_tup = tuple(trigo_indices) if trigo_indices is not None else None
    q_min = quorum_min

    if modo_espectral or trigo_tup is not None or ruido_tup is not None or q_min is not None:
        if q_min is None:
            q_min = max(int(np.ceil(quorum_ratio * dim)), 1)
        if trigo_tup is None:
            ruido_set = set(ruido_tup or ())
            trigo_tup = tuple(i for i in range(dim) if i not in ruido_set)

    return HojaDimensional(
        alma_a=alma_a,
        alma_b=alma_b,
        lo_a=lo_a,
        hi_a=hi_a,
        lo_b=lo_b,
        hi_b=hi_b,
        gap=gap,
        disjoint=disjoint,
        trigo_indices=trigo_tup,
        ruido_indices=ruido_tup,
        quorum_min=q_min,
    )


def obtener_ejes_disjuntos(hoja: HojaDimensional) -> list[int]:
    return hoja.ejes_disjuntos()


def publicar_candado(hoja: HojaDimensional) -> Candado:
    return Candado(hoja=hoja)


def candados_canonicos(
    matrices: dict[str, npt.NDArray[np.floating]],
    pairs: list[tuple[str, str]] | tuple[tuple[str, str], ...] | None = None,
    ruido_indices: list[int] | tuple[int, ...] | None = None,
    modo_espectral: bool = False,
    quorum_ratio: float = 0.10,
) -> dict[str, Candado]:
    locks: dict[str, Candado] = {}
    names = list(matrices.keys())
    if pairs is not None:
        active_pairs = pairs
    elif len(names) <= 5 and all(
        a in {p[0] for p in CANONICAL_PAIRS} | {p[1] for p in CANONICAL_PAIRS} for a in names
    ):
        active_pairs = [p for p in CANONICAL_PAIRS if p[0] in matrices and p[1] in matrices]
    else:
        import itertools

        active_pairs = list(itertools.combinations(names, 2))

    for alma_a, alma_b in active_pairs:
        if alma_a not in matrices or alma_b not in matrices:
            continue
        hoja = calcular_hoja(
            matrices[alma_a],
            matrices[alma_b],
            alma_a,
            alma_b,
            ruido_indices=ruido_indices,
            modo_espectral=modo_espectral,
            quorum_ratio=quorum_ratio,
        )
        locks[pair_id(alma_a, alma_b)] = publicar_candado(hoja)
    return locks


def _disjoint_score(matrices: dict[str, npt.NDArray[np.floating]]) -> tuple[int, int]:
    published = 0
    total_disjoint = 0
    for candado in candados_canonicos(matrices).values():
        total_disjoint += candado.disjoint_count
        published += int(candado.published)
    return published, total_disjoint


def podar_hasta_publicar(
    matrices: dict[str, npt.NDArray[np.floating]],
    ids: dict[str, list[str]],
    min_n: int = 8,
) -> tuple[dict[str, FloatArray], dict[str, list[str]], list[str]]:
    """Quita filas (nunca holgura de gap) hasta publicar los pares canónicos aplicables o agotar el mazo."""
    applicable = [(a, b) for a, b in CANONICAL_PAIRS if a in matrices and b in matrices]
    current = {name: np.asarray(rows, dtype=np.float32).copy() for name, rows in matrices.items()}
    current_ids = {name: list(values) for name, values in ids.items()}
    dropped: list[str] = []

    while True:
        published, total = _disjoint_score(current)
        if published == len(applicable):
            return current, current_ids, dropped

        best: tuple[int, int, str, int] | None = None
        for alma, rows in current.items():
            if rows.shape[0] <= min_n:
                continue
            for index in range(rows.shape[0]):
                trial = {name: value for name, value in current.items()}
                trial[alma] = np.delete(rows, index, axis=0)
                score = _disjoint_score(trial)
                candidate = (score[0], score[1], alma, index)
                if best is None or candidate[:2] > best[:2]:
                    best = candidate

        if best is None or (best[0], best[1]) <= (published, total):
            return current, current_ids, dropped

        alma, index = best[2], best[3]
        dropped.append(current_ids[alma][index])
        current[alma] = np.delete(current[alma], index, axis=0)
        del current_ids[alma][index]

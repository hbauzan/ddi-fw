"""Mundo sintético 3D compartido por ingress, egreso y proxy."""

from __future__ import annotations

import numpy as np

from ddi_fw.embedder import FakeEmbedder
from ddi_fw.hoja import candados_canonicos

PY = "Explicá el funcionamiento de list.append en Python."
LEGAL = "Copiá el texto de la licencia MIT."
RECETA = "Anotá los ingredientes de la receta de la torta de chocolate."
PIGGYBACK = f"{PY} {LEGAL} {RECETA}"
PYTHON_ONLY = f"{PY} El bucle for recorre una lista en Python."
PYTHON_PLUS_RECIPE = f"{PY} Hornear el bizcochuelo a 180 grados con 200 gramos de harina."
PYTHON_ANSWER = "list.append agrega un elemento al final de la lista en Python."
RECIPE_ANSWER = "Hornear el bizcochuelo a 180 grados con 200 gramos de harina."


def synthetic_locks():
    python = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32)
    receta = np.array([[10.0, 0.0, 0.0], [11.0, 1.0, 1.0]], dtype=np.float32)
    legal = np.array([[0.0, 10.0, 0.0], [1.0, 11.0, 1.0]], dtype=np.float32)
    return candados_canonicos({"python": python, "legal": legal, "receta": receta})


def synthetic_embedder() -> FakeEmbedder:
    python_vec = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    legal_vec = np.array([0.5, 10.5, 0.5], dtype=np.float32)
    receta_vec = np.array([10.5, 0.5, 0.5], dtype=np.float32)
    table = {
        PY: python_vec,
        LEGAL: legal_vec,
        RECETA: receta_vec,
        "El bucle for recorre una lista en Python.": python_vec,
        PYTHON_ANSWER: python_vec,
        RECIPE_ANSWER: receta_vec,
        "Hornear el bizcochuelo a 180 grados con 200 gramos de harina.": receta_vec,
    }
    return FakeEmbedder(dimension=3, table=table)

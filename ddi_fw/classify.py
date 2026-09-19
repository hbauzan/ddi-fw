"""Clasificador textual auditable. Cero embeddings. Cero regex de 'similitud'."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Label = Literal["python", "legal", "receta", "lomo_descarte"]

LOMO_MARKERS = (
    "toctree",
    "table of contents",
    "tabla de contenidos",
    "changelog",
    "what's new",
    "release notes",
    "notas de la versión",
    "previous next",
    "next previous",
    "breadcrumb",
    "índice general",
    "footer navigation",
    "spdx license list",
    "tabla nutricional",
    "información nutricional",
    "nutrition facts",
    "calorías por porción",
)

PYTHON_VETO = (
    "ssl",
    "tls",
    "cryptography",
    "criptografía",
    "hashlib",
    "fernet",
    "exploit",
    "explotación",
    "penetración",
    "penetration test",
    "pentest",
    "buffer overflow",
    "shellcode",
    "payload malicioso",
)

LEGAL_VETO = (
    "privacy policy",
    "política de privacidad",
    "employment agreement",
    "contrato laboral",
    "criminal",
    "penal",
    "terms of service",
    "términos de servicio",
    "terms of use",
)

PYTHON_CUES = (
    "python",
    "list.append",
    "lista",
    "diccionario",
    "dict",
    "tupla",
    "tuple",
    "def ",
    "función",
    "funcion",
    "except ",
    "excepción",
    "excepcion",
    "for loop",
    "bucle",
    "import ",
    "slicing",
    "slice",
    "none",
    "classmethod",
    "indentación",
    "indentacion",
    "módulo",
    "modulo",
)

LEGAL_CUES = (
    "copyright",
    "license",
    "licencia",
    "permission is hereby granted",
    "without warranty",
    "as is",
    "redistribution",
    "redistribución",
    "redistribucion",
    "spdx",
    "apache license",
    "mit license",
    "bsd",
    "disclaimer",
    "exención de responsabilidad",
    "exencion de responsabilidad",
    "copyright holders",
    "liable",
    "merchantability",
)

RECETA_CUES = (
    "harina",
    "azúcar",
    "azucar",
    "huevo",
    "clara",
    "yema",
    "hornear",
    "horno",
    "batir",
    "amasar",
    "gramos",
    "cucharada",
    "sartén",
    "sarten",
    "saltear",
    "ingrediente",
    "precalentar",
    "masa",
    "levadura",
    "aceite de oliva",
    "punto nieve",
    "bizcochuelo",
    "salsa",
)


@dataclass(frozen=True)
class Classification:
    label: Label
    reason: str


def _contains_any(text: str, markers: tuple[str, ...]) -> str | None:
    lowered = text.casefold()
    for marker in markers:
        if marker.casefold() in lowered:
            return marker
    return None


def _score(text: str, cues: tuple[str, ...]) -> int:
    lowered = text.casefold()
    return sum(1 for cue in cues if cue.casefold() in lowered)


def classify_clause(text: str) -> Classification:
    """Asigna etiqueta explícita o descarta lomo/veto. Determinista."""
    stripped = text.strip()
    if not stripped:
        return Classification("lomo_descarte", "empty")

    lomo = _contains_any(stripped, LOMO_MARKERS)
    if lomo:
        return Classification("lomo_descarte", f"editorial:{lomo}")

    python_veto = _contains_any(stripped, PYTHON_VETO)
    if python_veto:
        return Classification("lomo_descarte", f"veto_python:{python_veto}")

    legal_veto = _contains_any(stripped, LEGAL_VETO)
    if legal_veto:
        return Classification("lomo_descarte", f"veto_legal:{legal_veto}")

    py_score = _score(stripped, PYTHON_CUES)
    legal_score = _score(stripped, LEGAL_CUES)
    receta_score = _score(stripped, RECETA_CUES)

    if py_score > 0 and receta_score > 0:
        return Classification("lomo_descarte", "veto_receta:mezcla_programacion_cocina")

    ranked = (
        ("python", py_score),
        ("legal", legal_score),
        ("receta", receta_score),
    )
    ranked = tuple(sorted(ranked, key=lambda item: item[1], reverse=True))
    winner, win_score = ranked[0]
    runner_up = ranked[1][1]
    if win_score == 0 or win_score == runner_up:
        return Classification("lomo_descarte", "ambiguous_or_empty_cues")
    return Classification(winner, f"cues:{winner}={win_score}")

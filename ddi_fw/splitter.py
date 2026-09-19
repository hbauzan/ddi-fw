"""Segmentador determinista de cláusulas. Protege decimales 0.8 y 1,4."""

from __future__ import annotations

import re
from dataclasses import dataclass

_DECIMAL = re.compile(r"\d+[.,]\d+")
_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


@dataclass(frozen=True)
class ClauseSplitter:
    """Corta por puntuación terminal y saltos de línea, sin romper números."""

    def split(self, text: str) -> list[str]:
        if text is None:
            raise ValueError("texto nulo")
        stripped = text.strip()
        if not stripped:
            return []
        tokens: list[str] = []

        def stash(match: re.Match[str]) -> str:
            tokens.append(match.group(0))
            return f"\x00{len(tokens) - 1}\x00"

        protected = _DECIMAL.sub(stash, stripped)
        parts = _SPLIT.split(protected)
        clauses: list[str] = []
        for part in parts:
            restored = part
            for index, token in enumerate(tokens):
                restored = restored.replace(f"\x00{index}\x00", token)
            clause = restored.strip()
            if clause:
                clauses.append(clause)
        return clauses


def split_clauses(text: str) -> list[str]:
    return ClauseSplitter().split(text)

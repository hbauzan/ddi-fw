"""Egreso hold: retención total. Cero yield de tokens."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from ddi_fw.ingress import Decision, IngressResult
from ddi_fw.splitter import split_clauses

HoldStatus = Literal["DELIVERED", "BLOCKED"]


@dataclass(frozen=True)
class HoldResult:
    status: HoldStatus
    text: str
    decisions: tuple[Decision, ...] = ()
    reason: str = ""

    @property
    def delivered(self) -> bool:
        return self.status == "DELIVERED"


def hold(
    texto_generado: str,
    decide_fn: Callable[[str], Decision],
    splitter=split_clauses,
) -> HoldResult:
    """Evalúa todas las cláusulas antes de devolver texto. No emite fragmentos."""
    if texto_generado is None or not str(texto_generado).strip():
        return HoldResult(status="BLOCKED", text="", reason="empty_generation")
    try:
        clauses = splitter(texto_generado)
    except Exception as exc:  # noqa: BLE001
        return HoldResult(status="BLOCKED", text="", reason=f"parse_error:{exc}")
    if not clauses:
        return HoldResult(status="BLOCKED", text="", reason="empty_clauses")
    decisions: list[Decision] = []
    for clause in clauses:
        decision = decide_fn(clause)
        decision.clause = clause
        decisions.append(decision)
        if decision.verdict == "BREACH":
            return HoldResult(
                status="BLOCKED",
                text="",
                decisions=tuple(decisions),
                reason="clause_breach",
            )
    return HoldResult(
        status="DELIVERED",
        text=texto_generado,
        decisions=tuple(decisions),
        reason="all_allowed",
    )


def hold_from_ingress(result: IngressResult, texto_generado: str) -> HoldResult:
    if result.verdict == "BREACH":
        return HoldResult(
            status="BLOCKED",
            text="",
            decisions=tuple(result.decisions),
            reason=result.reason,
        )
    return HoldResult(
        status="DELIVERED",
        text=texto_generado,
        decisions=tuple(result.decisions),
        reason=result.reason,
    )

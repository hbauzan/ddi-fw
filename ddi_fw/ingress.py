"""Ingress fail-closed: una cláusula BREACH tumba el prompt entero."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import numpy.typing as npt

from ddi_fw.corte import etiquetar_fila, recuento_votos
from ddi_fw.embedder import BaseEmbedder
from ddi_fw.hoja import Candado
from ddi_fw.splitter import split_clauses

Verdict = Literal["PASS", "BREACH"]


@dataclass(frozen=True)
class Policy:
    allowed: str
    forbidden: frozenset[str]

    @classmethod
    def demo(cls) -> Policy:
        return cls(allowed="python", forbidden=frozenset({"receta", "legal"}))


@dataclass
class Decision:
    verdict: Verdict
    alma_asignada: str | None
    pair_labels: dict[str, str]
    vote_counts: dict[str, int]
    disjoint_count: int
    published: bool
    reason: str
    clause: str | None = None
    spectral_metrics: dict[str, Any] | None = None


@dataclass
class IngressResult:
    verdict: Verdict
    decisions: list[Decision] = field(default_factory=list)
    reason: str = ""

    @property
    def audit(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for decision in self.decisions:
            row: dict[str, object] = {
                "verdict": decision.verdict,
                "alma_asignada": decision.alma_asignada,
                "pair_labels": decision.pair_labels,
                "vote_counts": decision.vote_counts,
                "disjoint_count": decision.disjoint_count,
                "published": decision.published,
                "reason": decision.reason,
            }
            if decision.spectral_metrics is not None:
                row["spectral_metrics"] = decision.spectral_metrics
            rows.append(row)
        return rows


def _alma_from_label(candado: Candado, label: str) -> str | None:
    if label == "left":
        return candado.hoja.alma_a
    if label == "right":
        return candado.hoja.alma_b
    return None


def decide(
    vector: npt.NDArray[np.floating],
    candados: dict[str, Candado],
    politica: Policy,
) -> Decision:
    required = [
        candado
        for candado in candados.values()
        if politica.allowed in {candado.hoja.alma_a, candado.hoja.alma_b}
    ]
    if not required:
        return Decision(
            verdict="BREACH",
            alma_asignada=None,
            pair_labels={},
            vote_counts={},
            disjoint_count=0,
            published=False,
            reason="no_required_locks",
        )

    pair_labels: dict[str, str] = {}
    assigned: list[str] = []
    vote_counts: dict[str, int] = {}
    spectral_metrics: dict[str, Any] = {}
    disjoint_total = 0
    for candado in required:
        if not candado.published:
            return Decision(
                verdict="BREACH",
                alma_asignada=None,
                pair_labels=pair_labels,
                vote_counts={},
                disjoint_count=0,
                published=False,
                reason=f"unpublished:{candado.pair_id}",
            )
        label, votos = etiquetar_fila(vector, candado.hoja)
        pair_labels[candado.pair_id] = label
        disjoint_total += candado.disjoint_count
        if not vote_counts:
            vote_counts = recuento_votos(votos)

        if candado.is_spectral:
            from ddi_fw.corte import evaluar_corte_espectral

            _, met = evaluar_corte_espectral(
                votos,
                ejes_trigo=candado.ejes_trigo,
                quorum_min=candado.quorum_min,
                ruido_indices=candado.hoja.ruido_indices,
            )
            spectral_metrics[candado.pair_id] = met

        if label in {"split", "out"}:
            return Decision(
                verdict="BREACH",
                alma_asignada=None,
                pair_labels=pair_labels,
                vote_counts=vote_counts,
                disjoint_count=disjoint_total,
                published=True,
                reason=f"cut:{candado.pair_id}:{label}",
                spectral_metrics=spectral_metrics or None,
            )
        alma = _alma_from_label(candado, label)
        if alma is None:
            return Decision(
                verdict="BREACH",
                alma_asignada=None,
                pair_labels=pair_labels,
                vote_counts=vote_counts,
                disjoint_count=disjoint_total,
                published=True,
                reason="unassigned",
                spectral_metrics=spectral_metrics or None,
            )
        assigned.append(alma)

    forbidden_hit = next((alma for alma in assigned if alma in politica.forbidden), None)
    if forbidden_hit is not None:
        return Decision(
            verdict="BREACH",
            alma_asignada=forbidden_hit,
            pair_labels=pair_labels,
            vote_counts=vote_counts,
            disjoint_count=disjoint_total,
            published=True,
            reason=f"forbidden:{forbidden_hit}",
            spectral_metrics=spectral_metrics or None,
        )
    if assigned and all(alma == politica.allowed for alma in assigned):
        return Decision(
            verdict="PASS",
            alma_asignada=politica.allowed,
            pair_labels=pair_labels,
            vote_counts=vote_counts,
            disjoint_count=disjoint_total,
            published=True,
            reason="allowed",
            spectral_metrics=spectral_metrics or None,
        )
    return Decision(
        verdict="BREACH",
        alma_asignada=assigned[0] if assigned else None,
        pair_labels=pair_labels,
        vote_counts=vote_counts,
        disjoint_count=disjoint_total,
        published=True,
        reason="contradictory_pairs",
        spectral_metrics=spectral_metrics or None,
    )


def inspect_prompt(
    texto: str,
    embedder: BaseEmbedder,
    candados: dict[str, Candado],
    politica: Policy | None = None,
    splitter=split_clauses,
) -> IngressResult:
    policy = politica or Policy.demo()
    try:
        clauses = splitter(texto)
    except Exception as exc:  # noqa: BLE001 — fail-closed
        return IngressResult(verdict="BREACH", reason=f"parse_error:{exc}")
    if not clauses:
        return IngressResult(verdict="BREACH", reason="empty_clauses")
    try:
        vectors = embedder.embed_batch(clauses)
    except Exception as exc:  # noqa: BLE001 — fail-closed
        return IngressResult(verdict="BREACH", reason=f"embedder_down:{exc}")
    decisions: list[Decision] = []
    for clause, vector in zip(clauses, vectors, strict=True):
        decision = decide(vector, candados, policy)
        decision.clause = clause
        decisions.append(decision)
    if any(item.verdict == "BREACH" for item in decisions):
        return IngressResult(verdict="BREACH", decisions=decisions, reason="clause_breach")
    return IngressResult(verdict="PASS", decisions=decisions, reason="all_allowed")

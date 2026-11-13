"""Señales cinemáticas por turno: ancla, velocidad, memoria negativa y contaminación."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ddi_fw.lab_v2.ast_symbol_index import AstViolation
from ddi_fw.lab_v2.models import ledoit_wolf_covariance


@dataclass(frozen=True)
class NegativeMemoryEntry:
    turn_id: int
    reason: str
    whitened_vec: np.ndarray
    ast_hashes: frozenset[str]


@dataclass(frozen=True)
class TurnAlert:
    kind: str
    turn_id: int
    detail: str
    symbol: str | None = None
    related_turn: int | None = None


def compute_context_pollution(
    total_tokens: int,
    superseded_tokens: int,
    stale_trace_tokens: int,
) -> float:
    """H_ctx: bloques sobrescritos y trazas viejas sobre el historial acumulado."""
    if total_tokens < 0 or superseded_tokens < 0 or stale_trace_tokens < 0:
        raise ValueError("los conteos de contaminación no pueden ser negativos")
    return float(superseded_tokens + stale_trace_tokens) / float(max(1, total_tokens))


class TrajectoryMonitor:
    """Compara un modo `raw_cosine` contra un modo `whitened` con la misma interfaz."""

    def __init__(
        self,
        anchor: np.ndarray,
        *,
        mode: str = "whitened",
        reference: np.ndarray | None = None,
        anchor_floor: float = 0.75,
    ) -> None:
        if mode not in {"raw_cosine", "whitened"}:
            raise ValueError(f"modo desconocido: {mode}")
        if not  -1.0 <= anchor_floor <= 1.0:
            raise ValueError("anchor_floor debe estar en [-1, 1]")
        anchor_vec = np.asarray(anchor, dtype=np.float64).reshape(-1)
        if mode == "raw_cosine" or reference is None or np.asarray(reference).shape[0] < 2:
            self.mu = np.zeros(anchor_vec.shape[0], dtype=np.float64)
            self.transform = np.eye(anchor_vec.shape[0], dtype=np.float64)
        else:
            mu, cov, _shrinkage = ledoit_wolf_covariance(np.asarray(reference, dtype=np.float64))
            if mu.shape[0] != anchor_vec.shape[0]:
                raise ValueError("el ancla y la referencia no comparten dimensión")
            self.mu = mu
            self.transform = _inv_sqrt(cov)
        self.mode = mode
        self.anchor_floor = float(anchor_floor)
        self.anchor = project_vector(anchor_vec, self.mu, self.transform)
        self.memory: list[NegativeMemoryEntry] = []
        self._previous: np.ndarray | None = None
        self._low_alpha_streak = 0
        self._previous_failed = False

    def evaluate_turn(
        self,
        *,
        turn_id: int,
        vector: np.ndarray,
        accepted: bool,
        ast_violations: list[AstViolation],
        ast_hashes: set[str] | frozenset[str],
        pollution: float,
        failure_reason: str = "",
    ) -> list[TurnAlert]:
        if not 0.0 <= pollution <= 1.0:
            raise ValueError(f"pollution fuera de [0, 1]: {pollution}")
        current = project_vector(vector, self.mu, self.transform)
        alpha = _alignment(current, self.anchor)
        nu = 1.0 if self._previous is None else float(np.linalg.norm(current - self._previous))
        rho = 0.0
        if self.memory:
            rho = max(float(np.dot(current, entry.whitened_vec)) for entry in self.memory)
        failed_hashes: set[str] = set()
        for entry in self.memory:
            failed_hashes.update(entry.ast_hashes)
        exact_ast_loop = bool(set(ast_hashes) & failed_hashes)
        alerts: list[TurnAlert] = []
        if ast_violations:
            first = ast_violations[0]
            alerts.append(
                TurnAlert(
                    kind="AST_CONTRACT_BREACH",
                    turn_id=turn_id,
                    detail=first.detail,
                    symbol=first.symbol,
                    related_turn=first.deprecated_from_turn,
                )
            )
        if exact_ast_loop or rho >= 0.90:
            related = self.memory[-1].turn_id if self.memory else None
            alerts.append(
                TurnAlert(
                    kind="THRASHING_LOOP_DETECTED",
                    turn_id=turn_id,
                    detail="el turno repite un parche ya rechazado",
                    related_turn=related,
                )
            )
        if alpha < self.anchor_floor:
            self._low_alpha_streak += 1
        else:
            self._low_alpha_streak = 0
        if self._low_alpha_streak >= 2:
            alerts.append(
                TurnAlert(
                    kind="GOAL_DRIFT_DETECTED",
                    turn_id=turn_id,
                    detail="la alineación con el ancla estuvo bajo el piso dos turnos seguidos",
                )
            )
        if self._previous_failed and nu < 0.05:
            alerts.append(
                TurnAlert(
                    kind="COSMETIC_STAGNATION",
                    turn_id=turn_id,
                    detail="el paso semántico quedó por debajo de 0.05 después de un rechazo",
                )
            )
        if not accepted:
            self.memory.append(
                NegativeMemoryEntry(
                    turn_id=turn_id,
                    reason=failure_reason or "rejected",
                    whitened_vec=current,
                    ast_hashes=frozenset(ast_hashes),
                )
            )
        self._previous = current
        self._previous_failed = not accepted
        return alerts


def _alignment(current: np.ndarray, anchor: np.ndarray) -> float:
    """Dos vectores nulos están en el centro de la referencia: siguen sobre el ancla."""
    if float(np.linalg.norm(current)) < 1e-8 and float(np.linalg.norm(anchor)) < 1e-8:
        return 1.0
    return float(np.dot(current, anchor))


def project_vector(vector: np.ndarray, mu: np.ndarray, transform: np.ndarray) -> np.ndarray:
    array = np.asarray(vector, dtype=np.float64).reshape(-1)
    if array.shape[0] != mu.shape[0] or transform.shape != (mu.shape[0], mu.shape[0]):
        raise ValueError(
            f"dimensión incompatible: vector {array.shape}, mu {mu.shape}, M {transform.shape}"
        )
    centered = array - mu
    projected = transform @ centered
    return projected / (float(np.linalg.norm(projected)) + 1e-12)


def build_surgical_reprompt(alert: TurnAlert) -> str:
    symbol = alert.symbol or "el símbolo activo"
    related = ""
    if alert.related_turn is not None:
        related = f" Revisá el turno {alert.related_turn}."
    if alert.kind == "AST_CONTRACT_BREACH":
        return (
            f"Corregí el contrato AST de {symbol} en el turno {alert.turn_id}.{related} "
            f"Detalle: {alert.detail}"
        )
    if alert.kind == "THRASHING_LOOP_DETECTED":
        return (
            f"No repitas el parche rechazado en el turno {alert.turn_id}.{related} "
            f"Detalle: {alert.detail}"
        )
    if alert.kind == "GOAL_DRIFT_DETECTED":
        return (
            f"Volvé al objetivo anclado. El turno {alert.turn_id} derivó dos pasos seguidos. "
            f"Detalle: {alert.detail}"
        )
    if alert.kind == "COSMETIC_STAGNATION":
        return (
            f"El turno {alert.turn_id} no se movió después del rechazo anterior. "
            f"Cambiá el enfoque. Detalle: {alert.detail}"
        )
    raise ValueError(f"alerta desconocida: {alert.kind}")


def _inv_sqrt(cov: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(np.asarray(cov, dtype=np.float64))
    safe = np.maximum(values, 1e-8)
    scaled = vectors * (1.0 / np.sqrt(safe))
    return scaled @ vectors.T

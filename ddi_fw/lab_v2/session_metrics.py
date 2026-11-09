"""Métricas y veredicto del Test B. Ningún ganador está escrito de antemano."""

from __future__ import annotations

import numpy as np

LATEX_BLOCK = r"""## Fórmulas

Alineación con el ancla:

$$\alpha_t = \tilde{e}_t^{\top} \tilde{e}_{\text{anchor}}$$

Velocidad de paso:

$$\nu_t = \|\tilde{e}_t - \tilde{e}_{t-1}\|_2$$

Resonancia con la memoria negativa:

$$\rho_t = \max_{j \in \mathcal{F}_{<t}} \tilde{e}_t^{\top} \tilde{e}_j$$

Contaminación del historial:

$$H_{\text{ctx}}(t) = \frac{\text{superseded} + \text{traces}}{\max(1,\ \text{tokens})}$$
"""

_DETECTOR_ORDER = (
    "D1_RawCosineOnly",
    "D2_WhitenedKinematicsOnly",
    "D3_FullGovernor_Kinematics_Plus_AST",
)
_FAULTY = ("shadowing", "thrashing", "goal_drift")


def harmonic_f1(precision: float, recall: float) -> float:
    if precision + recall == 0.0:
        return 0.0
    return float(2.0 * precision * recall / (precision + recall))


def summarize_detector(
    *,
    sessions: list[object],
    alert_turns: list[list[int]],
    audit_latency_ms: list[float],
) -> dict[str, float]:
    if len(sessions) != len(alert_turns):
        raise ValueError("sesiones y alertas no alinean")
    detected = {name: 0 for name in _FAULTY}
    totals = {name: 0 for name in _FAULTY}
    healthy_total = 0
    healthy_false = 0
    for session, alerts in zip(sessions, alert_turns, strict=True):
        archetype = str(session.archetype)
        fault = session.ground_truth_fault_turn
        if fault is None:
            healthy_total += 1
            healthy_false += int(bool(alerts))
            continue
        if archetype not in detected:
            continue
        totals[archetype] += 1
        detected[archetype] += int(any(turn <= int(fault) for turn in alerts))
    faulty_total = sum(totals.values())
    faulty_hit = sum(detected.values())
    if faulty_total < 1 or healthy_total < 1:
        raise ValueError("el benchmark necesita sesiones sanas y defectuosas")
    recall = float(faulty_hit) / float(faulty_total)
    false_rate = float(healthy_false) / float(healthy_total)
    precision = 0.0 if faulty_hit + healthy_false == 0 else float(faulty_hit) / float(faulty_hit + healthy_false)
    per_archetype: dict[str, float] = {}
    for name in _FAULTY:
        arch_recall = float(detected[name]) / float(totals[name])
        arch_precision = (
            0.0
            if detected[name] + healthy_false == 0
            else float(detected[name]) / float(detected[name] + healthy_false)
        )
        per_archetype[name] = harmonic_f1(arch_precision, arch_recall)
    latency = np.asarray(audit_latency_ms, dtype=np.float64).reshape(-1)
    if latency.size < 1:
        raise ValueError("no hay latencias de auditoría")
    return {
        "fault_detection_recall": recall,
        "healthy_session_false_alarm_rate": false_rate,
        "f1_score": harmonic_f1(precision, recall),
        "f1_shadowing": per_archetype["shadowing"],
        "f1_thrashing": per_archetype["thrashing"],
        "f1_goal_drift": per_archetype["goal_drift"],
        "mean_turn_audit_latency_ms": float(np.mean(latency)),
    }


def summarize_compiler(rows: list[dict[str, float]]) -> dict[str, float]:
    if not rows:
        raise ValueError("no hay compilaciones")
    count = float(len(rows))
    return {
        "mean_original_tokens": float(sum(row["original_tokens"] for row in rows) / count),
        "mean_compiled_tokens": float(sum(row["compiled_tokens"] for row in rows) / count),
        "mean_token_savings_ratio": float(sum(row["savings_ratio"] for row in rows) / count),
        "invariant_retention_rate": float(sum(row["invariant_ok"] for row in rows) / count),
        "live_signature_retention_rate": float(sum(row["live_ok"] for row in rows) / count),
        "obsolete_code_pruning_rate": float(sum(row["obsolete_ok"] for row in rows) / count),
        "mean_compile_latency_ms": float(sum(row["latency_ms"] for row in rows) / count),
        "mean_turn_audit_latency_ms": float(sum(row["audit_latency_ms"] for row in rows) / count),
    }


def determine_test_b_verdict(
    d1_stats: dict[str, float],
    d2_stats: dict[str, float],
    d3_stats: dict[str, float],
    compiler_stats: dict[str, float],
) -> dict[str, object]:
    d3_beats_raw = (
        d3_stats["fault_detection_recall"] >= d1_stats["fault_detection_recall"] + 0.05
        or d3_stats["f1_score"] >= d1_stats["f1_score"] + 0.05
    ) and d3_stats["healthy_session_false_alarm_rate"] <= d1_stats[
        "healthy_session_false_alarm_rate"
    ]
    ranking = sorted(
        [
            ("D1_RawCosineOnly", d1_stats),
            ("D2_WhitenedKinematicsOnly", d2_stats),
            ("D3_FullGovernor_Kinematics_Plus_AST", d3_stats),
        ],
        key=lambda item: (
            item[1]["f1_score"],
            item[1]["fault_detection_recall"],
            -item[1]["healthy_session_false_alarm_rate"],
        ),
        reverse=True,
    )
    compiler_ok = (
        compiler_stats["invariant_retention_rate"] == 1.0
        and compiler_stats["live_signature_retention_rate"] == 1.0
        and compiler_stats["mean_compiled_tokens"] <= 36000
        and compiler_stats["mean_token_savings_ratio"] > 0.85
    )
    return {
        "overall_winner": ranking[0][0],
        "governor_beats_raw_cosine": bool(d3_beats_raw),
        "compiler_meets_contract": bool(compiler_ok),
    }


def render_test_b_markdown(payload: dict[str, object]) -> str:
    detectors = payload["detectors"]
    compiler = payload["compiler"]
    verdict = payload["verdict"]
    if not isinstance(detectors, dict) or not isinstance(compiler, dict) or not isinstance(verdict, dict):
        raise ValueError("payload incompleto")
    lines = [
        "# Test B — Context rot por encima de 250k tokens",
        "",
        "Las cifras salen de `summarize_detector`, `summarize_compiler` y `determine_test_b_verdict`.",
        "El JSON guarda float nativo; esta tabla usa `format(x, '.17g')`.",
        "",
        LATEX_BLOCK.rstrip(),
        "",
        "## Detectores",
        "",
        "| detector | recall | false_alarm | f1 | f1_shadowing | f1_thrashing | f1_goal_drift |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in _DETECTOR_ORDER:
        stats = detectors[name]
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    _fmt(stats["fault_detection_recall"]),
                    _fmt(stats["healthy_session_false_alarm_rate"]),
                    _fmt(stats["f1_score"]),
                    _fmt(stats["f1_shadowing"]),
                    _fmt(stats["f1_thrashing"]),
                    _fmt(stats["f1_goal_drift"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## ContextCompiler",
            "",
            "| mean_original_tokens | mean_compiled_tokens | mean_token_savings_ratio | invariant_retention_rate | live_signature_retention_rate | obsolete_code_pruning_rate | mean_compile_latency_ms |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            "| "
            + " | ".join(
                [
                    _fmt(compiler["mean_original_tokens"]),
                    _fmt(compiler["mean_compiled_tokens"]),
                    _fmt(compiler["mean_token_savings_ratio"]),
                    _fmt(compiler["invariant_retention_rate"]),
                    _fmt(compiler["live_signature_retention_rate"]),
                    _fmt(compiler["obsolete_code_pruning_rate"]),
                    _fmt(compiler["mean_compile_latency_ms"]),
                ]
            )
            + " |",
            "",
            "## Veredicto",
            "",
            f"- overall_winner: {verdict['overall_winner']}",
            f"- governor_beats_raw_cosine: {bool(verdict['governor_beats_raw_cosine'])}",
            f"- compiler_meets_contract: {bool(verdict['compiler_meets_contract'])}",
            "",
        ]
    )
    return "\n".join(lines)


def _fmt(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        return format(float(value), ".17g")
    return str(value)

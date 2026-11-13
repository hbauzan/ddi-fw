"""Métricas exactas del Test A y veredicto dinámico. Sin redondeo de exportación."""

from __future__ import annotations

import numpy as np

LATEX_BLOCK = r"""## Fórmulas

Margen de coseno por chunk, con umbral conformal \(\tau = q_{\hat{}}\):

$$\tau:\ s_{\cos}(\hat{x}) = \max_{b} (\hat{x}^{\top} \hat{\mu}_{b}) - (\hat{x}^{\top} \hat{\mu}_{\text{python}})$$

Score del subespacio blanqueado:

$$s_{\text{EEB}}(x) = 0.50\,\tilde{z}_{\text{fisher}}(x) + 0.20\,\tilde{z}_{\parallel}(x) + 0.30\,\tilde{z}_{\perp}(x)$$

Dirección de Fisher en el espacio original:

$$\vec{w}^{\top} \vec{x}$$
"""

_MODEL_ORDER = ("M1_DDI_v040", "M2_Cosine", "M3_EEB_Pure", "M4_Hybrid_AST_EEB")
_STAT_FIELDS = (
    "roc_auc",
    "pr_auc",
    "far_at_frr_01",
    "far_at_frr_05",
    "frr_stdlib_python",
    "frr_business_python",
    "far_seen_domain",
    "far_unseen_domain_ood",
    "far_other_language",
    "far_piggybacking",
    "frr_total",
    "far_total",
    "latency_ms_p50",
    "latency_ms_p95",
    "latency_ms_p99",
)


def compute_roc_auc(pos_legit_scores: np.ndarray, neg_attack_scores: np.ndarray) -> float:
    legit = _vector(pos_legit_scores, "pos_legit_scores")
    attack = _vector(neg_attack_scores, "neg_attack_scores")
    diffs = attack[:, None] - legit[None, :]
    wins = np.sum(diffs > 0) + 0.5 * np.sum(diffs == 0)
    return float(wins) / float(legit.size * attack.size)


def compute_pr_auc(pos_legit_scores: np.ndarray, neg_attack_scores: np.ndarray) -> float:
    legit = _vector(pos_legit_scores, "pos_legit_scores")
    attack = _vector(neg_attack_scores, "neg_attack_scores")
    y_true = np.concatenate((np.ones(attack.size, dtype=np.float64), np.zeros(legit.size)))
    y_score = np.concatenate((attack, legit))
    order = np.argsort(-y_score, kind="mergesort")
    y_true = y_true[order]
    tp = np.cumsum(y_true)
    fp = np.cumsum(1.0 - y_true)
    precision = tp / np.maximum(tp + fp, 1e-12)
    return float(np.sum(precision[y_true == 1.0]) / float(attack.size))


def compute_far_at_frr(
    pos_legit_scores: np.ndarray,
    neg_attack_scores: np.ndarray,
    max_frr: float,
) -> float:
    legit = _vector(pos_legit_scores, "pos_legit_scores")
    attack = _vector(neg_attack_scores, "neg_attack_scores")
    if not 0.0 <= max_frr <= 1.0:
        raise ValueError(f"max_frr debe estar en [0, 1], recibido: {max_frr}")
    threshold = float(np.quantile(legit, 1.0 - max_frr))
    return float(np.mean(attack <= threshold))


def summarize_detection(
    *,
    legit_scores: np.ndarray,
    attack_scores: np.ndarray,
    counts: dict[str, tuple[int, int]],
    latency_ms: np.ndarray,
) -> dict[str, float]:
    """`counts[category] = (n, n_breach)` sobre el split de test."""
    legit = _vector(legit_scores, "legit_scores")
    attack = _vector(attack_scores, "attack_scores")
    latency = _vector(latency_ms, "latency_ms")
    stdlib_n, stdlib_block = _pair(counts, "pos_stdlib_python")
    business_n, business_block = _pair(counts, "pos_business_python")
    seen_n, seen_block = _pair(counts, "neg_seen_domain")
    ood_n, ood_block = _pair(counts, "neg_unseen_domain_ood")
    lang_n, lang_block = _pair(counts, "neg_other_language")
    piggy_n, piggy_block = _pair(counts, "neg_piggybacking")
    positive_n = stdlib_n + business_n
    negative_n = seen_n + ood_n + lang_n + piggy_n
    negative_miss = (
        (seen_n - seen_block)
        + (ood_n - ood_block)
        + (lang_n - lang_block)
        + (piggy_n - piggy_block)
    )
    stats = {
        "roc_auc": compute_roc_auc(legit, attack),
        "pr_auc": compute_pr_auc(legit, attack),
        "far_at_frr_01": compute_far_at_frr(legit, attack, 0.01),
        "far_at_frr_05": compute_far_at_frr(legit, attack, 0.05),
        "frr_stdlib_python": _rate(stdlib_block, stdlib_n),
        "frr_business_python": _rate(business_block, business_n),
        "far_seen_domain": _rate(seen_n - seen_block, seen_n),
        "far_unseen_domain_ood": _rate(ood_n - ood_block, ood_n),
        "far_other_language": _rate(lang_n - lang_block, lang_n),
        "far_piggybacking": _rate(piggy_n - piggy_block, piggy_n),
        "frr_total": _rate(stdlib_block + business_block, positive_n),
        "far_total": _rate(negative_miss, negative_n),
        "latency_ms_p50": float(np.percentile(latency, 50)),
        "latency_ms_p95": float(np.percentile(latency, 95)),
        "latency_ms_p99": float(np.percentile(latency, 99)),
    }
    return {key: float(stats[key]) for key in _STAT_FIELDS}


def determine_test_a_verdict(
    m1_stats: dict[str, float],
    m2_stats: dict[str, float],
    m3_stats: dict[str, float],
    m4_stats: dict[str, float],
) -> dict[str, object]:
    m3_beats_cosine = (m3_stats["roc_auc"] >= m2_stats["roc_auc"] + 0.01) or (
        m3_stats["far_at_frr_05"] <= m2_stats["far_at_frr_05"] - 0.03
    )
    ranking = sorted(
        [
            ("M1_DDI_v040", m1_stats),
            ("M2_Cosine", m2_stats),
            ("M3_EEB_Pure", m3_stats),
            ("M4_Hybrid_AST_EEB", m4_stats),
        ],
        key=lambda item: (item[1]["roc_auc"], -item[1]["far_at_frr_05"]),
        reverse=True,
    )
    return {
        "overall_winner": ranking[0][0],
        "pure_embedding_winner": "M3_EEB_Pure" if m3_beats_cosine else "M2_Cosine",
        "m3_beats_cosine_empirically": bool(m3_beats_cosine),
        "m1_ddi_v040_viable": bool(m1_stats["frr_total"] < 0.25 and m1_stats["far_total"] < 0.10),
    }


def render_test_a_markdown(payload: dict[str, object]) -> str:
    models = payload["models"]
    verdict = payload["verdict"]
    if not isinstance(models, dict) or not isinstance(verdict, dict):
        raise ValueError("payload sin models o verdict")
    lines = [
        "# Test A — Duelo de subespacio blanqueado contra coseno",
        "",
        "Los números salen de `summarize_detection` y `determine_test_a_verdict`.",
        "El JSON hermano guarda los float nativos; esta tabla usa `format(x, '.17g')`.",
        "",
        LATEX_BLOCK.rstrip(),
        "",
        "## Comparación",
        "",
        "| modelo | roc_auc | pr_auc | far_at_frr_01 | far_at_frr_05 | frr_total | far_total | frr_business_python | far_piggybacking |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in _MODEL_ORDER:
        stats = models[name]
        if not isinstance(stats, dict):
            raise ValueError(f"{name} no es un diccionario de métricas")
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    _fmt(stats["roc_auc"]),
                    _fmt(stats["pr_auc"]),
                    _fmt(stats["far_at_frr_01"]),
                    _fmt(stats["far_at_frr_05"]),
                    _fmt(stats["frr_total"]),
                    _fmt(stats["far_total"]),
                    _fmt(stats["frr_business_python"]),
                    _fmt(stats["far_piggybacking"]),
                ]
            )
            + " |"
        )
    _append_category_breakdown(lines, models)
    lines.extend(
        [
            "",
            "## Latencia de scoring",
            "",
            "| modelo | p50_ms | p95_ms | p99_ms |",
            "| --- | --- | --- | --- |",
        ]
    )
    for name in _MODEL_ORDER:
        stats = models[name]
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    _fmt(stats["latency_ms_p50"]),
                    _fmt(stats["latency_ms_p95"]),
                    _fmt(stats["latency_ms_p99"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Veredicto",
            "",
            f"- overall_winner: {verdict['overall_winner']}",
            f"- pure_embedding_winner: {verdict['pure_embedding_winner']}",
            f"- m3_beats_cosine_empirically: {bool(verdict['m3_beats_cosine_empirically'])}",
            f"- m1_ddi_v040_viable: {bool(verdict['m1_ddi_v040_viable'])}",
            "",
        ]
    )
    hardware = payload.get("hardware")
    if isinstance(hardware, dict):
        lines.append("## Entorno")
        lines.append("")
        for key, value in hardware.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    return "\n".join(lines)


_BREAKDOWN_FIELDS = (
    "frr_stdlib_python",
    "frr_business_python",
    "far_seen_domain",
    "far_unseen_domain_ood",
    "far_other_language",
    "far_piggybacking",
)


def _append_category_breakdown(lines: list[str], models: dict[str, object]) -> None:
    first = next(iter(models.values()), None)
    if not isinstance(first, dict):
        return
    if "far_other_language" not in first or "far_unseen_domain_ood" not in first:
        return
    lines.extend(
        [
            "",
            "## Desglose por subcategoría",
            "",
            (
                "| modelo | frr_stdlib_python | frr_business_python | far_seen_domain | "
                "far_unseen_domain_ood | far_other_language | far_piggybacking |"
            ),
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for name in _MODEL_ORDER:
        stats = models[name]
        if not isinstance(stats, dict):
            raise ValueError(f"{name} no es un diccionario de métricas")
        cells = [name, *(_fmt(stats[field]) for field in _BREAKDOWN_FIELDS)]
        lines.append("| " + " | ".join(cells) + " |")


def _vector(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64).reshape(-1)
    if array.size < 1:
        raise ValueError(f"{name} no puede estar vacío")
    return array


def _pair(counts: dict[str, tuple[int, int]], category: str) -> tuple[int, int]:
    if category not in counts:
        raise ValueError(f"falta la categoría {category}")
    total, blocked = counts[category]
    if total < 1 or blocked < 0 or blocked > total:
        raise ValueError(f"conteo inválido para {category}: {(total, blocked)}")
    return int(total), int(blocked)


def _rate(numerator: int, denominator: int) -> float:
    if denominator < 1:
        raise ValueError("denominador de tasa inválido")
    return float(numerator) / float(denominator)


def _fmt(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        return format(float(value), ".17g")
    return str(value)

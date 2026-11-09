"""Duelo A/B vivo o mock: 265k crudos contra el contexto compilado por DDI."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path

import httpx

from ddi_fw.lab_v2.context_compiler import estimate_tokens
from ddi_fw.lab_v2.live_ab_harness import BudgetGuard, GeminiLiveClient, load_live_config
from ddi_fw.lab_v2.live_ab_scenarios import (
    LiveAbScenario,
    build_live_ab_scenarios,
    compile_scenario_for_ddi,
    verify_scenario_code,
)

_DEFAULT_JSON = Path("reports/lab_v2_test_c_live_ab.json")
_DEFAULT_MD = Path("reports/test_c_ab_live_api.md")
_LATEX = r"""## Fórmula

El ahorro y la ganancia salen de los conteos del summary, sin redondeo previo:

$$\mathrm{Pass@1}_{\mathrm{gain}} = \mathrm{Pass@1}_{\mathrm{DDI}} - \mathrm{Pass@1}_{\mathrm{raw}}$$

$$\mathrm{savings} = 1 - \frac{T_{\mathrm{DDI}}}{T_{\mathrm{raw}}}$$
"""


def determine_test_c_verdict(summary: dict[str, object]) -> dict[str, object]:
    raw = _as_float(summary["pass_at_1_raw_265k"])
    compiled = _as_float(summary["pass_at_1_ddi_compiled"])
    savings = _as_float(summary["real_input_token_savings_ratio"])
    if compiled > raw:
        winner = "DDI_Compiled"
    elif compiled < raw:
        winner = "Raw_265k"
    else:
        winner = "Tie"
    return {
        "accuracy_winner": winner,
        "ddi_improves_or_preserves_pass_at_1": bool(compiled >= raw),
        "ddi_strictly_beats_raw_pass_at_1": bool(compiled > raw),
        "token_savings_exceeds_80pct": bool(savings >= 0.80),
    }


def run_test_c_live_ab(
    *,
    mode: str,
    json_path: Path,
    md_path: Path,
    transport: httpx.BaseTransport | None = None,
    sleep_fn: Callable[[float], None] | None = None,
) -> dict[str, object]:
    if mode not in {"live", "mock"}:
        raise ValueError("mode debe ser live o mock")
    scenarios = build_live_ab_scenarios()
    if len(scenarios) != 10:
        raise RuntimeError("se requieren 10 escenarios")
    guard = BudgetGuard()
    if mode == "mock":
        api_key = "mock-not-a-real-key"
        model = "gemini-2.5-flash"
        client_transport = transport if transport is not None else httpx.MockTransport(_mock_handler)
        sleeper = sleep_fn if sleep_fn is not None else _noop_sleep
    else:
        config = load_live_config()
        api_key = config.api_key
        model = config.model
        client_transport = transport
        sleeper = time.sleep if sleep_fn is None else sleep_fn
    client = GeminiLiveClient(
        api_key,
        model,
        guard,
        transport=client_transport,
        sleep_fn=sleeper,
    )
    try:
        rows = [_evaluate_scenario(client, scenario) for scenario in scenarios]
    finally:
        client.close()
    summary = _summarize(rows)
    payload: dict[str, object] = {
        "task_id": "TASK-004",
        "mode": mode,
        "model": model,
        "successful_api_calls": guard.successful_calls,
        "http_attempts": guard.http_attempts,
        "accumulated_input_tokens": guard.accumulated_input_tokens,
        "summary": summary,
        "verdict": determine_test_c_verdict(summary),
        "scenarios": rows,
    }
    _write_outputs(payload, json_path, md_path)
    return payload


def _evaluate_scenario(client: GeminiLiveClient, scenario: LiveAbScenario) -> dict[str, object]:
    compiled = compile_scenario_for_ddi(scenario)
    raw = _call_arm(client, scenario, scenario.messages)
    _progress(scenario.scenario_id, "raw_265k", raw)
    ddi = _call_arm(client, scenario, compiled.messages)
    _progress(scenario.scenario_id, "ddi_compiled", ddi)
    return {
        "scenario_id": scenario.scenario_id,
        "family": scenario.family,
        "raw_265k": raw,
        "ddi_compiled": ddi,
    }


def _call_arm(
    client: GeminiLiveClient,
    scenario: LiveAbScenario,
    messages: list[dict[str, str]],
) -> dict[str, object]:
    estimated = sum(estimate_tokens(message.get("content", "")) for message in messages)
    completion = client.generate(messages, estimated)
    evaluated = verify_scenario_code(scenario, completion.text)
    return {
        "prompt_tokens": completion.prompt_tokens,
        "output_tokens": completion.output_tokens,
        "latency_ms": float(completion.latency_ms),
        "syntax_ok": evaluated.syntax_ok,
        "ast_signature_ok": evaluated.ast_signature_ok,
        "passed": evaluated.passed,
        "failure_reason": evaluated.failure_reason,
    }


def _summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    raw_pass = [_flag(row, "raw_265k", "passed") for row in rows]
    ddi_pass = [_flag(row, "ddi_compiled", "passed") for row in rows]
    families = [str(row["family"]) for row in rows]
    shadow_raw = [flag for flag, family in zip(raw_pass, families, strict=True) if family == "multi_refactor_shadowing"]
    shadow_ddi = [flag for flag, family in zip(ddi_pass, families, strict=True) if family == "multi_refactor_shadowing"]
    thrash_raw = [flag for flag, family in zip(raw_pass, families, strict=True) if family == "rejected_patch_thrashing"]
    thrash_ddi = [flag for flag, family in zip(ddi_pass, families, strict=True) if family == "rejected_patch_thrashing"]
    raw_tokens = _ints(rows, "raw_265k", "prompt_tokens")
    ddi_tokens = _ints(rows, "ddi_compiled", "prompt_tokens")
    raw_output = _ints(rows, "raw_265k", "output_tokens")
    ddi_output = _ints(rows, "ddi_compiled", "output_tokens")
    raw_latency = _floats(rows, "raw_265k", "latency_ms")
    ddi_latency = _floats(rows, "ddi_compiled", "latency_ms")
    total_raw = sum(raw_tokens)
    total_ddi = sum(ddi_tokens)
    savings = 0.0 if total_raw == 0 else float(total_raw - total_ddi) / float(total_raw)
    p50_raw = _percentile(raw_latency, 0.50)
    p50_ddi = _percentile(ddi_latency, 0.50)
    both_pass = 0
    both_fail = 0
    ddi_wins = 0
    raw_wins = 0
    for raw_ok, ddi_ok in zip(raw_pass, ddi_pass, strict=True):
        if raw_ok and ddi_ok:
            both_pass += 1
        elif raw_ok:
            raw_wins += 1
        elif ddi_ok:
            ddi_wins += 1
        else:
            both_fail += 1
    raw_rate = _rate(raw_pass)
    ddi_rate = _rate(ddi_pass)
    return {
        "pass_at_1_raw_265k": raw_rate,
        "pass_at_1_ddi_compiled": ddi_rate,
        "pass_at_1_gain": float(ddi_rate - raw_rate),
        "shadowing_pass_at_1_raw": _rate(shadow_raw),
        "shadowing_pass_at_1_ddi": _rate(shadow_ddi),
        "thrashing_pass_at_1_raw": _rate(thrash_raw),
        "thrashing_pass_at_1_ddi": _rate(thrash_ddi),
        "ast_signature_ok_rate_raw": _rate([_flag(row, "raw_265k", "ast_signature_ok") for row in rows]),
        "ast_signature_ok_rate_ddi": _rate([_flag(row, "ddi_compiled", "ast_signature_ok") for row in rows]),
        "paired_outcomes": {
            "ddi_wins": ddi_wins,
            "raw_wins": raw_wins,
            "both_pass": both_pass,
            "both_fail": both_fail,
        },
        "total_prompt_tokens_raw": total_raw,
        "total_prompt_tokens_ddi": total_ddi,
        "real_input_token_savings_ratio": float(savings),
        "total_output_tokens_raw": sum(raw_output),
        "total_output_tokens_ddi": sum(ddi_output),
        "latency_ms_p50_raw": p50_raw,
        "latency_ms_p95_raw": _percentile(raw_latency, 0.95),
        "latency_ms_p50_ddi": p50_ddi,
        "latency_ms_p95_ddi": _percentile(ddi_latency, 0.95),
        "latency_speedup_p50": 0.0 if p50_ddi == 0.0 else float(p50_raw) / float(p50_ddi),
    }


def render_test_c_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    verdict = payload["verdict"]
    rows = payload["scenarios"]
    if not isinstance(summary, dict) or not isinstance(verdict, dict) or not isinstance(rows, list):
        raise ValueError("payload incompleto")
    paired = summary["paired_outcomes"]
    if not isinstance(paired, dict):
        raise ValueError("paired_outcomes incompleto")
    lines = [
        "# Test C — Duelo A/B vivo contra Gemini API",
        "",
        "Las cifras salen de `determine_test_c_verdict` y de los conteos por escenario.",
        "El JSON guarda float nativo; esta tabla usa `format(x, '.17g')`.",
        "",
        _LATEX.rstrip(),
        "",
        "## Summary",
        "",
        f"- mode: {payload['mode']}",
        f"- model: {payload['model']}",
        f"- successful_api_calls: {payload['successful_api_calls']}",
        f"- pass_at_1_raw_265k: {_fmt(summary['pass_at_1_raw_265k'])}",
        f"- pass_at_1_ddi_compiled: {_fmt(summary['pass_at_1_ddi_compiled'])}",
        f"- pass_at_1_gain: {_fmt(summary['pass_at_1_gain'])}",
        f"- shadowing_pass_at_1_raw: {_fmt(summary['shadowing_pass_at_1_raw'])}",
        f"- shadowing_pass_at_1_ddi: {_fmt(summary['shadowing_pass_at_1_ddi'])}",
        f"- thrashing_pass_at_1_raw: {_fmt(summary['thrashing_pass_at_1_raw'])}",
        f"- thrashing_pass_at_1_ddi: {_fmt(summary['thrashing_pass_at_1_ddi'])}",
        f"- ast_signature_ok_rate_raw: {_fmt(summary['ast_signature_ok_rate_raw'])}",
        f"- ast_signature_ok_rate_ddi: {_fmt(summary['ast_signature_ok_rate_ddi'])}",
        f"- total_prompt_tokens_raw: {_fmt(summary['total_prompt_tokens_raw'])}",
        f"- total_prompt_tokens_ddi: {_fmt(summary['total_prompt_tokens_ddi'])}",
        f"- real_input_token_savings_ratio: {_fmt(summary['real_input_token_savings_ratio'])}",
        f"- total_output_tokens_raw: {_fmt(summary['total_output_tokens_raw'])}",
        f"- total_output_tokens_ddi: {_fmt(summary['total_output_tokens_ddi'])}",
        f"- latency_ms_p50_raw: {_fmt(summary['latency_ms_p50_raw'])}",
        f"- latency_ms_p95_raw: {_fmt(summary['latency_ms_p95_raw'])}",
        f"- latency_ms_p50_ddi: {_fmt(summary['latency_ms_p50_ddi'])}",
        f"- latency_ms_p95_ddi: {_fmt(summary['latency_ms_p95_ddi'])}",
        f"- latency_speedup_p50: {_fmt(summary['latency_speedup_p50'])}",
        f"- ddi_wins: {_fmt(paired['ddi_wins'])}",
        f"- raw_wins: {_fmt(paired['raw_wins'])}",
        f"- both_pass: {_fmt(paired['both_pass'])}",
        f"- both_fail: {_fmt(paired['both_fail'])}",
        "",
        "## Veredicto",
        "",
        f"- accuracy_winner: {verdict['accuracy_winner']}",
        f"- ddi_improves_or_preserves_pass_at_1: {_fmt(verdict['ddi_improves_or_preserves_pass_at_1'])}",
        f"- ddi_strictly_beats_raw_pass_at_1: {_fmt(verdict['ddi_strictly_beats_raw_pass_at_1'])}",
        f"- token_savings_exceeds_80pct: {_fmt(verdict['token_savings_exceeds_80pct'])}",
        "",
        "## Escenarios",
        "",
        "| escenario | familia | tokens_raw | tokens_ddi | lat_raw_ms | lat_ddi_ms | syntax_raw | syntax_ddi | ast_raw | ast_ddi | pass_raw | pass_ddi | failure_raw | failure_ddi |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("fila invalida")
        raw = row["raw_265k"]
        ddi = row["ddi_compiled"]
        if not isinstance(raw, dict) or not isinstance(ddi, dict):
            raise ValueError("brazo invalido")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["scenario_id"]),
                    str(row["family"]),
                    _fmt(raw["prompt_tokens"]),
                    _fmt(ddi["prompt_tokens"]),
                    _fmt(raw["latency_ms"]),
                    _fmt(ddi["latency_ms"]),
                    _fmt(raw["syntax_ok"]),
                    _fmt(ddi["syntax_ok"]),
                    _fmt(raw["ast_signature_ok"]),
                    _fmt(ddi["ast_signature_ok"]),
                    _fmt(raw["passed"]),
                    _fmt(ddi["passed"]),
                    _cell(raw["failure_reason"]),
                    _cell(ddi["failure_reason"]),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> dict[str, object]:
    parser = argparse.ArgumentParser(description="Duelo A/B vivo de Test C contra Gemini")
    parser.add_argument("--mode", choices=("live", "mock"), default="live")
    parser.add_argument("--json-out", type=Path, default=_DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=_DEFAULT_MD)
    args = parser.parse_args(argv)
    return run_test_c_live_ab(mode=args.mode, json_path=args.json_out, md_path=args.md_out)


def _mock_handler(request: httpx.Request) -> httpx.Response:
    del request
    return httpx.Response(
        200,
        json={
            "candidates": [{"content": {"parts": [{"text": "sin implementacion"}]}}],
            "usageMetadata": {"promptTokenCount": 128, "candidatesTokenCount": 4},
        },
    )


def _progress(scenario_id: str, arm: str, row: dict[str, object]) -> None:
    print(
        f"{scenario_id} {arm} passed={row['passed']} "
        f"prompt_tokens={row['prompt_tokens']} latency_ms={row['latency_ms']}",
        file=sys.stderr,
        flush=True,
    )


def _noop_sleep(seconds: float) -> None:
    del seconds


def _write_outputs(payload: dict[str, object], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False)
    json_path.write_text(encoded + "\n", encoding="utf-8")
    md_path.write_text(render_test_c_markdown(payload), encoding="utf-8")


def _percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def _rate(flags: list[bool]) -> float:
    if not flags:
        return 0.0
    return float(sum(1 for flag in flags if flag)) / float(len(flags))


def _flag(row: dict[str, object], arm: str, field: str) -> bool:
    arm_row = row[arm]
    if not isinstance(arm_row, dict):
        raise ValueError("brazo invalido")
    return bool(arm_row[field])


def _ints(rows: list[dict[str, object]], arm: str, field: str) -> list[int]:
    values: list[int] = []
    for row in rows:
        arm_row = row[arm]
        if not isinstance(arm_row, dict) or not isinstance(arm_row[field], int):
            raise ValueError(field)
        values.append(arm_row[field])
    return values


def _floats(rows: list[dict[str, object]], arm: str, field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        arm_row = row[arm]
        if not isinstance(arm_row, dict) or not isinstance(arm_row[field], (int, float)):
            raise ValueError(field)
        if isinstance(arm_row[field], bool):
            raise ValueError(field)
        values.append(float(arm_row[field]))
    return values


def _as_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("metrica numerica invalida")
    return float(value)


def _fmt(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(value, ".17g")
    if value is None:
        return ""
    return str(value)


def _cell(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


if __name__ == "__main__":
    main()

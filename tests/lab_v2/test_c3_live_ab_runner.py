"""Slice C3: veredicto dinamico y runner mock sin red."""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from scripts.lab_v2.run_test_c_live_ab import determine_test_c_verdict, run_test_c_live_ab


def _summary(raw: float, compiled: float, savings: float) -> dict[str, object]:
    return {
        "pass_at_1_raw_265k": raw,
        "pass_at_1_ddi_compiled": compiled,
        "real_input_token_savings_ratio": savings,
    }


def test_verdict_follows_the_measured_rates() -> None:
    ddi = determine_test_c_verdict(_summary(0.2, 0.6, 0.91))
    assert ddi["accuracy_winner"] == "DDI_Compiled"
    assert ddi["ddi_improves_or_preserves_pass_at_1"] is True
    assert ddi["ddi_strictly_beats_raw_pass_at_1"] is True
    assert ddi["token_savings_exceeds_80pct"] is True
    raw = determine_test_c_verdict(_summary(0.8, 0.3, 0.91))
    assert raw["accuracy_winner"] == "Raw_265k"
    assert raw["ddi_improves_or_preserves_pass_at_1"] is False
    assert raw["ddi_strictly_beats_raw_pass_at_1"] is False
    tie = determine_test_c_verdict(_summary(0.4, 0.4, 0.79))
    assert tie["accuracy_winner"] == "Tie"
    assert tie["ddi_improves_or_preserves_pass_at_1"] is True
    assert tie["ddi_strictly_beats_raw_pass_at_1"] is False
    assert tie["token_savings_exceeds_80pct"] is False
    exact = determine_test_c_verdict(_summary(0.0, 0.0, 0.80))
    assert exact["token_savings_exceeds_80pct"] is True


def test_mock_runner_makes_twenty_calls_and_keeps_native_precision(tmp_path: Path) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "candidates": [{"content": {"parts": [{"text": "sin implementacion"}]}}],
                "usageMetadata": {"promptTokenCount": 128, "candidatesTokenCount": 4},
            },
        )

    json_path = tmp_path / "lab_v2_test_c_live_ab.json"
    md_path = tmp_path / "test_c_ab_live_api.md"
    payload = run_test_c_live_ab(
        mode="mock",
        json_path=json_path,
        md_path=md_path,
        transport=httpx.MockTransport(handler),
    )
    assert len(seen) == 20
    assert payload["mode"] == "mock"
    assert payload["successful_api_calls"] == 20
    source = Path("scripts/lab_v2/run_test_c_live_ab.py").read_text(encoding="utf-8")
    assert "round(" not in source
    assert ":.2f" not in source
    markdown = md_path.read_text(encoding="utf-8")
    assert "\t" not in markdown
    assert "\x0b" not in markdown
    assert r"\frac" in markdown
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["successful_api_calls"] == 20
    assert loaded["verdict"]["accuracy_winner"] in {"DDI_Compiled", "Raw_265k", "Tie"}
    assert isinstance(loaded["summary"]["pass_at_1_gain"], (int, float))

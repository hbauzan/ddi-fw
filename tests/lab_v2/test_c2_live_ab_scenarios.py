"""Slice C2: diez escenarios de ~265k, compilacion y oraculo ejecutable."""

from __future__ import annotations

from ddi_fw.lab_v2.context_compiler import estimate_tokens
from ddi_fw.lab_v2.live_ab_scenarios import (
    build_live_ab_scenarios,
    compile_scenario_for_ddi,
    evaluar_lote_peticiones,
    verify_scenario_code,
)


def test_ten_scenarios_compile_and_the_oracle_separates_solutions() -> None:
    scenarios = build_live_ab_scenarios()
    assert len(scenarios) == 10
    families = [scenario.family for scenario in scenarios]
    assert families[:5] == ["multi_refactor_shadowing"] * 5
    assert families[5:] == ["rejected_patch_thrashing"] * 5
    assert evaluar_lote_peticiones(
        [("p1", 4), ("p1", 9), ("p2", 20)],
        recarga=10,
        tope=15,
        minimo=2,
        canal="api",
    ) == {
        "canal": "api",
        "aceptadas": 1,
        "rechazadas": 1,
        "consumidas": 4,
        "disponible": 6,
    }
    for scenario in scenarios:
        assert len(scenario.turns) == 96
        assert 255_000 <= scenario.raw_tokens <= 275_000
        compiled = compile_scenario_for_ddi(scenario)
        assert compiled.compiled_tokens <= 36_000
        assert compiled.messages[-1]["content"] == scenario.messages[-1]["content"]
        governor = "\n".join(
            message["content"]
            for message in compiled.messages
            if "[DDI-CONTEXT-GOVERNOR]" in message["content"]
        )
        assert governor
        for signature in scenario.live_signature_texts:
            assert signature in governor
        if scenario.family == "multi_refactor_shadowing":
            assert "*," in governor
        else:
            later = sum(
                estimate_tokens(turn.content) for turn in scenario.turns if turn.turn_id > 56
            )
            assert later > 150_000
            assert [turn.turn_id for turn in scenario.turns if not turn.accepted] == [20, 38, 56]
        joined = "\n".join(message["content"] for message in compiled.messages)
        assert "MARCA-PARCHE-RECHAZADO" not in joined
        assert "total = 0.0" not in joined
        reference = verify_scenario_code(scenario, scenario.reference_solution)
        assert reference.passed is True
        assert reference.syntax_ok is True
        assert reference.ast_signature_ok is True
        assert reference.failure_reason is None
        deprecated = verify_scenario_code(scenario, scenario.broken_deprecated_call_solution)
        assert deprecated.passed is False
        assert deprecated.failure_reason
        broken = verify_scenario_code(scenario, scenario.broken_invariant_solution)
        assert broken.passed is False
        assert broken.failure_reason

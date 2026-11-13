"""Slice C2: diez escenarios de ~265k, compilacion y oraculo ejecutable."""

from __future__ import annotations

from ddi_fw.lab_v2.context_compiler import estimate_tokens
from ddi_fw.lab_v2.live_ab_scenarios import (
    build_live_ab_scenarios,
    compile_scenario_for_ddi,
    evaluar_lote_peticiones,
    shadow_expected,
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
    assert shadow_expected(
        [("a", 100000), ("a", 1), ("b", 40000)],
        rate_a=250,
        floor=100,
        rate_b=5000,
        cap=80,
        label="ARS",
        divisor_a=10000,
        divisor_b=10000,
        label_key="moneda",
        left_key="cargos_centavos",
        right_key="retenciones_centavos",
        net_key="neto_centavos",
        count_key="operaciones",
    ) == {
        "moneda": "ARS",
        "cargos_centavos": 3500,
        "retenciones_centavos": 160,
        "neto_centavos": 3340,
        "operaciones": 2,
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
        joined = "\n".join(message["content"] for message in compiled.messages)
        for signature in scenario.live_signature_texts:
            assert signature in governor
        assert "Encabezados tipados vigentes:" in governor
        assert "-> int" in governor.split("Encabezados tipados vigentes:", 1)[1]
        for name in scenario.helper_names:
            assert f"def {name}" in joined
        if scenario.family == "multi_refactor_shadowing":
            assert "*," in governor
            assert scenario.exclusive_kw_names
            turn_74 = scenario.turns[74].content
            for name in scenario.exclusive_kw_names:
                assert name in turn_74
                for turn_id in (0, 1, 95):
                    assert name not in scenario.turns[turn_id].content
                assert sum(name in turn.content for turn in scenario.turns) == 1
        else:
            later = sum(
                estimate_tokens(turn.content) for turn in scenario.turns if turn.turn_id > 56
            )
            assert later > 150_000
            assert [turn.turn_id for turn in scenario.turns if not turn.accepted] == [18, 36, 54]
        for turn in scenario.turns:
            assert "xxxx" not in turn.content
            assert estimate_tokens(turn.content) <= 6_000
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

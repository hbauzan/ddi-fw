# Test C — Duelo A/B vivo contra Gemini API

Las cifras salen de `determine_test_c_verdict` y de los conteos por escenario.
El JSON guarda float nativo; esta tabla usa `format(x, '.17g')`.

## Fórmula

El ahorro y la ganancia salen de los conteos del summary, sin redondeo previo:

$$\mathrm{Pass@1}_{\mathrm{gain}} = \mathrm{Pass@1}_{\mathrm{DDI}} - \mathrm{Pass@1}_{\mathrm{raw}}$$

$$\mathrm{savings} = 1 - \frac{T_{\mathrm{DDI}}}{T_{\mathrm{raw}}}$$

## Summary

- mode: live
- model: gemini-3.8-flash
- successful_api_calls: 20
- pass_at_1_raw_265k: 1
- pass_at_1_ddi_compiled: 1
- pass_at_1_gain: 0
- shadowing_pass_at_1_raw: 1
- shadowing_pass_at_1_ddi: 1
- thrashing_pass_at_1_raw: 1
- thrashing_pass_at_1_ddi: 1
- ast_signature_ok_rate_raw: 1
- ast_signature_ok_rate_ddi: 1
- total_prompt_tokens_raw: 2926009
- total_prompt_tokens_ddi: 375201
- real_input_token_savings_ratio: 0.87177038758253989
- total_output_tokens_raw: 5296
- total_output_tokens_ddi: 5233
- latency_ms_p50_raw: 9965.4928750023828
- latency_ms_p95_raw: 16945.119389952735
- latency_ms_p50_ddi: 5477.4640830000862
- latency_ms_p95_ddi: 6222.8258711998933
- latency_speedup_p50: 1.8193625232397943
- ddi_wins: 0
- raw_wins: 0
- both_pass: 10
- both_fail: 0

## Veredicto

- accuracy_winner: Tie
- ddi_improves_or_preserves_pass_at_1: true
- ddi_strictly_beats_raw_pass_at_1: false
- token_savings_exceeds_80pct: true

## Escenarios

| escenario | familia | tokens_raw | tokens_ddi | lat_raw_ms | lat_ddi_ms | syntax_raw | syntax_ddi | ast_raw | ast_ddi | pass_raw | pass_ddi | failure_raw | failure_ddi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01_ledger_settlement | multi_refactor_shadowing | 293226 | 37595 | 9878.6245840019546 | 5660.6894169963198 | true | true | true | true | true | true |  |  |
| S02_infusion_dosing | multi_refactor_shadowing | 293593 | 37525 | 20684.04033400293 | 5820.7598750013858 | true | true | true | true | true | true |  |  |
| S03_orbital_window | multi_refactor_shadowing | 293422 | 37487 | 9354.5414999971399 | 6247.8949590004049 | true | true | true | true | true | true |  |  |
| S04_contract_indexation | multi_refactor_shadowing | 293373 | 37551 | 10426.579999999376 | 6192.185874999268 | true | true | true | true | true | true |  |  |
| S05_coldchain_allocation | multi_refactor_shadowing | 293652 | 37767 | 9990.7238750020042 | 4863.6583750048885 | true | true | true | true | true | true |  |  |
| S06_token_bucket | rejected_patch_thrashing | 291550 | 37255 | 9940.2618750027614 | 5490.4367910057772 | true | true | true | true | true | true |  |  |
| S07_audit_chain | rejected_patch_thrashing | 291604 | 37492 | 8461.8882909999229 | 4346.5282079996541 | true | true | true | true | true | true |  |  |
| S08_fx_netting | rejected_patch_thrashing | 291872 | 37499 | 12172.058334006579 | 5464.4913749943953 | true | true | true | true | true | true |  |  |
| S09_triage_queue | rejected_patch_thrashing | 291600 | 37447 | 8794.6532089990797 | 5443.8171250076266 | true | true | true | true | true | true |  |  |
| S10_retry_planner | rejected_patch_thrashing | 292117 | 37583 | 12375.327125002514 | 5158.5665000020526 | true | true | true | true | true | true |  |  |

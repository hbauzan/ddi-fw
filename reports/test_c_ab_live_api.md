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
- pass_at_1_raw_265k: 0.10000000000000001
- pass_at_1_ddi_compiled: 0.20000000000000001
- pass_at_1_gain: 0.10000000000000001
- shadowing_pass_at_1_raw: 0
- shadowing_pass_at_1_ddi: 0
- thrashing_pass_at_1_raw: 0.20000000000000001
- thrashing_pass_at_1_ddi: 0.40000000000000002
- ast_signature_ok_rate_raw: 1
- ast_signature_ok_rate_ddi: 1
- total_prompt_tokens_raw: 2146589
- total_prompt_tokens_ddi: 236994
- real_input_token_savings_ratio: 0.88959507385903869
- total_output_tokens_raw: 5708
- total_output_tokens_ddi: 6110
- latency_ms_p50_raw: 9056.0214789948077
- latency_ms_p95_raw: 11490.963985047347
- latency_ms_p50_ddi: 6334.3242709997867
- latency_ms_p95_ddi: 8234.6845168511172
- latency_speedup_p50: 1.4296744359071845
- ddi_wins: 1
- raw_wins: 0
- both_pass: 1
- both_fail: 8

## Veredicto

- accuracy_winner: DDI_Compiled
- ddi_improves_or_preserves_pass_at_1: true
- ddi_strictly_beats_raw_pass_at_1: true
- token_savings_exceeds_80pct: true

## Escenarios

| escenario | familia | tokens_raw | tokens_ddi | lat_raw_ms | lat_ddi_ms | syntax_raw | syntax_ddi | ast_raw | ast_ddi | pass_raw | pass_ddi | failure_raw | failure_ddi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01_ledger_settlement | multi_refactor_shadowing | 214596 | 18627 | 8454.8172080030781 | 6680.5525000017951 | true | true | true | true | false | false | AssertionError: piso: {'moneda': 'ARS', 'cargos_centavos': 100, 'retenciones_centavos': 1, 'neto_centavos': 99, 'operaciones': 1} != {'moneda': 'ARS', 'cargos_centavos': 100, 'retenciones_centavos': 50, 'neto_centavos': 50, 'operaciones': 1} | AssertionError: piso: {'moneda': 'ARS', 'cargos_centavos': 100, 'retenciones_centavos': 1, 'neto_centavos': 99, 'operaciones': 1} != {'moneda': 'ARS', 'cargos_centavos': 100, 'retenciones_centavos': 50, 'neto_centavos': 50, 'operaciones': 1} |
| S02_infusion_dosing | multi_refactor_shadowing | 214750 | 18764 | 8380.601958000625 | 6821.0516250037472 | true | true | true | true | false | false | TypeError: tuple indices must be integers or slices, not str | AttributeError: 'tuple' object has no attribute 'get' |
| S03_orbital_window | multi_refactor_shadowing | 214708 | 18751 | 12136.804791000031 | 6407.348542001273 | true | true | true | true | false | false | TypeError: '<' not supported between instances of 'str' and 'int' | TypeError: '<' not supported between instances of 'str' and 'int' |
| S04_contract_indexation | multi_refactor_shadowing | 214669 | 18718 | 8539.0104999969481 | 6202.1662920014933 | true | true | true | true | false | false | ValueError: Formato de cuota invalido | ValueError: entrada invalida |
| S05_coldchain_allocation | multi_refactor_shadowing | 214789 | 18849 | 10701.602999994066 | 9291.5437920019031 | true | true | true | true | false | false | AssertionError: lote: {'deposito': 'farmacia', 'unidades_netas': 1750000, 'reserva_unidades': 160, 'despacho_unidades': 160, 'lineas': [80, 80]} != {'deposito': 'farmacia', 'unidades_netas': 1750000, 'reserva_unidades': 160, 'despacho_unidades': 1749840, 'lineas': 2} | TypeError: '<' not supported between instances of 'str' and 'int' |
| S06_token_bucket | rejected_patch_thrashing | 214512 | 28580 | 9074.342958003399 | 5927.9772919981042 | true | true | true | true | true | true |  |  |
| S07_audit_chain | rejected_patch_thrashing | 214521 | 28577 | 7534.7594999911962 | 6942.9676250001648 | true | true | true | true | false | true | AssertionError: cadena: {'canal': 'audit', 'eventos': [(3, 1, 4), (8, 2, 5)], 'huella': 2602802402, 'primero': (3, 1, 4), 'ultimo': (8, 2, 5)} != {'canal': 'audit', 'eventos': 2, 'huella': 2602802402, 'primero': 3, 'ultimo': 8} |  |
| S08_fx_netting | rejected_patch_thrashing | 214702 | 28710 | 9758.604667003965 | 6261.2999999983003 | true | true | true | true | false | false | ValueError: sentido desconocido: a | AttributeError: 'tuple' object has no attribute 'get' |
| S09_triage_queue | rejected_patch_thrashing | 214592 | 28604 | 9037.6999999862164 | 5274.2180419882061 | true | true | true | true | false | false | AssertionError: orden: {'sala': 'guardia', 'orden': ['b', 'a'], 'puntaje_maximo': 87, 'pacientes': [('b', 5, 70, 80), ('a', 2, 40, 10)], 'espera_primera': 80} != {'sala': 'guardia', 'orden': ('b', 'a'), 'puntaje_maximo': 87, 'pacientes': 2, 'espera_primera': 80} | AttributeError: 'tuple' object has no attribute 'get' |
| S10_retry_planner | rejected_patch_thrashing | 214750 | 28814 | 9995.079916989198 | 5245.9604579926236 | true | true | true | true | false | false | AssertionError: negativo: no lanzo ValueError | AssertionError: negativo: no lanzo ValueError |

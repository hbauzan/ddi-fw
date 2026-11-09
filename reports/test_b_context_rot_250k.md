# Test B — Context rot por encima de 250k tokens

Las cifras salen de `summarize_detector`, `summarize_compiler` y `determine_test_b_verdict`.
El JSON guarda float nativo; esta tabla usa `format(x, '.17g')`.

## Fórmulas

Alineación con el ancla:

$$\alpha_t = \tilde{e}_t^{\top} \tilde{e}_{\text{anchor}}$$

Velocidad de paso:

$$\nu_t = \|\tilde{e}_t - \tilde{e}_{t-1}\|_2$$

Resonancia con la memoria negativa:

$$\rho_t = \max_{j \in \mathcal{F}_{<t}} \tilde{e}_t^{\top} \tilde{e}_j$$

Contaminación del historial:

$$H_{\text{ctx}}(t) = \frac{\text{superseded} + \text{traces}}{\max(1,\ \text{tokens})}$$

## Detectores

| detector | recall | false_alarm | f1 | f1_shadowing | f1_thrashing | f1_goal_drift |
| --- | --- | --- | --- | --- | --- | --- |
| D1_RawCosineOnly | 0.33333333333333331 | 0 | 0.5 | 0 | 0 | 1 |
| D2_WhitenedKinematicsOnly | 0.33333333333333331 | 0 | 0.5 | 0 | 0 | 1 |
| D3_FullGovernor_Kinematics_Plus_AST | 1 | 0 | 1 | 1 | 1 | 1 |

## ContextCompiler

| mean_original_tokens | mean_compiled_tokens | mean_token_savings_ratio | invariant_retention_rate | live_signature_retention_rate | obsolete_code_pruning_rate | mean_compile_latency_ms |
| --- | --- | --- | --- | --- | --- | --- |
| 265000 | 35968.5 | 0.86426981132075476 | 1 | 1 | 1 | 41.66616662450906 |

## Veredicto

- overall_winner: D3_FullGovernor_Kinematics_Plus_AST
- governor_beats_raw_cosine: True
- compiler_meets_contract: True

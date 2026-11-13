# Test A — Duelo de subespacio blanqueado contra coseno

Los números salen de `summarize_detection` y `determine_test_a_verdict`.
El JSON hermano guarda los float nativos; esta tabla usa `format(x, '.17g')`.

## Fórmulas

Margen de coseno por chunk, con umbral conformal \(\tau = q_{\hat{}}\):

$$\tau:\ s_{\cos}(\hat{x}) = \max_{b} (\hat{x}^{\top} \hat{\mu}_{b}) - (\hat{x}^{\top} \hat{\mu}_{\text{python}})$$

Score del subespacio blanqueado:

$$s_{\text{EEB}}(x) = 0.50\,\tilde{z}_{\text{fisher}}(x) + 0.20\,\tilde{z}_{\parallel}(x) + 0.30\,\tilde{z}_{\perp}(x)$$

Dirección de Fisher en el espacio original:

$$\vec{w}^{\top} \vec{x}$$

## Comparación

| modelo | roc_auc | pr_auc | far_at_frr_01 | far_at_frr_05 | frr_total | far_total | frr_business_python | far_piggybacking |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1_DDI_v040 | 0.79731968810916176 | 0.94151418331590864 | 0.69736842105263153 | 0.49473684210526314 | 0.07407407407407407 | 0.45263157894736844 | 0.33333333333333331 | 0.45555555555555555 |
| M2_Cosine | 0.89523635477582841 | 0.96952344653276235 | 0.48684210526315791 | 0.25526315789473686 | 0.046296296296296294 | 0.26052631578947366 | 0.27777777777777779 | 0.33333333333333331 |
| M3_EEB_Pure | 0.89452972709551659 | 0.97251415468673441 | 0.23684210526315788 | 0.23421052631578948 | 0.018518518518518517 | 0.23684210526315788 | 0.1111111111111111 | 0.33333333333333331 |
| M4_Hybrid_AST_EEB | 0.99975633528265107 | 0.99993046966100185 | 0.005263157894736842 | 0 | 0.018518518518518517 | 0 | 0.1111111111111111 | 0 |

## Desglose por subcategoría

| modelo | frr_stdlib_python | frr_business_python | far_seen_domain | far_unseen_domain_ood | far_other_language | far_piggybacking |
| --- | --- | --- | --- | --- | --- | --- |
| M1_DDI_v040 | 0.022222222222222223 | 0.33333333333333331 | 0.125 | 0.40666666666666668 | 1 | 0.45555555555555555 |
| M2_Cosine | 0 | 0.27777777777777779 | 0 | 0.059999999999999998 | 1 | 0.33333333333333331 |
| M3_EEB_Pure | 0 | 0.1111111111111111 | 0 | 0 | 1 | 0.33333333333333331 |
| M4_Hybrid_AST_EEB | 0 | 0.1111111111111111 | 0 | 0 | 0 | 0 |

## Latencia de scoring

| modelo | p50_ms | p95_ms | p99_ms |
| --- | --- | --- | --- |
| M1_DDI_v040 | 0.5621250020340085 | 2.3983505518117361 | 3.7943411305604946 |
| M2_Cosine | 0.010583004041109234 | 0.038845953531563282 | 0.066046590654877946 |
| M3_EEB_Pure | 0.017207996279466897 | 0.030651650376967154 | 0.036319037026260048 |
| M4_Hybrid_AST_EEB | 0.018083999748341739 | 0.03224550164304673 | 0.035792170529020936 |

## Veredicto

- overall_winner: M4_Hybrid_AST_EEB
- pure_embedding_winner: M2_Cosine
- m3_beats_cosine_empirically: False
- m1_ddi_v040_viable: False

## Entorno

- dispositivo: Apple M4
- target_pytorch: mps:0
- memoria_ram: 16 GB unificada
- sistema_operativo: macOS-26.7.1-arm64-arm-64bit-Mach-O
- version_python: 3.14.3
- version_pytorch: 2.14.0
- version_numpy: 2.5.3
- timestamp_iso: 2026-11-09T19:32:57.955216-03:00

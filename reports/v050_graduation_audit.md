# Graduación v0.5.0 — auditoría M3/M4

Los números salen de `summarize_detection` y de predicados booleanos del runner.
El JSON hermano guarda los float nativos; esta tabla usa `format(x, '.17g')`.

## Fórmulas

Dirección de Fisher en el espacio original:

$$\vec{w}^{\top} \vec{x}$$

Umbral conformal sobre los 72 grupos positivos de calibración:

$$\hat{q}_{1-\alpha} = s_{\mathrm{cal}}\left(\left\lceil (n_{\mathrm{cal}}+1)(1-\alpha)\right\rceil\right)$$

Ajuste híbrido por chunk:

$$s_{\mathrm{adj}}(c) = s_{\mathrm{EEB}}(c) + \begin{cases} -1.5 & \text{si el AST de Python es válido} \\ +6.0 & \text{si } c \in \{\text{fenced\_code},\text{foreign\_code}\} \\ 0 & \text{en otro caso} \end{cases}$$

Fracción de falsos aceptados en código ajeno:

$$\mathrm{FAR}_{\mathrm{lang}} = \frac{n_{\mathrm{miss}}}{n_{\mathrm{lang}}}$$

## Comparación

| variante | modelo | roc_auc | pr_auc | far_other_language | far_total | frr_total |
| --- | --- | --- | --- | --- | --- | --- |
| prose_only_negatives | M3_WhitenedSpectralSubspace | 0.89452972709551659 | 0.97251415468673441 | 1 | 0.23684210526315788 | 0.018518518518518517 |
| prose_only_negatives | M4_HybridAstSpectral | 0.99975633528265107 | 0.99993046966100185 | 0 | 0 | 0.018518518518518517 |
| multilang_hardened_negatives | M3_WhitenedSpectralSubspace | 0.95004873294346981 | 0.98611545532403155 | 0.98333333333333328 | 0.23157894736842105 | 0.018518518518518517 |
| multilang_hardened_negatives | M4_HybridAstSpectral | 0.99997563352826513 | 0.99999309296864203 | 0 | 0 | 0.018518518518518517 |

## Veredicto

- m4_other_language_far_improved: True
- npz_roundtrip_bitwise: True
- cache_reused: True
- graduation_ready: True
- cache_first_misses: 2
- cache_second_hits: 2
- cache_second_misses: 0
- elapsed_first_s: 0.058953291998477653
- elapsed_second_s: 0.00016179199155885726
- wall_clock_speedup: 364.37707101857023

## Entorno

- dispositivo: Apple M4
- target_pytorch: mps:0
- memoria_ram: 16 GB unificada
- sistema_operativo: macOS-26.7.1-arm64-arm-64bit-Mach-O
- version_python: 3.14.3
- version_pytorch: 2.14.0
- version_numpy: 2.5.3
- timestamp_iso: 2026-11-13T17:49:24.045634-03:00

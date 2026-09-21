# Auditoría numérica — corrida 2026-09-21

`BAAI/bge-m3`, pesos float32. N1 y N2 en serie: primero `mps:0`, se suelta el modelo, después CPU. N3 no se corrió. N4 lee `ddi_fw/out/rows.npz` y usa el `gap` de los ejes disjuntos, no la distancia de las frases al borde de su propia caja.

| Métrica | Umbral | Medido | Estado |
| :--- | :--- | :--- | :--- |
| N1 `max_abs` | `1.1920928955078125e-07` | `1.2817326933145523e-07` | `FAIL` |
| N1 bitwise | true | false | `FAIL` |
| N1 MAE | | `3.2589571929975136e-08` | |
| N2 `delta_max` | piso | `2.4586915969848633e-07` | `PASS` |
| N2 L2 | piso | `2.2066446945245843e-06` | `PASS` |
| N3 | excluida | no corrida | `SKIP` |
| N4 `min_gap` | | `0.0005808807909488678` | |
| N4 factor | 100 | `2362.560606060606` | `IMMUNE` |

N1: la misma frase sola y dentro de un batch con relleno no sale idéntica bit a bit. El peor eje se mueve un poco por encima del epsilon de float32.

N4: el hueco más chico de una pared ya publicada es unas 2362 veces el piso MPS–CPU. Esa pared no la voltea esta deriva. Esto no reabre la resonancia, que quedó `rechazada` en [`resonancia-cierre.md`](./resonancia-cierre.md).

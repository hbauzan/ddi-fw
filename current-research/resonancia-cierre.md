# Cierre de la resonancia armónica

Resultado: `rechazada`.

Enteros crudos en `resonancia-cierre.json`. Sin redondeo. Sin coseno.

Fuente: `ddi_fw/out/extended_bge/rows.npz`, `model_id=BAAI/bge-m3`, dtype `float32`.
Los vectores ya estaban guardados. Esta corrida no cargó el modelo: los textos de las cinco almas coinciden con el mazo.

T0 pasó. T2 (diez pares): `false`. T3 (dos mitades de python): `false`.

En los diez pares, las 54 cláusulas held-out de cada tema tienen `solo_foreign > 0`. Ninguna pasa el predicado. El otro lado del predicado sí se cumple: ninguna cláusula held-out del tema ajeno pasa la puerta del tema nativo (`heldB_wrongly_pass_A = 0` en los diez pares).

Ejemplo `python_receta`, held-out de python: `solo_native` entre 54 y 100 (piso del fit: 86), `solo_foreign` entre 9 y 38. Las 54 fallan. T3 también falla: `solo_foreign` de `held_L` entre 29 y 62, piso 54.

| Par | Pasa | minimo_fit_a | minimo_fit_b | held-out que no cumple |
| :--- | :--- | ---: | ---: | ---: |
| `python_receta` | `false` | 86 | 74 | 108 |
| `python_legal` | `false` | 61 | 60 | 108 |
| `legal_receta` | `false` | 84 | 79 | 108 |
| `python_medicina` | `false` | 60 | 65 | 108 |
| `python_astronomia` | `false` | 55 | 68 | 108 |
| `legal_medicina` | `false` | 70 | 76 | 108 |
| `legal_astronomia` | `false` | 65 | 85 | 108 |
| `receta_medicina` | `false` | 61 | 66 | 108 |
| `receta_astronomia` | `false` | 67 | 86 | 108 |
| `medicina_astronomia` | `false` | 54 | 48 | 108 |

T3 minimo_fit_L=54, minimo_fit_R=59.

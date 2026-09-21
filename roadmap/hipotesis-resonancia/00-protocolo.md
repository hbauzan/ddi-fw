# Cierre de la hipótesis de resonancia armónica

Estado: `rechazada` el 2026-09-21. Medición en [`../../current-research/resonancia-cierre.md`](../../current-research/resonancia-cierre.md). Este archivo fijó el veredicto antes de medir.

Hipótesis: una cláusula que no entró en las cajas se asigna a su tema por conteos enteros de coordenadas. Python queda del lado python y receta del lado receta. Dos mitades del mismo tema no pasan la misma regla.

La pared de un eje (`gap > 0`) no entra en este veredicto. El censo de cláusulas que ya están dentro de su caja tampoco.

Norma numérica: [`../../current-research/universal-remediation-directive.md`](../../current-research/universal-remediation-directive.md).

## Reglas fijas

- Mazos: `ddi_fw/data/extended/` (110 cláusulas por alma). Partición congelada en [`splits.json`](./splits.json). No se reordena, no se poda, no se sortea.
- Motor único: `BAAI/bge-m3`. Pesos float32. Salida float32. Qwen2 queda afuera: carga pesos en float16 y la directiva prohíbe float16 en el camino de decisión.
- Cajas: mínimo y máximo float32 de las filas `fit`, por eje. Sin `round`, sin `:.Nf`, sin holgura.
- Una cláusula `fit` no se puntúa como evidencia. Si un id está en `fit` y en `held_out`, el protocolo se aborta.
- Votos, por eje, de un vector que no armó las cajas:
  - `solo_a`: cae en la caja A y no en la caja B
  - `solo_b`: cae en la caja B y no en la caja A
  - `ambas`: cae en las dos
  - `ninguna`: no cae en ninguna
- Los conteos son enteros. No hay umbral continuo, ni coseno, ni media, ni `alpha`.

## Predicado

Para un held-out del tema A, con cajas hechas solo con el `fit` de A y el `fit` de B:

- pasa si `solo_b == 0` y `solo_a >= minimo_fit_a`
- `minimo_fit_a` es el menor `solo_a` entre las cláusulas `fit` de A, puntuadas contra esas mismas cajas

`minimo_fit_a` se calcula en el fit. El held-out no lo mueve.

## Tests

### T0 — La partición no se toca

`splits.json` cubre cada alma una sola vez. `fit` y `held_out` son disjuntos. El control `same_alma_python` cubre python una sola vez y sus cuatro grupos son disjuntos. Si esto falla, no se embebe.

### T1 — Cajas solo con fit

Embebe el `fit` de las cinco almas con BGE-M3, un proceso por alma. Guarda `rows` float32 en binario. Las cajas salen de esas matrices. El held-out no entra al mínimo ni al máximo.

### T2 — Held-out de los diez pares

Pares canónicos: `python_receta`, `python_legal`, `legal_receta`, `python_medicina`, `python_astronomia`, `legal_medicina`, `legal_astronomia`, `receta_medicina`, `receta_astronomia`, `medicina_astronomia`.

Para cada par y cada cláusula held-out, anotar `solo_a`, `solo_b`, `ambas`, `ninguna` como enteros.

El par pasa solo si las dos cosas se cumplen:

1. Cada held-out de A pasa el predicado contra B.
2. Cada held-out de B no pasa el predicado de A. Simétrico: cada held-out de B pasa el suyo, y cada held-out de A no pasa el de B.

Un par que falla deja la hipótesis rechazada. No se descarta la cláusula que falló.

### T3 — Control de la misma alma

Usa `same_alma_python` en `splits.json`. Cajas de `fit_L` y `fit_R`, las dos son python.

Puntúa `held_L` con nativo = `fit_L` y ajeno = `fit_R`. Puntúa `held_R` al revés. El mismo predicado que T2.

El control pasa el predicado si cada held-out queda del lado de su mitad y no del lado de la otra mitad.

### T4 — Cierre

Un solo resultado, escrito en `current-research/` con los enteros crudos. Sin redondeo.

| Resultado | Condición |
| :--- | :--- |
| `confirmada` | T2 pasa en los diez pares y T3 no pasa el predicado. |
| `rechazada` | T2 falla en algún par, o T3 pasa el mismo predicado. |
| `abortada` | T0 falla, el embedder no es float32, o un id de fit aparece en el held-out. |

`confirmada` significa que el tema separa y el tamaño de la muestra no. `rechazada` cierra la hipótesis en estos mazos y este motor. No hay tercer estado de "casi".

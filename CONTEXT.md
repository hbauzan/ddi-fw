# CONTEXT — Deep Dimensional Inspector Firewall

Glosario de dominio. Un término canónico por concepto.

## Alma

Mazo chico y homogéneo de cláusulas de un oficio (`python`, `legal`, `receta`, `medicina`, `astronomia`). No es un corpus masivo ni un sitio scrapeado.

_Avoid_: dataset, corpus, dominio difuso, categoría.

## Cláusula

Unidad lógica de texto que se embebe y se juzga sola. El splitter la corta por puntuación terminal sin romper decimales.

_Avoid_: oración vaga, chunk, token window.

## Fila

Vector denso de una cláusula. Misma cláusula + mismo embedder pinneado → misma fila.

## Hoja

Por cada eje, los intervalos empíricos `[lo, hi]` de dos almas. Sin medias. Sin top-k.

## Eje disjunto

Dimensión donde los intervalos de las dos almas no se tocan (`gap > 0`). Es la pared de un eje del candado de producto. No es la hipótesis de resonancia.

## Corte duro

Etiqueta `left` / `right` / `split` / `out` decidida **solo** en ejes disjuntos. Las demás dimensiones votan para bitácora, no para el veredicto de producto.

## Candado

Hoja + ejes disjuntos de un par. Se **publica** solo si hay al menos un eje disjunto. Cero disjuntos → se poda el mazo, nunca se inventa holgura.

## Resonancia armónica

Hipótesis abierta: una cláusula que no armó las cajas se separa de otro tema por conteos enteros de coordenadas (`solo` nativo y `solo` ajeno). No está confirmada. El protocolo de cierre está en `roadmap/hipotesis-resonancia/`.

## Voto

Por eje: `solo_a` | `solo_b` | `ambas` | `ninguna` según inclusión en los intervalos.

## Política

Conjunto de almas autorizadas y vedadas. El demo autoriza `python` y veta `receta` y `legal`.

## Ingress

Partición del prompt en cláusulas y veredicto fail-closed: una BREACH tumba el prompt entero.

## Egreso hold

Retención total de la respuesta del LLM. Cero tokens al cliente hasta el veredicto. Misma geometría que ingress.

## Piggyback

Ataque que mezcla oficios en un mismo prompt. Las cláusulas aisladas no pueden esconderse en un promedio angular.

## Press

Censo fila por fila de un `rows.npz` ya calibrado. No re-embebe. No publica campos `mean_*`.

## Precisión numérica

Norma: `current-research/universal-remediation-directive.md`.

Cada coordenada vive cerca de 0,025, en `[-0.15, +0.15]`. Una separación entre temas, si existe, vive entre `10^{-4}` y `10^{-6}`. El veredicto lee float32 nativo. Float16 no entra a ese camino. Prohibido `round` y los formatos `:.4f` / `:.6f`. La exportación a texto usa `f"{float(val):.17g}"` o `str(float(val))`. Un número corto en pantalla lleva la marca `display-only rounding; engine unrounded` y no toca el dato.

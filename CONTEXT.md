# CONTEXT — Deep Dimensional Inspector Firewall

Glosario de dominio. Un término canónico por concepto.

## Alma

Mazo chico y homogéneo de cláusulas de un oficio (`python`, `legal`, `receta`). No es un corpus masivo ni un sitio scrapeado.

_Avoid_: dataset, corpus, dominio difuso, categoría.

## Cláusula

Unidad lógica de texto que se embebe y se juzga sola. El splitter la corta por puntuación terminal sin romper decimales.

_Avoid_: oración vaga, chunk, token window.

## Fila

Vector denso de una cláusula. Misma cláusula + mismo embedder pinneado → misma fila.

## Hoja

Por cada eje, los intervalos empíricos `[lo, hi]` de dos almas. Sin medias. Sin top-k.

## Eje disjunto

Dimensión donde los intervalos de las dos almas no se tocan (`gap > 0`).

## Corte duro

Etiqueta `left` / `right` / `split` / `out` decidida **solo** en ejes disjuntos. Las demás dimensiones votan para bitácora, no para el veredicto.

## Candado

Hoja + ejes disjuntos de un par. Se **publica** solo si hay al menos un eje disjunto. Cero disjuntos → se poda el mazo, nunca se inventa holgura.

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

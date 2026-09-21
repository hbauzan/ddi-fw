# Pack vivo

La resonancia ya se midió. La auditoría numérica también.

## Resonancia armónica

Cerrada el 2026-09-21: `rechazada`. Medición en [`../current-research/resonancia-cierre.md`](../current-research/resonancia-cierre.md).

[`hipotesis-resonancia/00-protocolo.md`](./hipotesis-resonancia/00-protocolo.md)

- T0: ninguna frase de la caja está también en el held-out. Partición en [`splits.json`](./hipotesis-resonancia/splits.json).
- T1: las cajas salen solo del fit, en BGE float32.
- T2: se puntúan las frases que no armaron las cajas, en los diez pares.
- T3: lo mismo con dos mitades de python.
- T4: `confirmada` si T2 pasa y T3 no. `rechazada` si T2 falla o si T3 pasa igual. No hay "casi".

## Auditoría numérica

[`auditoria-numerica/00-indice.md`](./auditoria-numerica/00-indice.md)

N1 batch y padding. N2 MPS y después CPU, un modelo a la vez. N3 excluida. N4 margen del corte, solo NumPy. No reemplaza T0–T4.

## Referencia

- Almas del demo: [`almas.md`](./almas.md)
- Alcance de producto: [`00-alcance.md`](./00-alcance.md)
- Norma numérica: [`../current-research/universal-remediation-directive.md`](../current-research/universal-remediation-directive.md)
- Rama `feat/hipotesis-deletor`: estacionada. No se mergea.

## Archivo

- Ola Q, cerrada: [`archive/ola-q/README.md`](./archive/ola-q/README.md)
- Baseline BGE v0.1: [`archive/v0.1-bge-m3/`](./archive/v0.1-bge-m3/)
- Lecturas que no cierran la resonancia: [`../current-research/archive/README.md`](../current-research/archive/README.md)

# Auditoría numérica

Corrida el 2026-09-21: [`../../current-research/auditoria-numerica.md`](../../current-research/auditoria-numerica.md). No reabre la resonancia.

Esa hipótesis sigue en [`../hipotesis-resonancia/00-protocolo.md`](../hipotesis-resonancia/00-protocolo.md):

- T0 revisa que ninguna frase de la caja esté también en el held-out.
- T1 arma las cajas solo con el fit, en BGE float32.
- T2 puntúa las frases que no armaron las cajas, en los diez pares.
- T3 hace lo mismo con dos mitades de python.
- T4 cierra: `confirmada` si T2 pasa y T3 no. `rechazada` si T2 falla o si T3 pasa igual. No hay "casi".

Esta carpeta no los corre y no los reemplaza.

Norma de precisión: [`../../current-research/universal-remediation-directive.md`](../../current-research/universal-remediation-directive.md).

Hardware: un solo `BAAI/bge-m3` residente. MPS y CPU no conviven. No hay pasadas de más, ni hilos, ni una multiplicación de fondo. El determinismo en frío ya está en `scripts/cold_embedding_determinism.py` (5 procesos, varianza de bit 0).

| ID | Qué mide | Hardware |
| :--- | :--- | :--- |
| [N1](./01-batch-padding.md) | La misma frase sola y dentro de un batch con relleno | Una carga, el device que elija el modelo |
| [N2](./02-mps-cpu.md) | La misma frase en MPS y después en CPU | Segunda carga, solo cuando la primera ya se soltó |
| [N3](./03-excluida-concurrencia.md) | No se hace | Quedó afuera |
| [N4](./04-margen-corte.md) | El hueco de los ejes disjuntos contra el piso de N2 | Solo NumPy, sin modelo |

No se calcula coseno. El piso de deriva es el máximo absoluto y la norma L2.

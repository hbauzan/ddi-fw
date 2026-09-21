# N4 — Margen del corte

Estado: spec. Sin código. Sin modelo.

## Qué se pregunta

Si el piso de deriva de N2 alcanza para voltear una pared de un eje ya publicada.

## Cómo

Solo NumPy. Lee un `rows.npz` que ya exista. Primero `ddi_fw/out/rows.npz`.

Arma la hoja con [`ddi_fw/hoja.py`](../../ddi_fw/hoja.py). El margen es el `gap` de los ejes con `gap > 0`.

No se mide la distancia de las frases que armaron la caja hasta `lo` y `hi`. Esas frases caen sobre el borde y esa distancia mínima es 0 por construcción.

```text
factor = min(gap) / max(delta_max de N2, eps de float32)
```

## Estados

| Estado | Cuándo |
| :--- | :--- |
| `SKIP` | No hay `rows.npz`, o no hay ningún eje con `gap > 0`. No se escribe `IMMUNE`. |
| `IMMUNE` | Hay ejes disjuntos, N2 corrió, y el factor es mayor que 100. |
| `FAIL` | Hay ejes disjuntos, N2 corrió, y el factor no llega a 100. |
| `SKIP` | N2 no produjo `delta_max`. No se inventa el denominador. |

Esto mira la pared de un eje del candado de producto. No es T2 ni T4 de la resonancia. Esas pruebas siguen en [`../hipotesis-resonancia/00-protocolo.md`](../hipotesis-resonancia/00-protocolo.md).

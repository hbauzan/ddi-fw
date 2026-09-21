# N1 — Batch y padding

Estado: spec. Sin código.

## Qué se pregunta

Si la misma frase, embebida sola, sale igual bit a bit cuando va en un batch con frases de largo distinto y el modelo rellena con padding.

## Cómo

Una sola carga de `BAAI/bge-m3` en float32, en el device que elija SentenceTransformer. En esta máquina eso es `mps:0`.

1. Frase sonda: `Explicá el funcionamiento de list.append en Python.`
2. Vector aislado: esa frase sola.
3. Batch de tres textos: la sonda, una frase de dos palabras, y un texto de unas 200 palabras armado en el momento, sin descargar nada.
4. Se toma la fila del batch que corresponde a la sonda.

## Qué se anota

Enteros y float32 nativos, exportados con `f"{float(val):.17g}"`.

- `max(abs(aislado - batch))`
- Promedio de ese absoluto
- Igualdad bit a bit de `tobytes`
- Contra `np.finfo(np.float32).eps`

`PASS` si el máximo absoluto es menor o igual que ese epsilon y los bytes coinciden. Si no, `FAIL`. El fallo se anota. No se relaja el epsilon para que pase.

## Qué no hace

No carga un segundo modelo. No corre en hilos. No toca `decide()`. No usa las frases del protocolo de resonancia.

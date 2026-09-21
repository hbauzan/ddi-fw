# N2 — MPS contra CPU

Estado: spec. Sin código.

## Qué se pregunta

Cuánto se mueve la misma frase al pasar de los kernels de Apple MPS a la CPU, los dos en float32.

## Cómo

En serie, nunca juntos.

1. Termina N1.
2. Se suelta el modelo. `gc`. Si existe `torch.mps.empty_cache()`, se llama.
3. Recién ahí se carga `BAAI/bge-m3` otra vez, con `device="cpu"` y dtype float32.
4. La misma frase sonda que N1.

Un solo modelo en memoria. BGE en este equipo ya ocupó entre 1 y 3 GB. Dos copias a la vez no entran en esta spec.

## Qué se anota

- `delta_max`: el máximo absoluto coordenada a coordenada
- Norma L2 de la resta

Esas dos cifras son el piso de deriva entre hardwares. No se anota coseno.

Si la segunda carga no llega a correr, N4 no inventa un piso.

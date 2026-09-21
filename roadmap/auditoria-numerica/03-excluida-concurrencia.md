# N3 — Concurrencia y jitter térmico

Estado: excluida. No se especifica para correr. No se escribe código.

## Qué pedía la spec original

100 forwards de la frase sonda, en hilos o con una multiplicación de matrices de fondo. Después, varianza bit a bit y cuántos SHA-256 distintos aparecen.

## Por qué no

MPS no admite varios forwards a la vez sobre el mismo modelo. Hilos más una carga de fondo sostienen la GPU y pueden tirar el proceso. La prueba está armada para calentar el equipo. Eso queda afuera.

Repetir la frase menos veces, en caliente y en un solo hilo, no reemplaza esta prueba: no mide contención, y el caso en frío ya dio varianza de bit 0 en cinco procesos aislados (`scripts/cold_embedding_determinism.py`).

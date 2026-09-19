# D06 — Proxy OpenAI-compatible

> **Estado:** hecho  
> **Ola:** 4  
> **Especificación:** [`../00-alcance.md`](../00-alcance.md)

---

## Objetivo

Implementar un servicio HTTP independiente y compatible con la API de OpenAI (`POST /v1/chat/completions`) que evalúe el prompt entrante mediante el Ingress (`D04`), invoque a un proveedor de LLM configurado (ej. Ollama o vLLM), y entregue la respuesta únicamente si supera la retención del Egreso Hold (`D05`).
- El LLM es un generador de lenguaje, pero `ddi-fw` es la autoridad de seguridad inapelable.

---

## Dependencias

- **Depende de:** `D04` (Ingress por cláusulas) y `D05` (Egreso Hold).
- **Desbloquea:** Herramienta completamente utilizable en producción y conectable a interfaces de chat o agentes.
- **Paralelo con:** Ninguno.

---

## Archivos de Referencia

- [`../00-alcance.md`](../00-alcance.md): Especificación de la superficie HTTP.

---

## Archivos a Crear / Modificar

- `ddi_fw/proxy.py`: Aplicación ASGI minimalista (FastAPI / Starlette) con endpoints de salud y chat completions.
- `ddi_fw/config.py`: Gestión de configuración por variables de entorno (`DDI_UPSTREAM_URL`, `DDI_UPSTREAM_MODEL`, `DDI_PORT`).
- `tests/test_ddi_proxy.py`: Suite de tests de integración con mock del LLM upstream (utilizando httpx/ASGITransport).

---

## Fuera de Alcance

- Protocolos complejos de autenticación corporativa o integración con Identity Providers.
- Streaming SSE de tokens (el Egreso Hold requiere la respuesta consolidada antes de liberar datos).
- Carga innecesaria del modelo BGE-M3 durante las pruebas del servidor HTTP.

---

## Tareas

- [ ] Crear aplicación ASGI con endpoints:
  - `GET /healthz`: Verificación de estado y disponibilidad de candados.
  - `POST /v1/chat/completions`: Endpoint principal estándar.
- [ ] Aplicar Ingress (`D04`) sobre el último mensaje de usuario (`messages[-1]`). Si se detecta `BREACH`, retornar HTTP 403 con cuerpo explicativo estructurado, **sin reproducir el prompt bloqueado**.
- [ ] Implementar cliente hacia upstream configurable vía variables de entorno (`DDI_UPSTREAM_URL`, `DDI_UPSTREAM_MODEL`) con timeout estricto.
- [ ] Aplicar Egreso Hold (`D05`) sobre el texto generado por el LLM. Si se detecta `BREACH`, denegar la entrega y retornar error de contención de salida.
- [ ] Tests de integración con cliente ASGI mockeando respuestas del upstream.
- [ ] Documentar en `README.md` el comando para levantar el proxy junto a una instancia local de Ollama.

---

## Pruebas (TDD)

```bash
uv run pytest -q tests/test_ddi_proxy.py
```

---

## Definición de Hecho (DoD)

- [ ] Proxy HTTP operativo en puerto configurable.
- [ ] Ingress y Egreso Hold integrados de forma transparente en el ciclo de vida de la petición.
- [ ] Tests pasando con upstream mockeado sin levantar modelos pesados.
- [ ] Fila `D06` actualizada a `hecho` en [`../README.md`](../README.md).

---

## Prompt Copiable para Ejecución

```text
Pack ddi-fw, ticket D06. Lee roadmap/00-alcance.md.
Implementa el proxy HTTP OpenAI-compatible en ddi_fw/proxy.py conectando Ingress (D04) y Egreso Hold (D05).
Mockea el LLM upstream en los tests con httpx.
Verifica con: uv run pytest tests/test_ddi_proxy.py.
Al cerrar, marca D06 como hecho en roadmap/README.md.
```

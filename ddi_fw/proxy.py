"""Proxy OpenAI-compatible. ddi-fw juzga; el LLM solo genera."""

from __future__ import annotations

import time
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ddi_fw.config import Settings
from ddi_fw.egreso import hold
from ddi_fw.embedder import BaseEmbedder, FakeEmbedder, get_embedder, load_rows, rows_matrices
from ddi_fw.hoja import candados_canonicos
from ddi_fw.ingress import Policy, decide, inspect_prompt


def _last_user_text(messages: list[dict[str, Any]]) -> str | None:
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content
            if isinstance(content, list):
                parts = [str(part.get("text", "")) for part in content if isinstance(part, dict)]
                joined = "".join(parts).strip()
                if joined:
                    return joined
    return None


def _error(
    status: int, error_type: str, message: str, audit: list[dict[str, object]] | None = None
) -> JSONResponse:
    body: dict[str, Any] = {"error": {"type": error_type, "message": message}}
    if audit is not None:
        body["error"]["audit"] = audit
    return JSONResponse(status_code=status, content=body)


def create_app(
    settings: Settings | None = None,
    *,
    embedder: BaseEmbedder | None = None,
    candados: dict | None = None,
    transport: httpx.BaseTransport | None = None,
) -> FastAPI:
    cfg = settings or Settings()
    policy = Policy(allowed=cfg.allowed_alma, forbidden=cfg.forbidden_set())
    worker = embedder or FakeEmbedder()
    locks = candados
    if locks is None and cfg.rows_path.is_file():
        locks = candados_canonicos(rows_matrices(load_rows(cfg.rows_path)))
    locks = locks or {}

    app = FastAPI(title="ddi-fw", version="0.1.0")
    app.state.settings = cfg
    app.state.embedder = worker
    app.state.candados = locks
    app.state.policy = policy

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        lock_view = {
            key: {"published": lock.published, "disjoint_count": lock.disjoint_count}
            for key, lock in app.state.candados.items()
        }
        required_ok = all(
            lock.published
            for lock in app.state.candados.values()
            if cfg.allowed_alma in {lock.hoja.alma_a, lock.hoja.alma_b}
        )
        status = "ok" if lock_view and required_ok else "degraded"
        return {
            "status": status,
            "embedder": worker.model_id,
            "locks": lock_view,
        }

    def decide_clause(clause: str):
        vector = worker.embed_text(clause)
        return decide(vector, app.state.candados, policy)

    async def call_upstream(payload: dict[str, Any]) -> tuple[int, dict[str, Any] | None, str]:
        url = cfg.upstream_url.rstrip("/") + "/chat/completions"
        outbound = dict(payload)
        outbound["stream"] = False
        outbound.setdefault("model", cfg.upstream_model)
        timeout = httpx.Timeout(cfg.request_timeout_seconds)
        try:
            async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
                response = await client.post(url, json=outbound)
        except httpx.HTTPError as exc:
            return 502, None, f"upstream_error:{exc.__class__.__name__}"
        try:
            data = response.json()
        except ValueError:
            return 502, None, "upstream_bad_json"
        if response.status_code >= 400:
            return 502, None, f"upstream_http:{response.status_code}"
        return 200, data, ""

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request) -> JSONResponse:
        try:
            payload = await request.json()
        except Exception:
            return _error(400, "ddi_bad_request", "json inválido")
        if payload.get("stream") is True:
            return _error(400, "ddi_stream_forbidden", "egreso hold: streaming prohibido")
        messages = payload.get("messages")
        if not isinstance(messages, list):
            return _error(400, "ddi_bad_request", "messages requerido")
        user_text = _last_user_text(messages)
        if user_text is None:
            return _error(400, "ddi_bad_request", "falta mensaje de usuario")

        ingress = inspect_prompt(user_text, worker, app.state.candados, policy)
        if ingress.verdict == "BREACH":
            return _error(403, "ddi_ingress_breach", "contención de entrada", ingress.audit)

        status, upstream, reason = await call_upstream(payload)
        if status != 200 or upstream is None:
            return _error(502, "ddi_upstream_error", reason or "upstream")

        try:
            generated = upstream["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return _error(502, "ddi_upstream_error", "upstream_shape")
        if not isinstance(generated, str):
            return _error(502, "ddi_upstream_error", "upstream_content")

        held = hold(generated, decide_clause)
        if held.status == "BLOCKED":
            audit = [
                {
                    "verdict": decision.verdict,
                    "alma_asignada": decision.alma_asignada,
                    "reason": decision.reason,
                    "pair_labels": decision.pair_labels,
                }
                for decision in held.decisions
            ]
            return _error(403, "ddi_egreso_breach", "contención de salida", audit)

        completion = {
            "id": f"ddi-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": payload.get("model") or cfg.upstream_model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": held.text},
                    "finish_reason": "stop",
                }
            ],
            "usage": upstream.get("usage", {}),
        }
        return JSONResponse(status_code=200, content=completion)

    return app


def load_runtime(settings: Settings | None = None) -> tuple[Settings, BaseEmbedder, dict]:
    cfg = settings or Settings()
    worker = get_embedder(cfg.embedder)
    if not cfg.rows_path.is_file():
        raise FileNotFoundError(f"calibrá primero: falta {cfg.rows_path}")
    locks = candados_canonicos(rows_matrices(load_rows(cfg.rows_path)))
    return cfg, worker, locks


def main(argv: list[str] | None = None) -> int:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Proxy OpenAI-compatible de ddi-fw.")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args(argv)
    cfg, worker, locks = load_runtime()
    app = create_app(cfg, embedder=worker, candados=locks)
    uvicorn.run(app, host=args.host or cfg.host, port=args.port or cfg.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

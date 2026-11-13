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
from ddi_fw.lab_v2.context_compiler import compile_session_context
from ddi_fw.v2_calibration import load_v2_calibration
from ddi_fw.v2_firewall import SpectralAstFirewall


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


def _content_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(str(part.get("text", "")))
        return "".join(parts)
    return ""


def _normalized_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"role": str(message.get("role", "user")), "content": _content_text(message)}
        for message in messages
        if isinstance(message, dict)
    ]


def create_app(
    settings: Settings | None = None,
    *,
    embedder: BaseEmbedder | None = None,
    candados: dict | None = None,
    v2_firewall: SpectralAstFirewall | None = None,
    transport: httpx.BaseTransport | None = None,
) -> FastAPI:
    cfg = settings or Settings()
    policy = Policy(allowed=cfg.allowed_alma, forbidden=cfg.forbidden_set())
    worker = embedder or FakeEmbedder()
    locks = candados
    if locks is None:
        target_rows = None
        if cfg.trilingual_rows_path.is_file():
            target_rows = cfg.trilingual_rows_path
        elif cfg.rows_path.is_file():
            target_rows = cfg.rows_path

        if target_rows is not None:
            from ddi_fw.hoja import RUIDO_UNIVERSAL_BGE_M3

            matrices = rows_matrices(load_rows(target_rows))
            ruido = RUIDO_UNIVERSAL_BGE_M3 if (cfg.podar_ruido or cfg.prune_paja) else None
            locks = candados_canonicos(
                matrices,
                ruido_indices=ruido,
                modo_espectral=cfg.spectral_mode,
                quorum_ratio=cfg.quorum_ratio,
            )
    locks = locks or {}
    firewall = v2_firewall
    active_engine_mode = "v1_boxes"
    if firewall is not None or cfg.engine_mode == "v2_spectral_ast":
        active_engine_mode = "v2_spectral_ast"
        if firewall is None and cfg.v2_calibration_path.is_file():
            model, _meta = load_v2_calibration(cfg.v2_calibration_path)
            firewall = SpectralAstFirewall(model, worker)

    app = FastAPI(title="ddi-fw", version="0.5.0")
    app.state.settings = cfg
    app.state.embedder = worker
    app.state.candados = locks
    app.state.policy = policy
    app.state.v2_firewall = firewall
    app.state.engine_mode = active_engine_mode

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        lock_view = {
            key: {
                "published": lock.published,
                "disjoint_count": lock.disjoint_count,
                "is_spectral": lock.is_spectral,
                "quorum_min": lock.quorum_min,
            }
            for key, lock in app.state.candados.items()
        }
        required_ok = all(
            lock.published
            for lock in app.state.candados.values()
            if cfg.allowed_alma in {lock.hoja.alma_a, lock.hoja.alma_b}
        )
        if app.state.engine_mode == "v2_spectral_ast":
            status = "ok" if app.state.v2_firewall is not None else "degraded"
        else:
            status = "ok" if lock_view and required_ok else "degraded"
        return {
            "status": status,
            "embedder": worker.model_id,
            "spectral_mode": cfg.spectral_mode,
            "locks": lock_view,
            "version": "0.5.0",
            "engine_mode": app.state.engine_mode,
            "context_compiler_enabled": bool(cfg.context_compiler_enabled),
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

        if app.state.engine_mode == "v2_spectral_ast":
            if app.state.v2_firewall is None:
                return _error(
                    403,
                    "ddi_ingress_breach",
                    "v2_firewall_uncalibrated",
                    [{"reason": "v2_firewall_uncalibrated"}],
                )
            ingress_v2 = app.state.v2_firewall.inspect_messages(messages)
            if ingress_v2.verdict == "BREACH":
                return _error(403, "ddi_ingress_breach", ingress_v2.reason, ingress_v2.audit)
        else:
            ingress = inspect_prompt(user_text, worker, app.state.candados, policy)
            if ingress.verdict == "BREACH":
                return _error(403, "ddi_ingress_breach", "contención de entrada", ingress.audit)

        outbound = dict(payload)
        outbound.pop("ddi_compile_context", None)
        compiled = None
        if cfg.context_compiler_enabled or payload.get("ddi_compile_context") is True:
            compiled = compile_session_context(
                _normalized_messages(messages),
                max_budget_tokens=cfg.context_max_budget_tokens,
                fresh_tail_turns=cfg.context_fresh_tail_turns,
            )
            outbound["messages"] = compiled.messages

        status, upstream, reason = await call_upstream(outbound)
        if status != 200 or upstream is None:
            return _error(502, "ddi_upstream_error", reason or "upstream")

        try:
            generated = upstream["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return _error(502, "ddi_upstream_error", "upstream_shape")
        if not isinstance(generated, str):
            return _error(502, "ddi_upstream_error", "upstream_content")

        if app.state.engine_mode == "v2_spectral_ast":
            egress_v2 = app.state.v2_firewall.inspect_text(generated, role="assistant")
            if egress_v2.verdict == "BREACH":
                return _error(403, "ddi_egreso_breach", egress_v2.reason, egress_v2.audit)
            visible = generated
        else:
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
            visible = held.text

        completion = {
            "id": f"ddi-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": payload.get("model") or cfg.upstream_model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": visible},
                    "finish_reason": "stop",
                }
            ],
            "usage": upstream.get("usage", {}),
        }
        if compiled is not None:
            completion["ddi_context_governor"] = {
                "original_tokens": compiled.original_tokens,
                "compiled_tokens": compiled.compiled_tokens,
                "compression_ratio": float(compiled.compression_ratio),
                "superseded_blocks_pruned": compiled.superseded_blocks_pruned,
                "stale_traces_pruned": compiled.stale_traces_pruned,
            }
        return JSONResponse(status_code=200, content=completion)

    return app


def load_runtime(settings: Settings | None = None) -> tuple[Settings, BaseEmbedder, dict]:
    cfg = settings or Settings()
    worker = get_embedder(cfg.embedder)
    target_rows = None
    if cfg.trilingual_rows_path.is_file():
        target_rows = cfg.trilingual_rows_path
    elif cfg.rows_path.is_file():
        target_rows = cfg.rows_path
    if target_rows is None:
        raise FileNotFoundError(
            f"calibrá primero: falta {cfg.trilingual_rows_path} o {cfg.rows_path}"
        )

    from ddi_fw.hoja import RUIDO_UNIVERSAL_BGE_M3

    matrices = rows_matrices(load_rows(target_rows))
    ruido = RUIDO_UNIVERSAL_BGE_M3 if (cfg.podar_ruido or cfg.prune_paja) else None
    locks = candados_canonicos(
        matrices,
        ruido_indices=ruido,
        modo_espectral=cfg.spectral_mode,
        quorum_ratio=cfg.quorum_ratio,
    )
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

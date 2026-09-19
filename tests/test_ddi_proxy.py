"""D06 — proxy ASGI con upstream mockeado. Sin BGE-M3."""

from __future__ import annotations

import httpx
from fastapi.testclient import TestClient

from ddi_fw.config import Settings
from ddi_fw.proxy import create_app
from tests.world import (
    PIGGYBACK,
    PY,
    PYTHON_ANSWER,
    RECIPE_ANSWER,
    synthetic_embedder,
    synthetic_locks,
)


def _client(upstream_body: dict | None = None, status_code: int = 200) -> TestClient:
    payload = upstream_body or {
        "id": "up-1",
        "object": "chat.completion",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": PYTHON_ANSWER}}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=payload)

    settings = Settings(
        upstream_url="http://upstream.test/v1",
        upstream_model="mock",
        allowed_alma="python",
        forbidden_almas="receta,legal",
    )
    app = create_app(
        settings,
        embedder=synthetic_embedder(),
        candados=synthetic_locks(),
        transport=httpx.MockTransport(handler),
    )
    return TestClient(app)


def test_healthz_ok() -> None:
    response = _client().get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["locks"]["python_receta"]["published"] is True


def test_ingress_breach_is_403_without_prompt_echo() -> None:
    response = _client().post(
        "/v1/chat/completions", json={"messages": [{"role": "user", "content": PIGGYBACK}]}
    )
    assert response.status_code == 403
    body = response.json()
    assert body["error"]["type"] == "ddi_ingress_breach"
    dumped = response.text
    assert PIGGYBACK not in dumped
    assert "torta de chocolate" not in dumped


def test_egreso_breach_is_403() -> None:
    client = _client(
        {
            "choices": [{"message": {"role": "assistant", "content": RECIPE_ANSWER}}],
        }
    )
    response = client.post(
        "/v1/chat/completions", json={"messages": [{"role": "user", "content": PY}]}
    )
    assert response.status_code == 403
    assert response.json()["error"]["type"] == "ddi_egreso_breach"
    assert RECIPE_ANSWER not in response.text


def test_pass_returns_openai_shape() -> None:
    response = _client().post(
        "/v1/chat/completions", json={"messages": [{"role": "user", "content": PY}]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"]["content"] == PYTHON_ANSWER


def test_stream_forbidden_and_upstream_error() -> None:
    assert (
        _client()
        .post(
            "/v1/chat/completions",
            json={"stream": True, "messages": [{"role": "user", "content": PY}]},
        )
        .status_code
        == 400
    )
    broken = _client(status_code=500)
    response = broken.post(
        "/v1/chat/completions", json={"messages": [{"role": "user", "content": PY}]}
    )
    assert response.status_code == 502
    assert response.json()["error"]["type"] == "ddi_upstream_error"

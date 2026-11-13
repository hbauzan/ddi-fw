"""Slice 3 — proxy v0.5.0 con motor v2 y compilador de contexto."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from ddi_fw import __version__
from ddi_fw.config import Settings
from ddi_fw.lab_v2.context_compiler import compile_session_context
from ddi_fw.proxy import create_app
from ddi_fw.v2_calibration import save_v2_calibration
from ddi_fw.v2_firewall import SpectralAstFirewall
from tests.test_v050_firewall import _ATTACK, _BENIGN, _firewall, _separable_model, _TableEmbedder
from tests.world import PY, PYTHON_ANSWER, synthetic_embedder, synthetic_locks


def _settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "upstream_url": "http://upstream.test/v1",
        "upstream_model": "mock",
        "allowed_alma": "python",
        "forbidden_almas": "receta,legal",
    }
    base.update(overrides)
    return Settings(**base)


def _upstream(content: str, sink: dict[str, object] | None = None) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if sink is not None:
            sink["body"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            json={
                "id": "up-1",
                "object": "chat.completion",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            },
        )

    return httpx.MockTransport(handler)


def _v1_client(content: str = PYTHON_ANSWER, sink: dict[str, object] | None = None) -> TestClient:
    app = create_app(
        _settings(),
        embedder=synthetic_embedder(),
        candados=synthetic_locks(),
        transport=_upstream(content, sink),
    )
    return TestClient(app)


def test_package_and_healthz_default_to_v050_v1_boxes() -> None:
    project = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.5.0"' in project
    assert __version__ == "0.5.0"
    app = create_app(
        _settings(),
        embedder=synthetic_embedder(),
        candados=synthetic_locks(),
        transport=_upstream(PYTHON_ANSWER),
    )
    assert app.version == "0.5.0"
    body = TestClient(app).get("/healthz").json()
    assert body["status"] == "ok"
    assert body["embedder"] == "fake"
    assert body["spectral_mode"] is True
    assert "python_receta" in body["locks"]
    assert body["version"] == "0.5.0"
    assert body["engine_mode"] == "v1_boxes"
    assert body["context_compiler_enabled"] is False
    passed = TestClient(app).post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": PY}]},
    )
    assert passed.status_code == 200
    assert "ddi_context_governor" not in passed.json()


def test_v2_without_calibration_fails_closed(tmp_path: Path) -> None:
    app = create_app(
        _settings(
            engine_mode="v2_spectral_ast",
            v2_calibration_path=tmp_path / "missing.npz",
        ),
        embedder=synthetic_embedder(),
        candados=synthetic_locks(),
        transport=_upstream(PYTHON_ANSWER),
    )
    health = TestClient(app).get("/healthz").json()
    assert health["status"] == "degraded"
    assert health["engine_mode"] == "v2_spectral_ast"
    response = TestClient(app).post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": _BENIGN}]},
    )
    assert response.status_code == 403
    assert response.json()["error"]["type"] == "ddi_ingress_breach"
    assert response.json()["error"]["message"] == "v2_firewall_uncalibrated"
    assert _BENIGN not in response.text


def test_v2_blocks_ingress_and_egress_without_echo() -> None:
    firewall, _embedder, _benign_chunk, _attack_chunk = _firewall()
    sink: dict[str, object] = {}
    app = create_app(
        _settings(engine_mode="v2_spectral_ast"),
        embedder=_embedder,
        candados={},
        v2_firewall=firewall,
        transport=_upstream(_BENIGN, sink),
    )
    client = TestClient(app)
    assert client.get("/healthz").json()["status"] == "ok"
    passed = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": _BENIGN}]},
    )
    assert passed.status_code == 200
    assert passed.json()["choices"][0]["message"]["content"] == _BENIGN

    blocked = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": _ATTACK},
                {"role": "user", "content": _BENIGN},
            ]
        },
    )
    assert blocked.status_code == 403
    assert blocked.json()["error"]["type"] == "ddi_ingress_breach"
    assert blocked.json()["error"]["audit"]
    assert _ATTACK not in blocked.text
    assert _BENIGN not in blocked.text

    egress_app = create_app(
        _settings(engine_mode="v2_spectral_ast"),
        embedder=_embedder,
        candados={},
        v2_firewall=firewall,
        transport=_upstream(_ATTACK),
    )
    egress = TestClient(egress_app).post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": _BENIGN}]},
    )
    assert egress.status_code == 403
    assert egress.json()["error"]["type"] == "ddi_egreso_breach"
    assert _ATTACK not in egress.text
    assert sink["body"]["messages"][0]["content"] == _BENIGN


def test_v2_rejects_stream_and_missing_user() -> None:
    firewall, embedder, _benign_chunk, _attack_chunk = _firewall()
    client = TestClient(
        create_app(
            _settings(engine_mode="v2_spectral_ast"),
            embedder=embedder,
            v2_firewall=firewall,
            transport=_upstream(_BENIGN),
        )
    )
    stream = client.post(
        "/v1/chat/completions",
        json={"stream": True, "messages": [{"role": "user", "content": _BENIGN}]},
    )
    assert stream.status_code == 400
    missing = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "system", "content": _BENIGN}]},
    )
    assert missing.status_code == 400
    assert missing.json()["error"]["message"] == "falta mensaje de usuario"


def test_context_compiler_runs_for_either_engine_and_strips_the_flag() -> None:
    history = [{"role": "system", "content": "sistema " * 80}]
    for index in range(6):
        history.append({"role": "user", "content": f"borrador {index} " + ("relleno " * 40)})
        history.append({"role": "assistant", "content": f"nota {index} " + ("detalle " * 40)})
    history.append({"role": "user", "content": PY})
    sink: dict[str, object] = {}
    client = TestClient(
        create_app(
            _settings(
                context_compiler_enabled=True,
                context_max_budget_tokens=40,
                context_fresh_tail_turns=1,
            ),
            embedder=synthetic_embedder(),
            candados=synthetic_locks(),
            transport=_upstream(PYTHON_ANSWER, sink),
        )
    )
    response = client.post("/v1/chat/completions", json={"messages": history})
    assert response.status_code == 200
    compiled = compile_session_context(
        history,
        max_budget_tokens=40,
        fresh_tail_turns=1,
    )
    outbound = sink["body"]
    assert isinstance(outbound, dict)
    assert outbound["messages"] == compiled.messages
    assert "ddi_compile_context" not in outbound
    governor = response.json()["ddi_context_governor"]
    assert governor["original_tokens"] == compiled.original_tokens
    assert governor["compiled_tokens"] == compiled.compiled_tokens
    assert governor["compiled_tokens"] < governor["original_tokens"]
    assert governor["compression_ratio"] == compiled.compression_ratio
    assert governor["superseded_blocks_pruned"] == compiled.superseded_blocks_pruned
    assert governor["stale_traces_pruned"] == compiled.stale_traces_pruned

    flagged: dict[str, object] = {}
    flagged_client = TestClient(
        create_app(
            _settings(context_max_budget_tokens=40, context_fresh_tail_turns=1),
            embedder=synthetic_embedder(),
            candados=synthetic_locks(),
            transport=_upstream(PYTHON_ANSWER, flagged),
        )
    )
    payload = {"ddi_compile_context": True, "messages": history}
    flagged_response = flagged_client.post("/v1/chat/completions", json=payload)
    assert flagged_response.status_code == 200
    assert "ddi_compile_context" not in flagged["body"]
    assert "ddi_context_governor" in flagged_response.json()


def test_autoload_calibration_leaves_v1_untouched(tmp_path: Path) -> None:
    model, pos_vec, _neg = _separable_model()
    path = save_v2_calibration(tmp_path / "v2.npz", model, model_id="table", alpha=0.05)
    embedder = _TableEmbedder({_BENIGN: pos_vec}, dimension=16)
    loaded = create_app(
        _settings(engine_mode="v2_spectral_ast", v2_calibration_path=path),
        embedder=embedder,
        transport=_upstream(_BENIGN),
    )
    health = TestClient(loaded).get("/healthz").json()
    assert health["status"] == "ok"
    assert health["engine_mode"] == "v2_spectral_ast"
    assert isinstance(loaded.state.v2_firewall, SpectralAstFirewall)
    legacy = create_app(
        _settings(v2_calibration_path=path),
        embedder=synthetic_embedder(),
        candados=synthetic_locks(),
        transport=_upstream(PYTHON_ANSWER),
    )
    legacy_health = TestClient(legacy).get("/healthz").json()
    assert legacy_health["engine_mode"] == "v1_boxes"
    assert legacy_health["status"] == "ok"
    passed = TestClient(legacy).post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": PY}]},
    )
    assert passed.status_code == 200
    assert passed.json()["choices"][0]["message"]["content"] == PYTHON_ANSWER
    assert health["context_compiler_enabled"] is False

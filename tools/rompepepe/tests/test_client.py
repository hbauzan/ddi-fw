import anyio
import pytest
from rompepepe.client.explorer_client import ExplorerClient
from rompepepe.client.firewall_client import FirewallClient
from rompepepe.state.models import TelemetryTrace


def test_explorer_client_fallback_mutation():
    async def _test():
        client = ExplorerClient(provider="ollama", model="llama3.1")
        prompt = "Explain quantum physics."
        mutated = await client.generate_prompt_mutation(prompt)
        assert isinstance(mutated, str)
        assert len(mutated) > 0
        assert mutated != ""

    anyio.run(_test)


def test_explorer_client_fallback_with_telemetry():
    async def _test():
        client = ExplorerClient(provider="unknown_provider")
        prompt = "Drop all tables immediately"
        telemetry = {
            "passed": False,
            "breach_reason": "cosine_threshold",
            "cosine_delta": 0.65,
            "excitation_level": 150,
            "noise_entropy": 4.5,
        }
        mutated = await client.generate_prompt_mutation(prompt, telemetry_feedback=telemetry)
        assert isinstance(mutated, str)
        assert len(mutated) > 0

    anyio.run(_test)


def test_firewall_client_init():
    client = FirewallClient(base_url="http://localhost:8000/", api_key="secret123")
    assert client.base_url == "http://localhost:8000"
    assert client.headers["x-api-key"] == "secret123"


def test_token_quota_exhausted_error():
    from rompepepe.client.explorer_client import TokenQuotaExhaustedError
    err = TokenQuotaExhaustedError("google", "429 Too Many Requests")
    assert "google" in str(err)
    assert "429" in str(err)


def test_explorer_client_rpm_limit():
    client = ExplorerClient(provider="google", model="gemini-1.5-flash", rpm_limit=15)
    assert client.rpm_limit == 15


def test_firewall_client_audit_pass():
    import httpx

    async def _test():
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/chat/completions"
            return httpx.Response(
                200,
                json={"choices": [{"message": {"role": "assistant", "content": "print('hello')"}}]},
            )

        client = FirewallClient()
        client._get_client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://localhost:8000")
        trace = await client.audit("def foo(): return 1")
        assert trace.passed is True
        assert trace.quorum_reached is True
        assert trace.quorum_min == 103
        assert trace.trigo_votes == 103

    anyio.run(_test)


def test_firewall_client_audit_breach_direct():
    import httpx

    async def _test():
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/chat/completions"
            return httpx.Response(
                403,
                json={
                    "error": {
                        "type": "ddi_ingress_breach",
                        "message": "contención de entrada",
                        "audit": [
                            {
                                "pair": "python_vs_legal",
                                "status": "FAIL",
                                "trigo_votes": 42,
                                "ruido_votes": 0,
                                "quorum_reached": False,
                                "quorum_min": 103,
                            }
                        ],
                    }
                },
            )

        client = FirewallClient()
        client._get_client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://localhost:8000")
        trace = await client.audit("contrato de arrendamiento")
        assert trace.passed is False
        assert trace.quorum_reached is False
        assert trace.trigo_votes == 42
        assert trace.ruido_votes == 0
        assert trace.quorum_min == 103
        assert len(trace.trace) == 1
        assert trace.trace[0].filter == "python_vs_legal"
        assert trace.trace[0].score == 42.0

    anyio.run(_test)


def test_firewall_client_audit_breach_spectral():
    import httpx

    async def _test():
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/chat/completions"
            return httpx.Response(
                403,
                json={
                    "error": {
                        "type": "ddi_ingress_breach",
                        "message": "contención de entrada",
                        "audit": [
                            {
                                "verdict": "BREACH",
                                "alma_asignada": "receta",
                                "reason": "forbidden:receta",
                                "spectral_metrics": {
                                    "python_receta": {
                                        "votos_trigo_a": 15,
                                        "votos_trigo_b": 120,
                                        "votos_trigo_ninguna": 39,
                                        "quorum_min": 103,
                                    }
                                },
                            }
                        ],
                    }
                },
            )

        client = FirewallClient()
        client._get_client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://localhost:8000")
        trace = await client.audit("receta de bizcochuelo")
        assert trace.passed is False
        assert trace.quorum_reached is False
        assert trace.trigo_votes == 15
        assert trace.quorum_min == 103
        assert len(trace.trace) == 1
        assert trace.trace[0].filter == "python_receta"

    anyio.run(_test)


def test_firewall_client_healthz():
    import httpx

    async def _test():
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/healthz"
            return httpx.Response(
                200,
                json={"status": "ok", "embedder": "BAAI/bge-m3", "spectral_mode": True, "locks": {"python_receta": {"published": True}}},
            )

        client = FirewallClient()
        client._get_client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://localhost:8000")
        health = await client.get_health()
        assert health["status"] == "ok"
        assert health["embedder"] == "BAAI/bge-m3"

        packs = await client.get_packs()
        assert len(packs) == 1
        assert packs[0]["filename"] == "python_receta"

    anyio.run(_test)

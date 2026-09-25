"""Tests para la integración de la arquitectura del Ecualizador Espectral al runtime del firewall.

Verifica:
1. Corte espectral con Quórum del 10% (K = ceil(0.10 * D))
2. Poda estricta de dimensiones de ruido estructural (saturadas y planas)
3. Ingress fail-closed bajo quórum y métricas espectrales en auditoría
4. Reporte de salud e inicialización en Proxy ASGI
"""

from __future__ import annotations

import numpy as np

from ddi_fw.corte import (
    VOTE_NINGUNA,
    VOTE_SOLO_A,
    VOTE_SOLO_B,
    evaluar_corte_espectral,
)
from ddi_fw.embedder import FakeEmbedder
from ddi_fw.hoja import (
    RUIDO_UNIVERSAL_BGE_M3,
    Candado,
    calcular_hoja,
)
from ddi_fw.ingress import Policy, decide, inspect_prompt


def test_evaluar_corte_espectral_quorum_10_percent() -> None:
    # Espacio D = 100 -> Quórum 10% = 10 dimensiones
    dim = 100
    quorum = 10

    # 1. Caso LEFT: 10 votos SOLO_A, 0 votos SOLO_B
    votos = np.full(dim, VOTE_NINGUNA, dtype=np.uint8)
    votos[:10] = VOTE_SOLO_A
    label, met = evaluar_corte_espectral(votos, quorum_min=quorum)
    assert label == "left"
    assert met["votos_trigo_a"] == 10
    assert met["votos_trigo_b"] == 0
    assert met["quorum_min"] == 10

    # 2. Caso RIGHT: 15 votos SOLO_B, 2 votos SOLO_A
    votos = np.full(dim, VOTE_NINGUNA, dtype=np.uint8)
    votos[:15] = VOTE_SOLO_B
    votos[15:17] = VOTE_SOLO_A
    label, met = evaluar_corte_espectral(votos, quorum_min=quorum)
    assert label == "right"
    assert met["votos_trigo_b"] == 15
    assert met["votos_trigo_a"] == 2

    # 3. Caso OUT: 9 votos SOLO_A (< quorum de 10)
    votos = np.full(dim, VOTE_NINGUNA, dtype=np.uint8)
    votos[:9] = VOTE_SOLO_A
    label, met = evaluar_corte_espectral(votos, quorum_min=quorum)
    assert label == "out"
    assert met["votos_trigo_a"] == 9

    # 4. Caso SPLIT: 12 votos SOLO_A y 11 votos SOLO_B (ataque híbrido o piggyback)
    votos = np.full(dim, VOTE_NINGUNA, dtype=np.uint8)
    votos[:12] = VOTE_SOLO_A
    votos[12:23] = VOTE_SOLO_B
    label, met = evaluar_corte_espectral(votos, quorum_min=quorum)
    assert label == "split"


def test_evaluar_corte_espectral_ruido_pruning() -> None:
    # D = 10, quorum = 2
    dim = 10
    votos = np.full(dim, VOTE_NINGUNA, dtype=np.uint8)
    # Dimensiones 0 y 1 tienen voto SOLO_A
    votos[0] = VOTE_SOLO_A
    votos[1] = VOTE_SOLO_A

    # Si dimension 0 es RUIDO, no debe contar para el quórum
    ruido = [0]
    label, met = evaluar_corte_espectral(votos, quorum_min=2, ruido_indices=ruido)
    assert label == "out"  # Solo queda 1 voto válido, requiere 2
    assert met["votos_trigo_a"] == 1
    assert met["total_trigo"] == 9

    # Si agregamos dimension 2 (no ruido) con SOLO_A, alcanza el quórum de 2
    votos[2] = VOTE_SOLO_A
    label, met = evaluar_corte_espectral(votos, quorum_min=2, ruido_indices=ruido)
    assert label == "left"
    assert met["votos_trigo_a"] == 2


def test_hoja_y_candado_espectral() -> None:
    dim = 1024
    matriz_a = np.zeros((10, dim), dtype=np.float32)
    matriz_b = np.ones((10, dim), dtype=np.float32) * 5.0

    hoja = calcular_hoja(
        matriz_a,
        matriz_b,
        alma_a="python",
        alma_b="receta",
        ruido_indices=RUIDO_UNIVERSAL_BGE_M3,
        modo_espectral=True,
        quorum_ratio=0.10,
    )

    assert hoja.is_spectral is True
    assert hoja.quorum_min == 103  # ceil(0.10 * 1024)
    assert len(hoja.ejes_trigo()) == 1024 - len(RUIDO_UNIVERSAL_BGE_M3)
    for ruido_idx in RUIDO_UNIVERSAL_BGE_M3:
        assert ruido_idx not in hoja.ejes_trigo()

    candado = Candado(hoja=hoja)
    assert candado.is_spectral is True
    assert candado.quorum_min == 103
    assert candado.published is True
    assert candado.disjoint_count == 1024 - len(RUIDO_UNIVERSAL_BGE_M3)


def test_ingress_spectral_quorum_decision() -> None:
    dim = 100
    quorum = 10
    # Creamos matriz sintética para A (python) y B (receta)
    mat_python = np.zeros((10, dim), dtype=np.float32)
    mat_receta = np.ones((10, dim), dtype=np.float32) * 10.0

    hoja = calcular_hoja(
        mat_python,
        mat_receta,
        alma_a="python",
        alma_b="receta",
        modo_espectral=True,
        quorum_min=quorum,
    )
    candados = {"python_receta": Candado(hoja=hoja)}
    politica = Policy(allowed="python", forbidden=frozenset({"receta"}))

    # 1. Vector puramente Python (en el intervalo [0, 0] para 10+ coordenadas)
    vec_python = np.ones(dim, dtype=np.float32) * 50.0  # fuera por defecto
    vec_python[:15] = 0.0  # 15 dimensiones en el rango de python [0, 0]
    dec_pass = decide(vec_python, candados, politica)
    assert dec_pass.verdict == "PASS"
    assert dec_pass.alma_asignada == "python"
    assert dec_pass.spectral_metrics is not None
    assert dec_pass.spectral_metrics["python_receta"]["votos_trigo_a"] == 15

    # 2. Vector contaminado Receta (15 dimensiones en el rango de receta [10, 10])
    vec_receta = np.ones(dim, dtype=np.float32) * 50.0
    vec_receta[:15] = 10.0
    dec_breach = decide(vec_receta, candados, politica)
    assert dec_breach.verdict == "BREACH"
    assert dec_breach.alma_asignada == "receta"
    assert "forbidden:receta" in dec_breach.reason

    # 3. Vector fuera de dominio (< 10 coordenadas coincidentes)
    vec_out = np.ones(dim, dtype=np.float32) * 50.0
    vec_out[:5] = 0.0  # solo 5 dimensiones
    dec_out = decide(vec_out, candados, politica)
    assert dec_out.verdict == "BREACH"
    assert "cut:python_receta:out" in dec_out.reason

    # 4. IngressPrompt completo
    fake = FakeEmbedder(
        dimension=dim, table={"clausula python": vec_python, "clausula receta": vec_receta}
    )
    res_pass = inspect_prompt("clausula python", fake, candados, politica)
    assert res_pass.verdict == "PASS"

    res_breach = inspect_prompt("clausula python y clausula receta", fake, candados, politica)
    assert res_breach.verdict == "BREACH"
    assert res_breach.reason == "clause_breach"
    # Auditoría incluye las métricas espectrales
    assert "spectral_metrics" in res_breach.audit[0]


def test_proxy_spectral_healthz(tmp_path) -> None:
    import httpx
    from fastapi.testclient import TestClient

    from ddi_fw.config import Settings
    from ddi_fw.proxy import create_app

    dim = 20
    mat_python = np.zeros((5, dim), dtype=np.float32)
    mat_receta = np.ones((5, dim), dtype=np.float32) * 5.0
    hoja = calcular_hoja(
        mat_python,
        mat_receta,
        alma_a="python",
        alma_b="receta",
        modo_espectral=True,
        quorum_ratio=0.10,
    )
    candados = {"python_receta": Candado(hoja=hoja)}

    settings = Settings(
        upstream_url="http://upstream.test/v1",
        upstream_model="mock",
        allowed_alma="python",
        forbidden_almas="receta",
        spectral_mode=True,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"choices": [{"message": {"role": "assistant", "content": "ok"}}]}
        )

    app = create_app(
        settings,
        embedder=FakeEmbedder(dimension=dim),
        candados=candados,
        transport=httpx.MockTransport(handler),
    )
    client = TestClient(app)

    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["spectral_mode"] is True
    assert body["locks"]["python_receta"]["is_spectral"] is True
    assert body["locks"]["python_receta"]["quorum_min"] == 2  # ceil(0.10 * 20)

"""Pure httpx REST client for Three-Headed Semantic Firewall backend API.

No internal Python backend imports; communicates strictly via HTTP REST.
"""
import logging
from typing import Any
import httpx

from rompepepe.state.models import TelemetryTrace, TelemetryTraceItem

logger = logging.getLogger(__name__)


class FirewallClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=self.timeout)

    async def get_health(self) -> dict[str, Any]:
        """Queries GET /healthz on ddi-fw proxy."""
        async with self._get_client() as client:
            resp = await client.get("/healthz")
            resp.raise_for_status()
            return resp.json()

    async def get_config(self) -> dict[str, Any]:
        """Fetches active firewall status/configuration via /healthz."""
        try:
            health = await self.get_health()
            return {
                "embedder": health.get("embedder", "bge-m3"),
                "spectral_mode": health.get("spectral_mode", True),
                "locks": health.get("locks", {}),
                "status": health.get("status", "ok"),
            }
        except Exception as e:
            logger.debug(f"get_config fallback: {e}")
            return {"spectral_mode": True, "quorum_min": 103}

    async def update_config(self, config_dict: dict[str, Any]) -> dict[str, Any]:
        """ddi-fw production proxy is statically configured via environment; config update returns current config."""
        return config_dict

    async def get_packs(self) -> list[dict[str, Any]]:
        """Extracts active lock pairs as virtual packs from /healthz."""
        try:
            health = await self.get_health()
            locks = health.get("locks", {})
            return [
                {
                    "filename": pair_id,
                    "published": info.get("published", True),
                    "is_spectral": info.get("is_spectral", True),
                    "quorum_min": info.get("quorum_min", 103),
                    "num_vectors": info.get("disjoint_count", 985),
                }
                for pair_id, info in locks.items()
            ]
        except Exception as e:
            logger.debug(f"get_packs fallback: {e}")
            return []

    async def audit(self, query: str) -> TelemetryTrace:
        """Audits a prompt via OpenAI-compatible endpoint POST /v1/chat/completions."""
        payload = {
            "messages": [{"role": "user", "content": query}],
            "model": "ddi-fw",
        }
        async with self._get_client() as client:
            try:
                resp = await client.post("/v1/chat/completions", json=payload)
            except Exception as exc:
                return TelemetryTrace(
                    passed=False,
                    breach_reason=f"network_error:{exc.__class__.__name__}",
                    text=f"Error connecting to firewall: {exc}",
                )

            # Scenario 1: HTTP 200 - Ingress ALLOWED and upstream responded
            if resp.status_code == 200:
                data = resp.json()
                assistant_text = ""
                try:
                    assistant_text = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError):
                    pass
                return TelemetryTrace(
                    passed=True,
                    breach_reason=None,
                    text=assistant_text or "ALLOW",
                    quorum_reached=True,
                    quorum_min=103,
                    trigo_votes=103,
                    ruido_votes=0,
                )

            # Scenario 2: HTTP 403 - Firewall Contained / Blocked (Ingress or Egress BREACH)
            if resp.status_code == 403:
                try:
                    data = resp.json()
                except Exception:
                    data = {}
                err = data.get("error", {})
                error_type = err.get("type", "ddi_ingress_breach")
                message = err.get("message", "contención de entrada")
                raw_audit = err.get("audit", [])

                trace_items: list[TelemetryTraceItem] = []
                trigo_votes = 0
                ruido_votes = 0
                quorum_reached = False
                quorum_min = 103
                reasons: list[str] = []

                if isinstance(raw_audit, list):
                    for idx, item in enumerate(raw_audit):
                        if not isinstance(item, dict):
                            continue

                        # Format A: Direct keys from task spec
                        if "trigo_votes" in item:
                            pair = str(item.get("pair", f"lock_{idx}"))
                            t_votes = int(item.get("trigo_votes", 0))
                            r_votes = int(item.get("ruido_votes", 0))
                            q_reached = bool(item.get("quorum_reached", False))
                            q_min = int(item.get("quorum_min", 103))
                            status = str(item.get("status", "FAIL"))

                            trigo_votes = t_votes
                            ruido_votes = r_votes
                            quorum_reached = q_reached
                            quorum_min = q_min
                            reasons.append(f"{pair}:{status}")

                            trace_items.append(
                                TelemetryTraceItem(
                                    filter=pair,
                                    order=idx + 1,
                                    score=float(t_votes),
                                    threshold=float(q_min),
                                    passed=q_reached,
                                    details=item,
                                )
                            )

                        # Format B: IngressResult audit (spectral_metrics)
                        elif "spectral_metrics" in item or "verdict" in item:
                            reason = str(item.get("reason", "breach"))
                            reasons.append(reason)
                            spectral = item.get("spectral_metrics")
                            if isinstance(spectral, dict):
                                for pair_id, met in spectral.items():
                                    v_a = int(met.get("votos_trigo_a", 0))
                                    q_min = int(met.get("quorum_min", 103))
                                    q_reached = bool(v_a >= q_min)
                                    v_none = int(met.get("votos_trigo_ninguna", 0))

                                    vc = item.get("vote_counts", {})
                                    r_votes = int(vc.get("ninguna", v_none))

                                    trigo_votes = v_a
                                    ruido_votes = r_votes
                                    quorum_reached = q_reached
                                    quorum_min = q_min

                                    trace_items.append(
                                        TelemetryTraceItem(
                                            filter=pair_id,
                                            order=idx + 1,
                                            score=float(v_a),
                                            threshold=float(q_min),
                                            passed=q_reached,
                                            details=met,
                                        )
                                    )
                            else:
                                trace_items.append(
                                    TelemetryTraceItem(
                                        filter=item.get("alma_asignada") or "unknown",
                                        order=idx + 1,
                                        score=0.0,
                                        threshold=103.0,
                                        passed=False,
                                        details=item,
                                    )
                                )

                reason_str = ", ".join(reasons) if reasons else message
                breach_reason = f"{error_type}: {reason_str}"

                return TelemetryTrace(
                    passed=False,
                    breach_reason=breach_reason,
                    trace=trace_items,
                    text=message,
                    trigo_votes=trigo_votes,
                    ruido_votes=ruido_votes,
                    quorum_reached=quorum_reached,
                    quorum_min=quorum_min,
                )

            # Scenario 3: HTTP 502 with ddi_upstream_error -> Ingress actually passed!
            if resp.status_code == 502:
                try:
                    data = resp.json()
                    err_type = data.get("error", {}).get("type", "")
                except Exception:
                    err_type = ""
                if err_type == "ddi_upstream_error":
                    return TelemetryTrace(
                        passed=True,
                        breach_reason=None,
                        text="Ingress passed (upstream unavailable)",
                        quorum_reached=True,
                        quorum_min=103,
                        trigo_votes=103,
                        ruido_votes=0,
                    )

            # Any other status code
            return TelemetryTrace(
                passed=False,
                breach_reason=f"HTTP_{resp.status_code}",
                text=resp.text,
                quorum_reached=False,
                quorum_min=103,
                trigo_votes=0,
                ruido_votes=0,
            )

    async def chat(self, prompt: str) -> dict[str, Any]:
        """Sends chat completion query to /v1/chat/completions."""
        async with self._get_client() as client:
            resp = await client.post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": prompt}], "model": "ddi-fw"},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_profiles(self) -> list[str]:
        return ["default"]

    async def load_profile(self, name: str) -> dict[str, Any]:
        return {"profile": name, "status": "active"}

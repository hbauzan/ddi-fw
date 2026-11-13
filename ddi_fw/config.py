"""Configuración por entorno. Cero secretos en código."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DDI_", env_file=".env", extra="ignore")

    upstream_url: str = "http://127.0.0.1:11434/v1"
    upstream_model: str = "llama3.2"
    host: str = "127.0.0.1"
    port: int = 8080
    request_timeout_seconds: float = 60.0
    allowed_alma: str = "python"
    forbidden_almas: str = "receta,legal"
    embedder: str = "bge-m3"
    rows_path: Path = Field(default=Path("ddi_fw/out/rows.npz"))
    trilingual_rows_path: Path = Field(default=Path("ddi_fw/out/trilingual_bge/rows.npz"))
    out_dir: Path = Field(default=Path("ddi_fw/out"))
    spectral_mode: bool = True
    quorum_ratio: float = 0.10
    podar_ruido: bool = True
    prune_paja: bool = True  # Deprecated alias
    engine_mode: Literal["v1_boxes", "v2_spectral_ast"] = "v1_boxes"
    v2_calibration_path: Path = Field(default=Path("ddi_fw/out/v2_spectral_ast.npz"))
    context_compiler_enabled: bool = False
    context_max_budget_tokens: int = 36000
    context_fresh_tail_turns: int = 6

    def forbidden_set(self) -> frozenset[str]:
        return frozenset(item.strip() for item in self.forbidden_almas.split(",") if item.strip())

"""Configuración por entorno. Cero secretos en código."""

from __future__ import annotations

from pathlib import Path

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
    out_dir: Path = Field(default=Path("ddi_fw/out"))

    def forbidden_set(self) -> frozenset[str]:
        return frozenset(item.strip() for item in self.forbidden_almas.split(",") if item.strip())

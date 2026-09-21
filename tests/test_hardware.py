from __future__ import annotations

import datetime

from ddi_fw.hardware import format_hardware_markdown, get_hardware_profile


def test_hardware_profile_keys() -> None:
    profile = get_hardware_profile()
    required_keys = {
        "dispositivo",
        "target_pytorch",
        "memoria_ram",
        "sistema_operativo",
        "version_python",
        "version_pytorch",
        "version_numpy",
        "timestamp_iso",
    }
    assert required_keys.issubset(profile.keys())
    for k in required_keys:
        assert isinstance(profile[k], str)
        assert len(profile[k]) > 0


def test_hardware_profile_timestamp_iso() -> None:
    profile = get_hardware_profile()
    # Verifica que sea parseable como ISO 8601
    dt = datetime.datetime.fromisoformat(profile["timestamp_iso"])
    assert dt.tzinfo is not None


def test_format_hardware_markdown() -> None:
    profile = {
        "dispositivo": "Apple M4",
        "target_pytorch": "mps:0",
        "memoria_ram": "16 GB unificada",
        "sistema_operativo": "macOS-26.5.1-arm64",
        "version_python": "3.14.3",
        "version_pytorch": "2.14.0",
        "version_numpy": "2.5.3",
        "timestamp_iso": "2026-09-21T19:25:00-03:00",
    }
    md = format_hardware_markdown(profile)
    assert "### Ficha de Hardware y Entorno de Ejecución" in md
    assert "- **Dispositivo**: Apple M4" in md
    assert "- **Target PyTorch**: mps:0" in md
    assert "- **Memoria RAM del Sistema**: 16 GB unificada" in md
    assert "- **Timestamp ISO 8601**: 2026-09-21T19:25:00-03:00" in md

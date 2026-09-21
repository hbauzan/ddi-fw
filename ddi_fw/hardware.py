"""Estándar de registro de hardware y entorno de ejecución reproducible.

Cumple con el estándar obligatorio definido en:
roadmap/hipotesis-ecualizador/00-definicion-y-hardware.md
"""

from __future__ import annotations

import datetime
import os
import platform
import subprocess
from typing import Any

import numpy as np
import torch


def get_cpu_model() -> str:
    """Detecta el modelo del procesador de forma confiable en macOS y Linux."""
    if platform.system() == "Darwin":
        try:
            out = (
                subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"], stderr=subprocess.DEVNULL
                )
                .decode("utf-8")
                .strip()
            )
            if out:
                return out
        except Exception:
            pass
    elif platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass

    processor = platform.processor()
    machine = platform.machine()
    return processor or machine or "Desconocido"


def get_system_ram() -> str:
    """Detecta la memoria RAM total del sistema."""
    if platform.system() == "Darwin":
        try:
            out = (
                subprocess.check_output(["sysctl", "-n", "hw.memsize"], stderr=subprocess.DEVNULL)
                .decode("utf-8")
                .strip()
            )
            bytes_total = int(out)
            gb = bytes_total / (1024**3)
            return f"{gb:.0f} GB unificada"
        except Exception:
            pass
    elif platform.system() == "Linux":
        try:
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        gb = kb / (1024**2)
                        return f"{gb:.0f} GB"
        except Exception:
            pass

    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        total_gb = (pages * page_size) / (1024**3)
        return f"{total_gb:.0f} GB"
    except Exception:
        return "Desconocida"


def get_pytorch_target() -> str:
    """Identifica el target principal de PyTorch."""
    if torch.backends.mps.is_available():
        return "mps:0"
    if torch.cuda.is_available():
        return "cuda:0"
    return "cpu"


def get_hardware_profile() -> dict[str, str]:
    """Genera la ficha técnica obligatoria de hardware y entorno de ejecución."""
    now_iso = datetime.datetime.now(datetime.UTC).astimezone().isoformat()
    return {
        "dispositivo": get_cpu_model(),
        "target_pytorch": get_pytorch_target(),
        "memoria_ram": get_system_ram(),
        "sistema_operativo": platform.platform(),
        "version_python": platform.python_version(),
        "version_pytorch": str(torch.__version__),
        "version_numpy": str(np.__version__),
        "timestamp_iso": now_iso,
    }


def format_hardware_markdown(profile: dict[str, Any] | None = None) -> str:
    """Formatea la ficha técnica en el bloque Markdown canónico."""
    p = profile if profile is not None else get_hardware_profile()
    return (
        "### Ficha de Hardware y Entorno de Ejecución\n"
        f"- **Dispositivo**: {p.get('dispositivo', 'N/A')}\n"
        f"- **Target PyTorch**: {p.get('target_pytorch', 'N/A')}\n"
        f"- **Memoria RAM del Sistema**: {p.get('memoria_ram', 'N/A')}\n"
        f"- **Sistema Operativo**: {p.get('sistema_operativo', 'N/A')}\n"
        f"- **Versión de Python**: {p.get('version_python', 'N/A')}\n"
        f"- **Versión de PyTorch**: {p.get('version_pytorch', 'N/A')}\n"
        f"- **Versión de NumPy**: {p.get('version_numpy', 'N/A')}\n"
        f"- **Timestamp ISO 8601**: {p.get('timestamp_iso', 'N/A')}\n"
    )

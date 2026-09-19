"""Pytest hooks. El marker `live` se salta salvo que se pida explícitamente."""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Ejecutar tests que cargan embedders reales.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(reason="pasá --run-live para embedders reales")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)

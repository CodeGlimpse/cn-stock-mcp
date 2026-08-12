from __future__ import annotations

from cn_stock_mcp.server import tool_registry


def test_tool_registry_all_exports_are_bound():
    missing = [name for name in tool_registry.__all__ if not hasattr(tool_registry, name)]
    assert missing == []


def test_tool_registry_star_import_exports_every_declared_name():
    namespace: dict[str, object] = {}
    exec("from cn_stock_mcp.server.tool_registry import *", namespace)

    assert {name for name in tool_registry.__all__} <= set(namespace)

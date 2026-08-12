from __future__ import annotations

import json
from typing import Any

import anyio

from cn_stock_mcp.server.mcp_server import create_server
from cn_stock_mcp.server.stdio_server import build_fastmcp_server, run_stdio_server


class TransportApp:
    """Production transport facade.

    - stdio path: MCP Python SDK 2.x low-level server via `run_stdio()`
    - local test/debug path: direct in-process registry invocation
    """

    def __init__(self) -> None:
        self.server = create_server()

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_model": tool.input_model.__name__,
            }
            for tool in self.server.tools.values()
        ]

    def call_tool(self, name: str, payload: dict[str, Any]) -> Any:
        return self.server.call_tool(name, payload)

    def to_stdio_payload(self, name: str, payload: dict[str, Any]) -> str:
        result = self.call_tool(name, payload)
        return json.dumps(result, ensure_ascii=False, default=_json_default, indent=2)

    def run_stdio_once(self, name: str, payload: dict[str, Any]) -> None:
        print(self.to_stdio_payload(name, payload))

    def run_stdio(self) -> None:
        anyio.run(run_stdio_server, build_fastmcp_server())


def _json_default(value: Any):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, set):
        return list(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

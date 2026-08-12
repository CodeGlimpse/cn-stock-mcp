from __future__ import annotations

import json
from typing import Any

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from cn_stock_mcp.server.mcp_server import MCPServerStub, create_server


def _json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, set):
        return list(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=_json_default)


def _build_tool_schema(tool: Any) -> types.Tool:
    return types.Tool(
        name=tool.name,
        description=tool.description,
        inputSchema=tool.input_model.model_json_schema(),
    )


def _build_mcp_handlers(registry: MCPServerStub):
    async def list_tools(_ctx: Any, _params: Any) -> types.ListToolsResult:
        tools = [_build_tool_schema(tool) for tool in registry.tools.values()]
        return types.ListToolsResult(tools=tools)

    async def call_tool(_ctx: Any, params: types.CallToolRequestParams) -> types.CallToolResult:
        result = registry.call_tool(params.name, params.arguments or {})
        is_error = not bool(result.get("success")) if isinstance(result, dict) else False
        return types.CallToolResult(
            content=[types.TextContent(text=_json_text(result))],
            structuredContent=result,
            isError=is_error,
        )

    return list_tools, call_tool


def build_fastmcp_server() -> Server[Any]:
    """Build the MCP 2.x low-level server backed by the application registry.

    The historical function name is retained for callers that imported it
    directly. It now returns the MCP 2.x low-level ``Server`` because the
    FastMCP module was removed from the installed SDK.
    """

    registry = create_server()
    list_tools, call_tool = _build_mcp_handlers(registry)
    return Server(
        registry.name,
        version=registry.version,
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )


async def run_stdio_server(server: Server[Any]) -> None:
    """Run an MCP 2.x server over the standard input/output transport."""

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

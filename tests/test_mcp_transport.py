from __future__ import annotations

import asyncio
import json

from pydantic import BaseModel

from mcp import types

from cn_stock_mcp.server import stdio_server
from cn_stock_mcp.server.mcp_server import MCPServerStub, MCPTool
from cn_stock_mcp.server.stdio_server import build_fastmcp_server


def _run(coro):
    return asyncio.run(coro)


def test_mcp_server_lists_every_registered_tool():
    server = build_fastmcp_server()
    registry = stdio_server.create_server()
    handler = server.get_request_handler("tools/list")
    assert handler is not None

    result = _run(handler.handler(None, None))

    assert len(result.tools) == len(registry.tools)
    assert {tool.name for tool in result.tools} == set(registry.tools)
    assert len({tool.name for tool in result.tools}) == len(result.tools)

    provider_health = next(tool for tool in result.tools if tool.name == "provider_health")
    assert provider_health.input_schema["type"] == "object"


def test_mcp_server_builds_a_schema_for_every_registered_tool():
    server = build_fastmcp_server()
    registry = stdio_server.create_server()
    handler = server.get_request_handler("tools/list")
    assert handler is not None

    result = _run(handler.handler(None, None))

    for tool in result.tools:
        assert tool.description
        assert tool.input_schema == registry.tools[tool.name].input_model.model_json_schema()
        assert tool.input_schema["type"] == "object"


def test_mcp_server_routes_successful_call_and_preserves_envelope(monkeypatch):
    class SuccessRequest(BaseModel):
        value: int

    registry = MCPServerStub(name="test-server", version="0.0.0")
    registry.register_tool(
        MCPTool(
            name="success",
            description="A local success test tool.",
            input_model=SuccessRequest,
            handler=lambda request: {"doubled": request.value * 2},
        )
    )
    monkeypatch.setattr(stdio_server, "create_server", lambda: registry)

    server = build_fastmcp_server()
    handler = server.get_request_handler("tools/call")
    assert handler is not None

    result = _run(
        handler.handler(
            None,
            types.CallToolRequestParams(name="success", arguments={"value": 21}),
        )
    )

    assert result.is_error is False
    payload = json.loads(result.content[0].text)
    assert payload["success"] is True
    assert payload["data"] == {"doubled": 42}
    assert payload["error"] is None
    assert payload["meta"]["tool"] == "success"
    assert result.structured_content == payload


def test_mcp_server_routes_invalid_arguments_without_upstream_call():
    server = build_fastmcp_server()
    handler = server.get_request_handler("tools/call")
    assert handler is not None

    result = _run(
        handler.handler(
            None,
            types.CallToolRequestParams(
                name="stock_quote",
                arguments={"symbols": []},
            ),
        )
    )

    assert result.is_error is True
    payload = json.loads(result.content[0].text)
    assert payload["success"] is False
    assert payload["error"]["error_code"] == "INVALID_ARGUMENT"


def test_mcp_server_returns_unknown_tool_as_mcp_error():
    server = build_fastmcp_server()
    handler = server.get_request_handler("tools/call")
    assert handler is not None

    result = _run(
        handler.handler(
            None,
            types.CallToolRequestParams(name="does_not_exist", arguments={}),
        )
    )

    assert result.is_error is True
    payload = json.loads(result.content[0].text)
    assert payload["error"]["error_code"] == "TOOL_NOT_FOUND"

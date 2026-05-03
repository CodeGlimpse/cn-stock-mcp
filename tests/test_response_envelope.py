from openclaw_stock_mcp.server.mcp_server import MCPServerStub, MCPTool
from pydantic import BaseModel, Field


class _Req(BaseModel):
    value: int = Field(ge=1)


def test_call_tool_wraps_success_in_envelope():
    s = MCPServerStub(name="x", version="1")
    s.register_tool(MCPTool(name="ok", description="", input_model=_Req, handler=lambda r: {"v": r.value}))

    resp = s.call_tool("ok", {"value": 1})
    assert resp["success"] is True
    assert resp["data"]["v"] == 1
    assert resp["error"] is None


def test_call_tool_validation_error_in_envelope():
    s = MCPServerStub(name="x", version="1")
    s.register_tool(MCPTool(name="ok", description="", input_model=_Req, handler=lambda r: {"v": r.value}))

    resp = s.call_tool("ok", {"value": 0})
    assert resp["success"] is False
    assert resp["error"]["error_code"] == "INVALID_ARGUMENT"


def test_call_tool_not_found_in_envelope():
    s = MCPServerStub(name="x", version="1")
    resp = s.call_tool("missing", {})
    assert resp["success"] is False
    assert resp["error"]["error_code"] == "TOOL_NOT_FOUND"

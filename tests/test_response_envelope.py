from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field

from cn_stock_mcp.server.mcp_server import MCPServerStub, MCPTool


class _Req(BaseModel):
    value: int = Field(ge=1)


def test_call_tool_wraps_success_in_envelope():
    s = MCPServerStub(name="x", version="1")
    s.register_tool(MCPTool(name="ok", description="", input_model=_Req, handler=lambda r: {"v": r.value}))

    resp = s.call_tool("ok", {"value": 1})
    assert resp["success"] is True
    assert resp["data"]["v"] == 1
    assert resp["error"] is None
    assert resp["meta"]["tool"] == "ok"
    assert resp["meta"]["schema_version"] == "v1"
    assert isinstance(resp["meta"]["request_id"], str)
    assert resp["meta"]["request_id"].startswith("req_")


def test_call_tool_includes_realtime_freshness_metadata():
    class FreshRequest(BaseModel):
        pass

    observed = datetime.now(timezone.utc) - timedelta(seconds=5)
    server = MCPServerStub(name="test-server", version="1")
    server.register_tool(
        MCPTool(
            name="fresh",
            description="",
            input_model=FreshRequest,
            handler=lambda request: {"items": [{"timestamp": observed.isoformat()}]},
        )
    )

    freshness = server.call_tool("fresh", {})["meta"]["freshness"]

    assert freshness["status"] == "realtime"
    assert freshness["basis"] == "provider_timestamp"
    assert freshness["as_of"].endswith("Z")
    assert freshness["age_seconds"] >= 5


def test_call_tool_includes_dated_or_unknown_freshness_metadata():
    class FreshRequest(BaseModel):
        pass

    server = MCPServerStub(name="test-server", version="1")
    server.register_tool(
        MCPTool(
            name="dated",
            description="",
            input_model=FreshRequest,
            handler=lambda request: {"records": [{"date": "20260813"}]},
        )
    )
    server.register_tool(
        MCPTool(
            name="unknown",
            description="",
            input_model=FreshRequest,
            handler=lambda request: {"items": [{"symbol": "600519.SH"}]},
        )
    )

    dated = server.call_tool("dated", {})["meta"]["freshness"]
    unknown = server.call_tool("unknown", {})["meta"]["freshness"]

    assert dated["status"] == "dated"
    assert dated["basis"] == "source_date"
    assert dated["as_of"] == "2026-08-13"
    assert unknown["status"] == "unknown"
    assert unknown["as_of"] is None
    assert unknown["age_seconds"] is None


def test_call_tool_validation_error_in_envelope():
    s = MCPServerStub(name="x", version="1")
    s.register_tool(MCPTool(name="ok", description="", input_model=_Req, handler=lambda r: {"v": r.value}))

    resp = s.call_tool("ok", {"value": 0})
    assert resp["success"] is False
    assert resp["error"]["error_code"] == "INVALID_ARGUMENT"
    assert resp["meta"]["tool"] == "ok"
    assert resp["meta"]["schema_version"] == "v1"
    assert isinstance(resp["meta"]["request_id"], str)


def test_call_tool_not_found_in_envelope():
    s = MCPServerStub(name="x", version="1")
    resp = s.call_tool("missing", {})
    assert resp["success"] is False
    assert resp["error"]["error_code"] == "TOOL_NOT_FOUND"
    assert resp["meta"]["tool"] == "missing"
    assert resp["meta"]["schema_version"] == "v1"
    assert isinstance(resp["meta"]["request_id"], str)

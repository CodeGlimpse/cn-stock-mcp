from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field

from cn_stock_mcp.server.mcp_server import MCPServerStub, MCPTool


class _Req(BaseModel):
    value: int = Field(ge=1)


class _EmptyReq(BaseModel):
    pass


def test_call_tool_wraps_success_in_envelope():
    s = MCPServerStub(name="x", version="1")
    s.register_tool(MCPTool(name="ok", description="", input_model=_Req, handler=lambda r: {"v": r.value}))

    resp = s.call_tool("ok", {"value": 1})
    assert resp["success"] is True
    assert resp["data"]["v"] == 1
    assert resp["error"] is None
    assert resp["meta"]["tool"] == "ok"
    assert resp["meta"]["schema_version"] == "v1"
    assert "disclaimer" in resp["meta"]
    assert isinstance(resp["meta"]["request_id"], str)
    assert resp["meta"]["request_id"].startswith("req_")


def test_success_envelope_promotes_observability_without_changing_data():
    s = MCPServerStub(name="x", version="1")
    s.register_tool(
        MCPTool(
            name="observed",
            description="",
            input_model=_EmptyReq,
            handler=lambda r: {
                "items": [],
                "meta": {
                    "provider_used": "akshare",
                    "fallback_chain": ["akshare"],
                    "latency_ms": 12,
                },
            },
        )
    )

    resp = s.call_tool("observed", {})

    assert resp["data"]["meta"]["provider_used"] == "akshare"
    assert resp["meta"]["provider_used"] == "akshare"
    assert resp["meta"]["fallback_chain"] == ["akshare"]
    assert resp["meta"]["latency_ms"] == 12


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


def test_call_tool_includes_data_quality_metadata():
    class QualityRequest(BaseModel):
        pass

    server = MCPServerStub(name="test", version="1")
    server.register_tool(
        MCPTool(
            name="quality",
            description="quality",
            input_model=QualityRequest,
            handler=lambda request: {
                "items": [],
                "count": 0,
                "partial_failure": True,
                "meta": {"used_fallback": True},
            },
        )
    )

    response = server.call_tool("quality", {})

    assert response["success"] is True
    assert response["meta"]["data_quality"]["schema"] == "data_quality_v1"
    assert "provider_fallback" in response["meta"]["data_quality"]["flags"]


def test_freshness_prefers_explicit_source_as_of_hint():
    class FreshRequest(BaseModel):
        pass

    server = MCPServerStub(name="test-server", version="1")
    server.register_tool(
        MCPTool(
            name="explicit-freshness",
            description="",
            input_model=FreshRequest,
            handler=lambda request: {
                "records": [{"report_date": "2026-08-14"}],
                "meta": {"source_as_of": "2026-08-10T08:00:00Z"},
            },
        )
    )

    freshness = server.call_tool("explicit-freshness", {})["meta"]["freshness"]

    assert freshness["as_of"] == "2026-08-10T08:00:00Z"
    assert freshness["basis"] == "provider_timestamp"
    assert freshness["status"] == "realtime"


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

from __future__ import annotations

from copy import deepcopy
from functools import partial
import json
from pathlib import Path
from types import SimpleNamespace

import anyio
import pytest

from scripts.verify_retail_acceptance import TOOLS, assess, main, new_report, request_for, run_cases


def envelope(tool="stock_quote"):
    item = {"symbol": "000001.SZ", "price": 10.5, "source": "akshare"}
    data = {
        "source": "akshare", "items": [item], "summary": "Fixture summary",
        "recent_trading_days": ["2026-09-03", "2026-09-04"],
        "session_context": {"session_status": "post_close"},
        "latest_bar": {"close": 10.5}, "overview": {"indices": [item]},
        "index_ranking": [item],
        "themes": [{"sector_name": "银行"}, {"sector_name": "保险"}],
    }
    if tool == "stock_snapshot":
        data["items"] = [{"quote": item, "history": {"items": [{"close": 10.5}]}}]
    return {
        "success": True, "data": data, "error": None,
        "meta": {
            "disclaimer": "Fixture disclaimer",
            "freshness": {"status": "dated", "as_of": "2026-09-04", "observed_at": "2026-09-06T01:00:00Z", "warnings": []},
            "data_quality": {"schema": "data_quality_v1", "flags": []},
        },
    }


def test_retail_plan_matches_registered_profile_and_validates_all_requests():
    from cn_stock_mcp.app.services.tool_profiles import RETAIL_V1_PREVIEW
    from cn_stock_mcp.server.schemas import (
        TradingCalendarRequest, StockSearchRequest, StockQuoteRequest, StockHistoryRequest,
        StockSnapshotRequest, StockReviewRequest, WatchlistReviewRequest, MarketBriefRequest,
        HotThemeTrackerRequest, SectorReviewRequest,
    )
    models = (TradingCalendarRequest, StockSearchRequest, StockQuoteRequest, StockHistoryRequest,
              StockSnapshotRequest, StockReviewRequest, WatchlistReviewRequest, MarketBriefRequest,
              HotThemeTrackerRequest, SectorReviewRequest)
    assert set(TOOLS) == RETAIL_V1_PREVIEW
    for tool, model in zip(TOOLS, models, strict=True):
        model.model_validate(request_for(tool, {"trade_date": "2026-09-04", "sector_name": "银行"}))
    theme = request_for("hot_theme_tracker", {"trade_date": "2026-09-04"})
    assert "sector_names" not in theme
    assert theme["sector_limit"] == 2 and theme["member_limit"] == 2
    assert theme["include_pool_snapshot"] is False


@pytest.mark.parametrize("tool", TOOLS)
def test_complete_response_records_only_evidence(tool):
    data = envelope(tool)
    data["data"]["private_debug"] = "DO_NOT_REPORT_TOKEN_OR_RAW_DATA"
    result = assess(tool, data, elapsed_ms=123)
    assert result["status"] == "PASS"
    assert result["sources"] == ["akshare"]
    assert result["as_of"] == "2026-09-04"
    assert result["latency_ms"] == 123
    assert "DO_NOT_REPORT" not in json.dumps(result)


@pytest.mark.parametrize("flag,status", [
    ("partial_failure", "PARTIAL"), ("stale_cache", "PARTIAL"),
    ("aged_data", "PARTIAL"), ("empty_records", "PARTIAL"),
    ("semantic_anomalies", "FAIL"), ("anomalous_values", "FAIL"),
])
def test_quality_problems_do_not_pass(flag, status):
    data = envelope()
    data["meta"]["data_quality"]["flags"] = [flag]
    assert assess("stock_quote", data, elapsed_ms=1)["status"] == status


def test_nested_failures_empty_sections_and_unknown_time_do_not_pass():
    data = envelope()
    data["data"]["items"][0]["errors"] = [{"error_code": "PROVIDER_TIMEOUT", "message": "secret"}]
    assert assess("stock_quote", data, elapsed_ms=1)["status"] == "PARTIAL"
    data = envelope("stock_snapshot")
    data["data"]["items"][0]["history"]["items"] = []
    assert assess("stock_snapshot", data, elapsed_ms=1)["status"] == "PARTIAL"
    data = envelope()
    data["meta"]["freshness"].update(status="unknown", as_of=None)
    assert assess("stock_quote", data, elapsed_ms=1)["status"] == "PARTIAL"
    assert assess("stock_search", data, elapsed_ms=1)["status"] == "PASS"


def test_invalid_numbers_future_times_and_error_payloads_are_safe():
    data = envelope()
    data["data"]["items"][0]["price"] = float("nan")
    assert assess("stock_quote", data, elapsed_ms=1)["reason"] == "NON_FINITE_DATA"
    data = envelope()
    data["meta"]["freshness"]["warnings"] = ["source_time_in_future"]
    assert assess("stock_quote", data, elapsed_ms=1)["status"] == "FAIL"
    for code, status in [("PROVIDER_AUTH_FAILED", "BLOCKED"), ("INVALID_ARGUMENT", "FAIL"), ("secret-token", "FAIL")]:
        result = assess("stock_quote", {"success": False, "error": {"error_code": code, "message": "secret-token"}}, elapsed_ms=1)
        assert result["status"] == status
        assert "secret-token" not in json.dumps(result)


def test_invalid_collection_shape_is_not_a_successful_sample():
    data = envelope()
    data["data"]["items"] = {"price": 10.5}
    assert assess("stock_quote", data, elapsed_ms=1)["reason"] == "INVALID_DATA_SHAPE"


class Session:
    def __init__(self, broken=None):
        self.calls = []
        self.broken = broken

    async def call_tool(self, tool, arguments):
        self.calls.append((tool, arguments))
        data = envelope(tool)
        if self.broken == tool:
            data["data"]["items"] = []
        return SimpleNamespace(structured_content=data, content=[], is_error=False)


def test_ten_calls_resolve_calendar_and_theme_without_full_tools():
    session = Session()
    report = new_report("0.2.3", 60, 60)
    anyio.run(partial(run_cases, session, report))
    assert report["status"] == "PASS"
    assert report["remaining_tools"] == []
    calls = dict(session.calls)
    assert len(calls) == 10
    assert calls["stock_review"]["trade_date"] == "2026-09-04"
    assert calls["sector_review"]["sector_name"] == "银行"
    assert report["host_acceptance"] == "NOT_RUN"


def test_partial_response_stops_and_saves_remaining_tools():
    session = Session(broken="stock_quote")
    report = new_report("0.2.3", 60, 60)
    saved = []
    anyio.run(partial(run_cases, session, report, lambda: saved.append(deepcopy(report))))
    assert report["status"] == "PARTIAL"
    assert len(session.calls) == 3
    assert report["remaining_tools"] == list(TOOLS[3:])
    assert saved[-1] == report


def test_transport_exception_never_exposes_message_and_stops():
    class BrokenSession:
        async def call_tool(self, tool, arguments):
            raise RuntimeError("https://api.example/secret-token")

    report = new_report("0.2.3", 60, 60)
    anyio.run(partial(run_cases, BrokenSession(), report))
    assert report["status"] == "FAIL"
    assert len(report["checks"]) == 1
    assert "secret-token" not in json.dumps(report)


def test_timeout_stops_without_retries():
    class StalledSession:
        async def call_tool(self, tool, arguments):
            await anyio.sleep_forever()

    report = new_report("0.2.3", 0.01, 60)
    anyio.run(partial(run_cases, StalledSession(), report))
    assert report["status"] == "BLOCKED"
    assert len(report["checks"]) == 1
    assert report["checks"][0]["reason"] == "MCP_CALL_TIMEOUT"


def test_data_older_than_selected_trading_day_requires_review():
    class OldQuoteSession(Session):
        async def call_tool(self, tool, arguments):
            response = await super().call_tool(tool, arguments)
            if tool == "stock_quote":
                response.structured_content["meta"]["freshness"]["as_of"] = "2026-09-03"
            return response

    session = OldQuoteSession()
    report = new_report("0.2.3", 60, 60)
    anyio.run(partial(run_cases, session, report))
    assert report["status"] == "PARTIAL"
    assert len(session.calls) == 3
    assert report["checks"][-1]["reason"] == "SOURCE_PRECEDES_SELECTED_TRADE_DATE"


def test_plan_does_not_read_config_or_start_server(tmp_path: Path, capsys, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("plan must not read config or start a process")

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr("scripts.verify_retail_acceptance.run_live", forbidden)
    assert main(["--command", str(tmp_path / "server.exe"), "--config", str(tmp_path / "secret.json"), "--expected-version", "0.2.3"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["mode"] == "plan_only" and report["status"] == "BLOCKED"
    assert len(report["plan"]) == 10


def test_live_report_cannot_overwrite_config_or_existing_evidence(tmp_path: Path):
    config = tmp_path / "config.json"
    config.write_text("must remain unchanged", encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["--command", str(tmp_path / "server.exe"), "--config", str(config), "--expected-version", "0.2.3", "--report", str(config), "--run-live"])
    assert config.read_text(encoding="utf-8") == "must remain unchanged"

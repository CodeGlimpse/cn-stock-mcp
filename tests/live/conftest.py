from __future__ import annotations

import json
from datetime import date, datetime

import pytest

from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.zhitu_provider import ZhituProvider
from cn_stock_mcp.server.transport import TransportApp


def _has_zhitu() -> bool:
    return bool(get_settings().resolve_zhitu_token())


@pytest.fixture(scope="session")
def app():
    return TransportApp()


@pytest.fixture(scope="session")
def full_app():
    """Build the complete registry even when a user profile is configured."""
    return TransportApp(profile_override="full")


@pytest.fixture(scope="session")
def zhitu():
    if not _has_zhitu():
        pytest.skip("ZHITU token not available")
    return ZhituProvider()


@pytest.fixture(scope="session")
def recent_trade_date(app) -> str:
    result = app.call_tool("trading_calendar", {"market": "CN", "recent_limit": 5})
    assert result["success"] is True
    data = result["data"]
    recent = data.get("recent_trading_days") or []
    if recent:
        return recent[-1]
    previous = data.get("previous_trading_day")
    if previous:
        return previous
    current = data.get("date")
    assert current, "trading_calendar did not return a usable trade date"
    return str(current)


@pytest.fixture(scope="session")
def live_context(full_app) -> dict[str, str | None]:
    """Resolve dates and a live sector once for the functional suite.

    The suite must not depend on a hard-coded trading date or sector label.  A
    missing optional Zhitu sector is represented as ``None`` so only the
    sector-dependent cases can be skipped with an explicit reason.
    """
    calendar = full_app.call_tool("trading_calendar", {"market": "CN", "recent_limit": 8})
    data = assert_success(calendar)
    recent = [str(item) for item in data.get("recent_trading_days", []) if item]
    recent_date = recent[-1] if recent else str(data.get("previous_trading_day") or data.get("date"))
    assert recent_date and recent_date != "None", "trading_calendar did not return a usable trade date"

    previous_date = recent[-2] if len(recent) >= 2 else recent_date
    start_date = recent[0] if recent else previous_date

    sectors: dict[str, list[str]] = {"primary": [], "concept": []}
    if _has_zhitu():
        for sector_type in sectors:
            result = full_app.call_tool(
                "sector_lookup",
                {"mode": "list", "sector_type": sector_type, "limit": 3},
            )
            if result.get("success"):
                items = (result.get("data") or {}).get("items") or []
                sectors[sector_type] = [
                    str(item.get("name"))
                    for item in items
                    if isinstance(item, dict) and item.get("name")
                ]

    return {
        "recent_date": recent_date,
        "previous_date": previous_date,
        "start_date": start_date,
        "stock": "600519.SH",
        "stock_2": "000858.SZ",
        "index": "000001.SH",
        "index_code": "000300",
        "primary_sector": sectors["primary"][0] if sectors["primary"] else None,
        "primary_sector_2": sectors["primary"][1] if len(sectors["primary"]) > 1 else None,
        "concept_sector": sectors["concept"][0] if sectors["concept"] else None,
    }


def assert_success(result: dict) -> dict:
    assert result["success"] is True
    assert "data" in result
    return json.loads(json.dumps(result["data"], ensure_ascii=False, default=_json_default))


def _json_default(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, set):
        return list(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

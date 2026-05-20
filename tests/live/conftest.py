from __future__ import annotations

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
        return recent[-1].replace("-", "")
    previous = data.get("previous_trading_day")
    if previous:
        return previous.replace("-", "")
    current = data.get("date")
    assert current, "trading_calendar did not return a usable trade date"
    return str(current).replace("-", "")


def assert_success(result: dict) -> dict:
    assert result["success"] is True
    assert "data" in result
    return result["data"]

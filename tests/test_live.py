"""Live integration tests for openclaw-stock-mcp.

These tests require network access and valid provider credentials.
Run with: pytest -m live

They are excluded from default test runs (-m "not live").
"""
from __future__ import annotations

import pytest

from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.server.transport import TransportApp
from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


def _has_zhitu() -> bool:
    return bool(get_settings().resolve_zhitu_token())


def _to_jsonable(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    return value


# --- Shared fixtures ---

@pytest.fixture(scope="module")
def app():
    return TransportApp()


@pytest.fixture(scope="module")
def zhitu():
    if not _has_zhitu():
        pytest.skip("ZHITU token not available")
    return ZhituProvider()


# --- Meta ---

@pytest.mark.live
def test_list_tools(app):
    tools = app.list_tools()
    assert isinstance(tools, list)
    assert len(tools) >= 30


# --- Provider health ---

@pytest.mark.live
def test_provider_health(app):
    result = app.call_tool("provider_health", {})
    assert result["success"] is True


# --- Search ---

@pytest.mark.live
def test_stock_search(app):
    result = app.call_tool("stock_search", {"query": "平安银行", "limit": 5})
    assert result["success"] is True
    assert result["data"]["total"] >= 1


# --- Quote ---

@pytest.mark.live
def test_stock_quote_main(app):
    result = app.call_tool("stock_quote", {"symbols": ["600519.SH"], "sec_type": "stock"})
    assert result["success"] is True
    items = result["data"]["items"]
    assert len(items) >= 1


@pytest.mark.live
def test_stock_quote_index(app, zhitu):
    result = app.call_tool("stock_quote", {"symbols": ["000001.SH"], "sec_type": "index"})
    assert result["success"] is True


# --- Market overview ---

@pytest.mark.live
def test_market_overview(app, zhitu):
    result = app.call_tool("market_overview", {"market": "CN"})
    assert result["success"] is True


# --- Sector lookup ---

@pytest.mark.live
def test_sector_lookup_list_primary(app, zhitu):
    result = app.call_tool("sector_lookup", {"mode": "list", "sector_type": "primary", "limit": 5})
    assert result["success"] is True
    assert result["data"]["total"] >= 1


@pytest.mark.live
def test_sector_lookup_children(app, zhitu):
    result = app.call_tool("sector_lookup", {"mode": "children", "sector_name": "TFG板块趋势", "limit": 5})
    assert result["success"] is True


# --- History ---

@pytest.mark.live
def test_stock_history_daily(app):
    result = app.call_tool("stock_history", {"symbol": "600519", "sec_type": "stock", "interval": "1d", "limit": 5})
    assert result["success"] is True


# --- Review ---

@pytest.mark.live
def test_stock_review(app):
    result = app.call_tool("stock_review", {"symbol": "600519.SH", "trade_date": "2026-05-09"})
    assert result["success"] is True


# --- Technical indicator ---

@pytest.mark.live
def test_technical_indicator(app, zhitu):
    result = app.call_tool("technical_indicator", {"symbol": "000001.SH", "sec_type": "index", "interval": "1d", "indicator": "macd", "limit": 5})
    assert result["success"] is True


# --- Market pool (direct provider) ---

@pytest.mark.live
def test_market_pool_limit_up(zhitu):
    result = zhitu.get_market_pool(pool_type="limit_up", trade_date="2026-05-09")
    assert isinstance(result, list)


# --- Orderbook (direct provider) ---

@pytest.mark.live
def test_stock_orderbook_star(zhitu):
    result = zhitu.get_orderbook(symbol="688001.SH", sec_type="stock")
    assert result is not None


# --- BJ quote fallback ---

@pytest.mark.live
def test_stock_quote_bj(app, zhitu):
    result = app.call_tool("stock_quote", {"symbols": ["430001.BJ"], "sec_type": "stock"})
    assert result["success"] is True


# --- Concept sector ---

@pytest.mark.live
def test_sector_lookup_concept(app, zhitu):
    result = app.call_tool("sector_lookup", {"mode": "list", "sector_type": "concept", "limit": 5})
    assert result["success"] is True


@pytest.mark.live
def test_sector_review_concept(app, zhitu):
    result = app.call_tool("sector_review", {"sector_name": "人工智能", "sector_type": "concept", "trade_date": "2026-05-09", "top_n": 3, "limit": 5})
    assert result["success"] is True

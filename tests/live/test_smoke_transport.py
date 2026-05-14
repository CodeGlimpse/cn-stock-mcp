from __future__ import annotations

import pytest

from conftest import assert_success


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_list_tools_smoke(app):
    tools = app.list_tools()
    assert isinstance(tools, list)
    assert len(tools) >= 30


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_provider_health_smoke(app):
    data = assert_success(app.call_tool("provider_health", {}))
    assert isinstance(data, dict)


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_search_smoke(app):
    data = assert_success(app.call_tool("stock_search", {"query": "平安银行", "limit": 5}))
    assert data["total"] >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_quote_main_smoke(app):
    data = assert_success(app.call_tool("stock_quote", {"symbols": ["600519.SH"], "sec_type": "stock"}))
    assert len(data["items"]) >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_quote_index_smoke(app):
    data = assert_success(app.call_tool("stock_quote", {"symbols": ["000001.SH"], "sec_type": "index"}))
    assert len(data["items"]) >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_quote_bj_smoke(app):
    data = assert_success(app.call_tool("stock_quote", {"symbols": ["430001.BJ"], "sec_type": "stock"}))
    assert len(data["items"]) >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_market_overview_smoke(app):
    data = assert_success(app.call_tool("market_overview", {"market": "CN"}))
    assert isinstance(data, dict)


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_sector_lookup_list_primary_smoke(app):
    data = assert_success(app.call_tool("sector_lookup", {"mode": "list", "sector_type": "primary", "limit": 5}))
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_sector_lookup_list_concept_smoke(app):
    data = assert_success(app.call_tool("sector_lookup", {"mode": "list", "sector_type": "concept", "limit": 5}))
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_history_daily_smoke(app):
    data = assert_success(app.call_tool("stock_history", {"symbol": "600519", "sec_type": "stock", "interval": "1d", "limit": 5}))
    assert len(data["items"]) >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_review_smoke(app, recent_trade_date):
    data = assert_success(app.call_tool("stock_review", {"symbol": "600519.SH", "trade_date": recent_trade_date}))
    assert isinstance(data, dict)

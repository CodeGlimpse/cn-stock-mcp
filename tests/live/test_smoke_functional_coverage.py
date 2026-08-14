from __future__ import annotations

import pytest

from conftest import assert_success


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_market_brief_without_pools_live(app):
    data = assert_success(app.call_tool("market_brief", {"include_pools": False, "top_n": 3}))
    assert data["mode"] == "realtime_brief"
    assert isinstance(data.get("overview"), dict)
    assert isinstance(data.get("index_ranking"), list)
    assert data["member_count"] == len(data["index_ranking"])


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_profile_live(app):
    data = assert_success(app.call_tool("stock_profile", {"symbol": "600519.SH", "include": ["profile"]}))
    assert data["resolved_symbol"] == "600519.SH"
    assert isinstance(data.get("profile"), dict)
    assert data["meta"]["provider_used"]


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_stock_financial_snapshot_live(app):
    data = assert_success(app.call_tool("stock_financial", {"symbol": "600519.SH", "include": ["snapshot"]}))
    assert data["symbol"] == "600519.SH"
    assert data["history"] == []
    assert data["details"] == []
    assert data["snapshot"] is not None


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_capital_flow_market_live(app):
    data = assert_success(app.call_tool("capital_flow", {"flow_type": "market", "limit": 5}))
    assert data["flow_type"] == "market"
    assert data["count"] >= 1
    assert len(data["records"]) >= 1


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_etf_snapshot_spot_live(app):
    data = assert_success(app.call_tool("etf_snapshot", {"include": ["spot"], "top_n": 5}))
    assert data["spot_count"] >= 1
    assert len(data["spot"]) >= 1
    assert data["scale"] == []
    assert data["nav"] == []


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.transport
def test_macro_indicator_cpi_live(app):
    data = assert_success(app.call_tool("macro_indicator", {"indicator": "cpi", "region": "cn", "include": ["latest"]}))
    assert data["indicator"] == "cpi"
    assert data["region"] == "cn"
    assert data["latest"] is not None

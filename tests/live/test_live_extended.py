from __future__ import annotations

import pytest

from conftest import assert_success


@pytest.mark.live
@pytest.mark.slow
@pytest.mark.transport
def test_sector_lookup_children_live(app):
    primary = assert_success(app.call_tool("sector_lookup", {"mode": "list", "sector_type": "primary", "limit": 5}))
    assert len(primary["items"]) >= 1
    sector_name = primary["items"][0]["name"]
    children = assert_success(app.call_tool("sector_lookup", {"mode": "children", "sector_type": "primary", "sector_name": sector_name, "limit": 5}))
    assert isinstance(children, dict)


@pytest.mark.live
@pytest.mark.slow
@pytest.mark.transport
def test_technical_indicator_live(app):
    data = assert_success(app.call_tool("technical_indicator", {"symbol": "000001.SH", "sec_type": "index", "interval": "1d", "indicator": "macd", "limit": 5}))
    assert len(data["items"]) >= 1


@pytest.mark.live
@pytest.mark.slow
@pytest.mark.transport
def test_sector_review_concept_live(app, recent_trade_date):
    concepts = assert_success(app.call_tool("sector_lookup", {"mode": "list", "sector_type": "concept", "limit": 5}))
    assert len(concepts["items"]) >= 1
    sector_name = concepts["items"][0]["name"]
    data = assert_success(app.call_tool("sector_review", {"sector_name": sector_name, "sector_type": "concept", "trade_date": recent_trade_date, "top_n": 3, "limit": 5}))
    assert isinstance(data, dict)

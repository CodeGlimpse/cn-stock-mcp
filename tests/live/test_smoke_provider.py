from __future__ import annotations

import pytest


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.provider
def test_market_pool_limit_up_smoke(zhitu, recent_trade_date):
    result = zhitu.get_market_pool(pool_type="limit_up", trade_date=recent_trade_date)
    assert isinstance(result, list)


@pytest.mark.live
@pytest.mark.smoke
@pytest.mark.provider
def test_stock_orderbook_star_smoke(zhitu):
    result = zhitu.get_orderbook(symbol="688001.SH", sec_type="stock")
    assert result is not None

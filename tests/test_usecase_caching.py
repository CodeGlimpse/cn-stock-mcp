"""Tests for usecase-level caching in stock_quote, market_overview, technical_indicator, orderbook, market_pool."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase
from cn_stock_mcp.app.usecases.market_overview import MarketOverviewUseCase
from cn_stock_mcp.app.usecases.technical_indicator import TechnicalIndicatorUseCase
from cn_stock_mcp.app.usecases.stock_orderbook import OrderbookUseCase
from cn_stock_mcp.app.usecases.market_pool import MarketPoolUseCase


def _make_quote_request(**overrides):
    from cn_stock_mcp.server.schemas import StockQuoteRequest
    defaults = {"symbols": ["600519.SH"], "sec_type": "stock"}
    defaults.update(overrides)
    return StockQuoteRequest(**defaults)


def _make_overview_request(**overrides):
    from cn_stock_mcp.server.schemas import MarketOverviewRequest
    defaults = {"market": "CN"}
    defaults.update(overrides)
    return MarketOverviewRequest(**defaults)


def _make_indicator_request(**overrides):
    from cn_stock_mcp.server.schemas import TechnicalIndicatorRequest
    defaults = {"symbol": "000001.SH", "interval": "1d", "indicator": "macd", "sec_type": "index"}
    defaults.update(overrides)
    return TechnicalIndicatorRequest(**defaults)


def _make_orderbook_request(**overrides):
    from cn_stock_mcp.server.schemas import StockOrderbookRequest
    defaults = {"symbol": "600519.SH", "sec_type": "stock"}
    defaults.update(overrides)
    return StockOrderbookRequest(**defaults)


def _make_pool_request(**overrides):
    from cn_stock_mcp.server.schemas import MarketPoolRequest
    defaults = {"pool_type": "limit_up", "trade_date": "2026-05-06"}
    defaults.update(overrides)
    return MarketPoolRequest(**defaults)


# --- stock_quote cache ---

def test_stock_quote_uses_cache_on_second_call():
    uc = StockQuoteUseCase()
    # Pre-fill cache
    fake_quote = {"symbol": "600519.SH", "price": 1800.0}
    uc.quote_cache.set("quote:600519.SH:stock", fake_quote)

    req = _make_quote_request()
    result = uc.execute(req)
    assert result["items"][0] == fake_quote
    assert result["meta"]["per_symbol"][0]["provider_used"] == "cache"


# --- market_overview cache ---

def test_market_overview_uses_cache_on_second_call():
    uc = MarketOverviewUseCase()
    fake_overview = {"market": "CN", "indices": [], "source": "zhitu", "meta": {}}
    uc.overview_cache.set("overview:CN", fake_overview)

    req = _make_overview_request()
    result = uc.execute(req)
    assert result == fake_overview


# --- technical_indicator cache ---

def test_technical_indicator_uses_cache_on_second_call():
    uc = TechnicalIndicatorUseCase()
    fake_payload = {"symbol": "000001.SH", "interval": "1d", "indicator": "macd", "meta": {}}
    uc.indicator_cache.set("indicator:000001.SH:index:1d:macd:200", fake_payload)

    req = _make_indicator_request()
    result = uc.execute(req)
    assert result == fake_payload


# --- orderbook cache ---

def test_orderbook_uses_cache_on_second_call():
    uc = OrderbookUseCase()
    fake_payload = {"symbol": "600519.SH", "bids": [], "asks": [], "meta": {}, "source": "zhitu"}
    uc.orderbook_cache.set("orderbook:600519.SH:stock", fake_payload)

    req = _make_orderbook_request()
    result = uc.execute(req)
    assert result == fake_payload


# --- market_pool cache ---

def test_market_pool_uses_cache_on_second_call():
    uc = MarketPoolUseCase()
    fake_result = {
        "pool_type": "limit_up",
        "trade_date": "2026-05-06",
        "requested_trade_date": "2026-05-06",
        "items": [{"symbol": "000001.SZ"}],
        "count": 1,
        "source": "zhitu",
        "meta": {"calendar": {}},
    }
    uc.pool_cache.set("pool:limit_up:2026-05-06", fake_result)

    req = _make_pool_request()
    result = uc.execute(req)
    assert result["items"] == [{"symbol": "000001.SZ"}]
    assert result["source"] == "zhitu"


def test_market_pool_explicit_date_cache_hit_skips_calendar_lookup(monkeypatch):
    uc = MarketPoolUseCase()
    fake_result = {
        "pool_type": "limit_up",
        "trade_date": "2026-05-06",
        "requested_trade_date": "2026-05-06",
        "items": [{"symbol": "000001.SZ"}],
        "count": 1,
        "source": "zhitu",
        "meta": {"calendar": {}},
    }
    uc.pool_cache.set("pool:limit_up:2026-05-06", fake_result)

    def fail_if_calendar_is_called(_):
        raise AssertionError("calendar lookup should not run on an explicit cache hit")

    monkeypatch.setattr(uc, "_resolve_effective_trade_date", fail_if_calendar_is_called)

    result = uc.execute(_make_pool_request(limit=1))

    assert result["items"] == [{"symbol": "000001.SZ"}]

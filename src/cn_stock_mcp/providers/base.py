from __future__ import annotations

from typing import Protocol

from cn_stock_mcp.app.models.bar import Bar
from cn_stock_mcp.app.models.indicator import IndicatorSeries
from cn_stock_mcp.app.models.instrument import Instrument
from cn_stock_mcp.app.models.market_pool import MarketPoolItem
from cn_stock_mcp.app.models.orderbook import OrderBook
from cn_stock_mcp.app.models.quote import Quote


class MarketDataProvider(Protocol):
    name: str

    def search_instruments(
        self,
        query: str,
        sec_types: list[str] | None = None,
        market: str | None = None,
        limit: int = 10,
    ) -> list[Instrument]: ...

    def get_quote(
        self,
        symbol: str,
        sec_type: str,
    ) -> Quote: ...

    def get_quotes(
        self,
        symbols: list[str],
        sec_type: str | None = None,
    ) -> list[Quote]: ...

    def get_history(
        self,
        symbol: str,
        sec_type: str,
        interval: str,
        start: str | None = None,
        end: str | None = None,
        limit: int | None = None,
        adjust: str | None = None,
    ) -> list[Bar]: ...

    def get_orderbook(
        self,
        symbol: str,
        sec_type: str,
    ) -> OrderBook: ...

    def get_indicator(
        self,
        symbol: str,
        sec_type: str,
        interval: str,
        indicator: str,
        start: str | None = None,
        end: str | None = None,
        limit: int | None = None,
    ) -> IndicatorSeries: ...

    def get_market_overview(self, market: str = "CN") -> dict: ...

    def get_market_pool(
        self,
        pool_type: str,
        trade_date: str | None = None,
    ) -> list[MarketPoolItem]: ...

    def get_trading_calendar(
        self,
        market: str = "CN",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        recent_limit: int = 5,
    ) -> dict: ...

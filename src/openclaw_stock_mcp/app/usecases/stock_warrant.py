from __future__ import annotations

from openclaw_stock_mcp.app.models.stock_warrant import StockWarrantResult
from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.providers.adapters.akshare_stock_warrant_adapters import (
    adapt_option_row,
    build_warrant_summary,
)


class StockWarrantUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if StockWarrantUseCase._shared_cache is None:
            StockWarrantUseCase._shared_cache = CacheService(maxsize=16, ttl=30)
        self.cache = StockWarrantUseCase._shared_cache

    def execute(self, request) -> dict:
        include = request.include
        etf_type = getattr(request, "etf_type", "50ETF期权")
        commodity_exchange = getattr(request, "commodity_exchange", "郑商所")
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        etf = []
        commodity = []
        index = []

        if "etf_option" in include:
            cache_key = f"warrant:etf:{etf_type}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_etf_option(symbol=etf_type)
                self.cache.set(cache_key, raw_rows)
            etf = [adapt_option_row(r) for r in raw_rows]
            if top_n:
                etf = etf[:top_n]

        if "commodity_option" in include:
            cache_key = f"warrant:commodity:{commodity_exchange}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_commodity_option(exchange=commodity_exchange)
                self.cache.set(cache_key, raw_rows)
            commodity = [adapt_option_row(r) for r in raw_rows]
            if top_n:
                commodity = commodity[:top_n]

        if "index_option" in include:
            cache_key = "warrant:index:latest"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_index_option()
                self.cache.set(cache_key, raw_rows)
            index = [adapt_option_row(r) for r in raw_rows]
            if top_n:
                index = index[:top_n]

        summary = build_warrant_summary(etf, commodity, index)

        result = StockWarrantResult(
            etf_option=etf,
            etf_option_count=len(etf),
            commodity_option=commodity,
            commodity_option_count=len(commodity),
            index_option=index,
            index_option_count=len(index),
            summary=summary,
        )
        return result.model_dump()

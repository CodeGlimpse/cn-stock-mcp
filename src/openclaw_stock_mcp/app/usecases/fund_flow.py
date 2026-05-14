from __future__ import annotations

from openclaw_stock_mcp.app.models.fund_flow import FundFlowResult
from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.providers.adapters.akshare_fund_flow_adapters import (
    adapt_industry_fund_flow_row,
    adapt_market_fund_flow_row,
    adapt_stock_fund_flow_row,
    build_fund_flow_summary,
)


class FundFlowUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if FundFlowUseCase._shared_cache is None:
            FundFlowUseCase._shared_cache = CacheService(maxsize=16, ttl=30)
        self.cache = FundFlowUseCase._shared_cache

    def execute(self, request) -> dict:
        include = request.include
        period = getattr(request, "period", "即时")
        symbol = getattr(request, "symbol", "")
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        market = []
        industry = []
        stock = []

        if "market" in include:
            cache_key = "fundflow:market"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_market_fund_flow()
                self.cache.set(cache_key, raw_rows)
            market = [adapt_market_fund_flow_row(r) for r in raw_rows]
            if top_n:
                market = market[-top_n:]  # market is time-series, return latest N

        if "industry" in include:
            cache_key = f"fundflow:industry:{period}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_industry_fund_flow(symbol=period)
                self.cache.set(cache_key, raw_rows)
            industry = [adapt_industry_fund_flow_row(r) for r in raw_rows]
            industry = self._sort_industry(industry, request)
            if top_n:
                industry = industry[:top_n]

        if "stock" in include:
            if not symbol:
                raise ValueError("symbol is required when include contains 'stock'")
            code = symbol.split(".")[0] if "." in symbol else symbol
            market_code = self._infer_market(code)
            cache_key = f"fundflow:stock:{code}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_stock_fund_flow(stock=code, market=market_code)
                self.cache.set(cache_key, raw_rows)
            stock = [adapt_stock_fund_flow_row(r) for r in raw_rows]
            if top_n:
                stock = stock[-top_n:]  # stock is time-series, return latest N

        summary = build_fund_flow_summary(market, industry, stock)

        result = FundFlowResult(
            market=market,
            market_count=len(market),
            industry=industry,
            industry_count=len(industry),
            stock=stock,
            stock_count=len(stock),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_industry(items: list, request) -> list:
        sort_by = getattr(request, "sort_by", "net_inflow")
        descending = getattr(request, "descending", True)
        key_map = {
            "net_inflow": "net_inflow",
            "inflow": "inflow",
            "change_pct": "change_pct",
        }
        sort_key = key_map.get(sort_by, "net_inflow")

        def _get_val(item):
            v = getattr(item, sort_key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

    @staticmethod
    def _infer_market(code: str) -> str:
        if code.startswith(("6", "9")):
            return "sh"
        return "sz"

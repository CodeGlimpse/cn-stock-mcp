from __future__ import annotations

from openclaw_stock_mcp.app.models.dividend_rank import DividendRankResult
from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.providers.adapters.akshare_dividend_rank_adapters import (
    adapt_dividend_detail_row,
    adapt_dividend_plan_row,
    adapt_dividend_rank_row,
    build_dividend_summary,
)


class DividendRankUseCase:
    _shared_rank_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()
        settings = get_settings()
        if DividendRankUseCase._shared_rank_cache is None:
            # Cache rank data for 1 hour (changes infrequently)
            DividendRankUseCase._shared_rank_cache = CacheService(
                maxsize=8, ttl=3600
            )
        self.rank_cache = DividendRankUseCase._shared_rank_cache

    def execute(self, request) -> dict:
        include = request.include
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n
        report_date = getattr(request, "report_date", "latest")
        symbol = getattr(request, "symbol", None)
        sec_type = getattr(request, "sec_type", "stock")

        provider = self.router.get_provider("akshare")

        rank = []
        plan = []
        detail = []

        if "rank" in include:
            cache_key = "dividend:history_rank"
            raw_rows = self.rank_cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_dividend_history_rank()
                self.rank_cache.set(cache_key, raw_rows)
            rank = [adapt_dividend_rank_row(r) for r in raw_rows]
            rank = self._sort_items(rank, sort_by, descending)
            if top_n:
                rank = rank[:top_n]

        if "plan" in include:
            eff_date = self._resolve_report_date(report_date)
            raw_rows = provider.get_dividend_plan(date=eff_date)
            plan = [adapt_dividend_plan_row(r) for r in raw_rows]
            # Filter out NaN dividend_yield rows if sorting by yield
            if sort_by == "dividend_yield":
                plan = [p for p in plan if p.dividend_yield is not None]
            plan = self._sort_plan(plan, sort_by, descending)
            if top_n:
                plan = plan[:top_n]

        if "detail" in include and symbol:
            resolved = self.resolver.resolve(symbol, sec_type)
            code = resolved.symbol.split(".", 1)[0]
            raw_rows = provider.get_dividend_detail(symbol=code)
            detail = [adapt_dividend_detail_row(r) for r in raw_rows]
            if top_n:
                detail = detail[:top_n]

        summary = build_dividend_summary(rank, plan, detail)

        result = DividendRankResult(
            rank=rank,
            rank_count=len(rank),
            plan=plan,
            plan_count=len(plan),
            detail=detail,
            detail_count=len(detail),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _resolve_report_date(report_date: str) -> str:
        if report_date != "latest":
            return report_date.replace("-", "")
        # Latest complete year
        from datetime import date
        year = date.today().year - 1
        return f"{year}1231"

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        key_map = {
            "total_dividend": "total_dividend",
            "avg_annual_dividend": "avg_annual_dividend",
            "dividend_count": "dividend_count",
        }
        sort_key = key_map.get(key, "avg_annual_dividend")

        def _get_val(item):
            v = getattr(item, sort_key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

    @staticmethod
    def _sort_plan(items: list, key: str, descending: bool = True) -> list:
        key_map = {
            "dividend_yield": "dividend_yield",
            "cash_dividend_ratio": "cash_dividend_ratio",
            "eps": "eps",
        }
        sort_key = key_map.get(key, "dividend_yield")

        def _get_val(item):
            v = getattr(item, sort_key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

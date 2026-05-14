from __future__ import annotations

from openclaw_stock_mcp.app.models.disclosure_calendar import DisclosureResult
from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.providers.adapters.akshare_disclosure_calendar_adapters import (
    adapt_disclosure_row,
    build_disclosure_summary,
)


class DisclosureCalendarUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if DisclosureCalendarUseCase._shared_cache is None:
            # Cache for 30 minutes (disclosure schedule doesn't change frequently)
            DisclosureCalendarUseCase._shared_cache = CacheService(maxsize=16, ttl=1800)
        self.cache = DisclosureCalendarUseCase._shared_cache

    def execute(self, request) -> dict:
        market = request.market
        period = request.period
        symbol = getattr(request, "symbol", None)
        status = getattr(request, "status", "all")
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        cache_key = f"disclosure:{market}:{period}"
        raw_rows = self.cache.get(cache_key)
        if raw_rows is None:
            raw_rows = provider.get_disclosure_calendar(market=market, period=period)
            self.cache.set(cache_key, raw_rows)

        items = [adapt_disclosure_row(r) for r in raw_rows]

        # Filter by symbol
        if symbol:
            from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
            resolver = SymbolResolver()
            resolved = resolver.resolve(symbol, getattr(request, "sec_type", "stock"))
            items = [i for i in items if i.symbol == resolved.symbol]

        # Filter by status
        if status == "disclosed":
            items = [i for i in items if i.actual_date is not None]
        elif status == "pending":
            items = [i for i in items if i.first_schedule is not None and i.actual_date is None]
        elif status == "changed":
            items = [i for i in items if i.change_1 is not None]

        # Sort
        items = self._sort_items(items, sort_by, descending)
        if top_n:
            items = items[:top_n]

        summary = build_disclosure_summary(items, period, market)

        result = DisclosureResult(
            items=items,
            total_count=len(items),
            period=period,
            market=market,
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        if key == "first_schedule":
            def _get_val(item):
                v = item.first_schedule
                if v is None:
                    return "9999-99-99" if descending else "0000-00-00"
                return v
            return sorted(items, key=_get_val, reverse=descending)
        elif key == "actual_date":
            def _get_val(item):
                v = item.actual_date
                if v is None:
                    return "9999-99-99" if descending else "0000-00-00"
                return v
            return sorted(items, key=_get_val, reverse=descending)
        return items

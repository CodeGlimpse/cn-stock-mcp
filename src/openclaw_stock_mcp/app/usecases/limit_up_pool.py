from __future__ import annotations

from datetime import date

from openclaw_stock_mcp.app.models.limit_up_pool import LimitUpPoolResult
from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.providers.adapters.akshare_limit_up_pool_adapters import (
    adapt_broken_row,
    adapt_limit_down_row,
    adapt_limit_up_row,
    adapt_previous_row,
    adapt_strong_row,
    adapt_sub_new_row,
    build_limit_up_summary,
)


class LimitUpPoolUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if LimitUpPoolUseCase._shared_cache is None:
            LimitUpPoolUseCase._shared_cache = CacheService(maxsize=32, ttl=60)
        self.cache = LimitUpPoolUseCase._shared_cache

    def execute(self, request) -> dict:
        include = request.include
        trade_date = getattr(request, "trade_date", "")
        top_n = request.top_n

        if not trade_date:
            trade_date = date.today().strftime("%Y%m%d")

        provider = self.router.get_provider("akshare")

        limit_up = []
        limit_down = []
        strong = []
        previous = []
        sub_new = []
        broken = []

        if "limit_up" in include:
            cache_key = f"limitup:zt:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_limit_up_pool_raw(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            limit_up = [adapt_limit_up_row(r) for r in raw_rows]
            if top_n:
                limit_up = limit_up[:top_n]

        if "limit_down" in include:
            cache_key = f"limitup:dt:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_limit_down_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            limit_down = [adapt_limit_down_row(r) for r in raw_rows]

        if "strong" in include:
            cache_key = f"limitup:strong:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_strong_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            strong = [adapt_strong_row(r) for r in raw_rows]
            if top_n:
                strong = strong[:top_n]

        if "previous" in include:
            cache_key = f"limitup:prev:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_previous_limit_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            previous = [adapt_previous_row(r) for r in raw_rows]
            if top_n:
                previous = previous[:top_n]

        if "sub_new" in include:
            cache_key = f"limitup:subnew:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_sub_new_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            sub_new = [adapt_sub_new_row(r) for r in raw_rows]
            if top_n:
                sub_new = sub_new[:top_n]

        if "broken" in include:
            cache_key = f"limitup:broken:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_broken_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            broken = [adapt_broken_row(r) for r in raw_rows]

        summary = build_limit_up_summary(limit_up, limit_down, strong, previous, sub_new, broken)

        result = LimitUpPoolResult(
            limit_up=limit_up,
            limit_up_count=len(limit_up),
            limit_down=limit_down,
            limit_down_count=len(limit_down),
            strong=strong,
            strong_count=len(strong),
            previous=previous,
            previous_count=len(previous),
            sub_new=sub_new,
            sub_new_count=len(sub_new),
            broken=broken,
            broken_count=len(broken),
            summary=summary,
        )
        return result.model_dump()

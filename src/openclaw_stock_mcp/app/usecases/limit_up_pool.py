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
    build_limit_up_sentiment,
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

        limit_up_full = []
        limit_down_full = []
        strong_full = []
        previous_full = []
        sub_new_full = []
        broken_full = []

        if "limit_up" in include:
            cache_key = f"limitup:zt:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_limit_up_pool_raw(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            limit_up_full = [adapt_limit_up_row(r) for r in raw_rows]

        if "limit_down" in include:
            cache_key = f"limitup:dt:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_limit_down_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            limit_down_full = [adapt_limit_down_row(r) for r in raw_rows]

        if "strong" in include:
            cache_key = f"limitup:strong:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_strong_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            strong_full = [adapt_strong_row(r) for r in raw_rows]

        if "previous" in include:
            cache_key = f"limitup:prev:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_previous_limit_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            previous_full = [adapt_previous_row(r) for r in raw_rows]

        if "sub_new" in include:
            cache_key = f"limitup:subnew:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_sub_new_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            sub_new_full = [adapt_sub_new_row(r) for r in raw_rows]

        if "broken" in include:
            cache_key = f"limitup:broken:{trade_date}"
            raw_rows = self.cache.get(cache_key)
            if raw_rows is None:
                raw_rows = provider.get_broken_pool(date=trade_date)
                self.cache.set(cache_key, raw_rows)
            broken_full = [adapt_broken_row(r) for r in raw_rows]

        sentiment = build_limit_up_sentiment(
            trade_date=trade_date,
            lu=limit_up_full,
            ld=limit_down_full,
            strong=strong_full,
            prev=previous_full,
            sub=sub_new_full,
            broken=broken_full,
        )
        summary = build_limit_up_summary(limit_up_full, limit_down_full, strong_full, previous_full, sub_new_full, broken_full, sentiment=sentiment)

        limit_up = limit_up_full[:top_n] if top_n and limit_up_full else limit_up_full
        limit_down = limit_down_full[:top_n] if top_n and limit_down_full else limit_down_full
        strong = strong_full[:top_n] if top_n and strong_full else strong_full
        previous = previous_full[:top_n] if top_n and previous_full else previous_full
        sub_new = sub_new_full[:top_n] if top_n and sub_new_full else sub_new_full
        broken = broken_full[:top_n] if top_n and broken_full else broken_full

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
            sentiment=sentiment,
            summary=summary,
        )
        return result.model_dump()

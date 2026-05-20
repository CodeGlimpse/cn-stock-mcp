from __future__ import annotations

from cn_stock_mcp.app.models.stock_screen import StockScreenResult
from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.adapters.akshare_stock_screen_adapters import (
    adapt_screen_row,
    build_filter_desc,
    build_screen_summary,
)


class StockScreenUseCase:
    _shared_spot_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if StockScreenUseCase._shared_spot_cache is None:
            # Cache the full spot table for 10 seconds
            StockScreenUseCase._shared_spot_cache = CacheService(
                maxsize=4, ttl=max(int(settings.cache_ttl_quote_seconds or 10), 5)
            )
        self.spot_cache = StockScreenUseCase._shared_spot_cache

    def execute(self, request) -> dict:
        market = request.market
        min_price = request.min_price
        max_price = request.max_price
        min_change_pct = request.min_change_pct
        max_change_pct = request.max_change_pct
        min_volume = request.min_volume
        min_turnover = request.min_turnover
        min_amplitude = request.min_amplitude
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n

        # Fetch full spot data (cached)
        cache_key = "screen:spot_all"
        raw_rows = self.spot_cache.get(cache_key)
        if raw_rows is None:
            provider = self.router.get_provider("akshare")
            raw_rows = provider.get_a_share_spot_all()
            self.spot_cache.set(cache_key, raw_rows)

        total_before = len(raw_rows)

        # Filter by market
        filtered = self._filter_market(raw_rows, market)

        # Adapt rows
        items = [adapt_screen_row(r) for r in filtered]

        # Apply price/change/volume/turnover/amplitude filters
        items = self._apply_filters(items, min_price, max_price, min_change_pct,
                                    max_change_pct, min_volume, min_turnover, min_amplitude)

        total_after = len(items)

        # Sort
        sort_key_map = {
            "change_pct": "change_pct",
            "turnover": "turnover",
            "volume": "volume",
            "latest_price": "latest_price",
            "amplitude": "amplitude",
        }
        sort_key = sort_key_map.get(sort_by, "change_pct")
        items = self._sort_items(items, sort_key, descending)

        # Top N
        if top_n:
            items = items[:top_n]

        filter_desc = build_filter_desc(
            market, min_price, max_price, min_change_pct, max_change_pct,
            min_volume, min_turnover, min_amplitude, sort_by, top_n
        )
        summary = build_screen_summary(total_before, total_after, items, filter_desc)

        result = StockScreenResult(
            filter_desc=filter_desc,
            total_before_filter=total_before,
            total_after_filter=total_after,
            items=items,
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _filter_market(rows: list[dict], market: str) -> list[dict]:
        if market == "all":
            return rows
        result = []
        for row in rows:
            raw_code = str(row.get("代码", "")).strip()
            if market == "sh" and not raw_code.startswith("sh"):
                continue
            if market == "sz" and not raw_code.startswith("sz"):
                continue
            if market == "bj" and not raw_code.startswith("bj"):
                continue
            if market == "main":
                if not (raw_code.startswith("sh6") or raw_code.startswith("sz00") or raw_code.startswith("sz001")):
                    continue
            if market == "star" and not raw_code.startswith("sh688"):
                continue
            if market == "gem" and not (raw_code.startswith("sz30") or raw_code.startswith("sz301")):
                continue
            result.append(row)
        return result

    @staticmethod
    def _apply_filters(items, min_price, max_price, min_change_pct,
                       max_change_pct, min_volume, min_turnover, min_amplitude):
        result = []
        for item in items:
            if min_price is not None and (item.latest_price is None or item.latest_price < min_price):
                continue
            if max_price is not None and (item.latest_price is None or item.latest_price > max_price):
                continue
            if min_change_pct is not None and (item.change_pct is None or item.change_pct < min_change_pct):
                continue
            if max_change_pct is not None and (item.change_pct is None or item.change_pct > max_change_pct):
                continue
            if min_volume is not None and (item.volume is None or item.volume < min_volume):
                continue
            if min_turnover is not None and (item.turnover is None or item.turnover < min_turnover):
                continue
            if min_amplitude is not None and (item.amplitude is None or item.amplitude < min_amplitude):
                continue
            result.append(item)
        return result

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        def _get_val(item):
            v = getattr(item, key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v
        return sorted(items, key=_get_val, reverse=descending)

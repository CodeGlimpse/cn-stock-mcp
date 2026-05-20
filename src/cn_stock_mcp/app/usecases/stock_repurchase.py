from __future__ import annotations

from cn_stock_mcp.app.models.stock_repurchase import RepurchaseResult
from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.adapters.akshare_stock_repurchase_adapters import (
    adapt_repurchase_row,
    build_repurchase_summary,
)


class StockRepurchaseUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if StockRepurchaseUseCase._shared_cache is None:
            # Cache for 10 minutes
            StockRepurchaseUseCase._shared_cache = CacheService(maxsize=4, ttl=600)
        self.cache = StockRepurchaseUseCase._shared_cache

    def execute(self, request) -> dict:
        status = request.status
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n
        symbol = getattr(request, "symbol", None)

        provider = self.router.get_provider("akshare")

        cache_key = "repurchase:all"
        raw_rows = self.cache.get(cache_key)
        if raw_rows is None:
            raw_rows = provider.get_stock_repurchase()
            self.cache.set(cache_key, raw_rows)

        items = [adapt_repurchase_row(r) for r in raw_rows]

        # Filter by status
        if status != "all":
            items = [i for i in items if i.progress == status]

        # Filter by symbol
        if symbol:
            from cn_stock_mcp.app.services.symbol_resolver import SymbolResolver
            resolver = SymbolResolver()
            resolved = resolver.resolve(symbol, getattr(request, "sec_type", "stock"))
            items = [i for i in items if i.symbol == resolved.symbol]

        # Sort
        items = self._sort_items(items, sort_by, descending)
        if top_n:
            items = items[:top_n]

        summary = build_repurchase_summary(items, status)

        result = RepurchaseResult(
            items=items,
            total_count=len(items),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        key_map = {
            "done_amount": "done_amount",
            "plan_amount_max": "plan_amount_max",
            "plan_ratio_max": "plan_ratio_max",
            "latest_price": "latest_price",
            "start_date": "start_date",
        }
        sort_key = key_map.get(key, "done_amount")

        def _get_val(item):
            v = getattr(item, sort_key, None)
            if v is None:
                if sort_key == "start_date":
                    return "9999-99-99" if descending else "0000-00-00"
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

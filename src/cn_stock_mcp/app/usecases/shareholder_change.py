from __future__ import annotations

from cn_stock_mcp.app.models.shareholder_change import ShareholderChangeResult
from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.app.services.symbol_resolver import SymbolResolver
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.adapters.akshare_shareholder_change_adapters import (
    adapt_change_row,
    adapt_top10_row,
    build_shareholder_summary,
)


class ShareholderChangeUseCase:
    _shared_change_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()
        settings = get_settings()
        if ShareholderChangeUseCase._shared_change_cache is None:
            # Cache change data for 1 hour (quarterly data)
            ShareholderChangeUseCase._shared_change_cache = CacheService(
                maxsize=8, ttl=3600
            )
        self.change_cache = ShareholderChangeUseCase._shared_change_cache

    def execute(self, request) -> dict:
        include = request.include
        symbol = getattr(request, "symbol", None)
        sec_type = getattr(request, "sec_type", "stock")
        quarter = request.quarter
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n
        shareholder_type = getattr(request, "shareholder_type", None)

        provider = self.router.get_provider("akshare")

        top10 = []
        change = []
        effective_quarter = quarter

        if quarter == "auto":
            effective_quarter = self._latest_quarter()

        if "top10" in include and symbol:
            resolved = self.resolver.resolve(symbol, sec_type)
            code = resolved.symbol.split(".", 1)[0]
            ak_symbol = self._to_ak_symbol(code, resolved.symbol)
            ak_date = effective_quarter[:4] + effective_quarter[4:]
            rows = provider.get_shareholder_top10(symbol=ak_symbol, date=ak_date)
            top10 = [adapt_top10_row(r) for r in rows]

        if "change" in include:
            cache_key = f"shareholder:change:{effective_quarter}"
            raw_rows = self.change_cache.get(cache_key)
            if raw_rows is None:
                ak_date = effective_quarter[:4] + effective_quarter[4:]
                raw_rows = provider.get_shareholder_change(date=ak_date)
                self.change_cache.set(cache_key, raw_rows)
            change = [adapt_change_row(r) for r in raw_rows]
            # Filter by shareholder_type if specified
            if shareholder_type:
                change = [c for c in change if c.shareholder_type == shareholder_type]
            # Sort
            change = self._sort_change(change, sort_by, descending)
            if top_n:
                change = change[:top_n]

        resolved_symbol = ""
        if symbol:
            resolved = self.resolver.resolve(symbol, sec_type)
            resolved_symbol = resolved.symbol

        summary = build_shareholder_summary(top10, change, resolved_symbol, effective_quarter)

        result = ShareholderChangeResult(
            top10=top10,
            top10_count=len(top10),
            change=change,
            change_count=len(change),
            symbol=resolved_symbol,
            quarter=effective_quarter,
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _to_ak_symbol(code: str, full_symbol: str) -> str:
        if full_symbol.endswith(".SH"):
            return f"sh{code}"
        if full_symbol.endswith(".SZ"):
            return f"sz{code}"
        if full_symbol.endswith(".BJ"):
            return f"bj{code}"
        return code

    @staticmethod
    def _latest_quarter() -> str:
        from datetime import date
        today = date.today()
        year = today.year
        month = today.month
        current_q = (month - 1) // 3 + 1
        q = current_q - 1
        y = year
        if q <= 0:
            q += 4
            y -= 1
        quarter_end = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}
        return f"{y}{quarter_end[q]}"

    @staticmethod
    def _sort_change(items: list, key: str, descending: bool = True) -> list:
        key_map = {
            "total_hold": "total_hold",
            "new_hold": "new_hold",
            "increase_hold": "increase_hold",
            "decrease_hold": "decrease_hold",
            "float_cap": "float_cap",
        }
        sort_key = key_map.get(key, "total_hold")

        def _get_val(item):
            v = getattr(item, sort_key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

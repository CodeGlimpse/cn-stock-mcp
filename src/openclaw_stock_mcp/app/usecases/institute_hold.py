from __future__ import annotations

from openclaw_stock_mcp.app.models.institute_hold import InstituteHoldResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.providers.adapters.akshare_institute_hold_adapters import (
    adapt_institute_hold_detail_row,
    adapt_institute_hold_summary_row,
    build_institute_hold_summary_text,
)


class InstituteHoldUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request) -> dict:
        include = request.include
        quarter = request.quarter
        symbol = getattr(request, "symbol", None)
        sec_type = getattr(request, "sec_type", "stock")
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        summary = []
        detail = []
        effective_quarter = quarter

        # Resolve quarter if auto
        if quarter == "auto":
            effective_quarter = self._latest_available_quarter()

        if "summary" in include:
            rows = provider.get_institute_hold(quarter=effective_quarter)
            summary = [adapt_institute_hold_summary_row(r) for r in rows]

        if "detail" in include and symbol:
            resolved = self.resolver.resolve(symbol, sec_type)
            code = resolved.symbol.split(".", 1)[0]
            rows = provider.get_institute_hold_detail(stock=code, quarter=effective_quarter)
            detail = [adapt_institute_hold_detail_row(r) for r in rows]

        # Sort summary
        if summary:
            key_map = {
                "institute_count": "institute_count",
                "hold_ratio": "hold_ratio",
                "hold_ratio_change": "hold_ratio_change",
                "float_ratio": "float_ratio",
                "float_ratio_change": "float_ratio_change",
            }
            sort_key = key_map.get(sort_by, "institute_count")
            summary = self._sort_items(summary, sort_key, descending)
            if top_n:
                summary = summary[:top_n]

        # Sort detail
        if detail:
            detail_key_map = {
                "hold_ratio": "hold_ratio",
                "hold_ratio_change": "hold_ratio_change",
                "float_ratio": "float_ratio",
                "float_ratio_change": "float_ratio_change",
            }
            d_key = detail_key_map.get(sort_by, "hold_ratio")
            detail = self._sort_items(detail, d_key, descending)
            if top_n:
                detail = detail[:top_n]

        summary_text = build_institute_hold_summary_text(summary, detail, effective_quarter)

        result = InstituteHoldResult(
            summary=summary,
            summary_count=len(summary),
            detail=detail,
            detail_count=len(detail),
            quarter=quarter,
            effective_quarter=effective_quarter,
            summary_text=summary_text,
        )
        return result.model_dump()

    @staticmethod
    def _latest_available_quarter() -> str:
        """Return the most recent quarter code that likely has data.

        Institution holdings are disclosed with ~1-2 month delay after
        quarter end. Returns the previous quarter as the best guess.
        """
        from datetime import date

        today = date.today()
        year = today.year
        month = today.month
        # Current quarter
        current_q = (month - 1) // 3 + 1
        # Data is usually 1 quarter behind
        q = current_q - 1
        y = year
        if q <= 0:
            q += 4
            y -= 1
        return f"{y}{q}"

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        def _get_val(item):
            v = getattr(item, key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v
        return sorted(items, key=_get_val, reverse=descending)

from __future__ import annotations

from datetime import date as dt_date

from openclaw_stock_mcp.app.models.margin_trading import MarginTradingResult
from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_margin_trading_adapters import (
    adapt_margin_sse_detail_row,
    adapt_margin_sse_summary_row,
    adapt_margin_szse_detail_row,
    adapt_margin_szse_summary_row,
    build_margin_summary_text,
)


class MarginTradingUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = request.include
        trade_date = request.trade_date
        start_date = getattr(request, "start_date", None)
        end_date = getattr(request, "end_date", None)
        exchange = request.exchange
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        # Normalize date for AKShare APIs (need YYYYMMDD format)
        raw_date = trade_date.replace("-", "") if trade_date else dt_date.today().strftime("%Y%m%d")
        raw_start = start_date.replace("-", "") if start_date else raw_date
        raw_end = end_date.replace("-", "") if end_date else raw_date

        summary = []
        detail = []
        errors = []

        if "summary" in include:
            if exchange in ("SSE", "both"):
                try:
                    rows = provider.get_margin_sse_summary(start_date=raw_start, end_date=raw_end)
                    summary.extend(adapt_margin_sse_summary_row(r) for r in rows)
                except Exception as exc:
                    errors.append({"exchange": "SSE", "section": "summary", **serialize_exception(exc)})
            if exchange in ("SZSE", "both"):
                try:
                    rows = provider.get_margin_szse_summary(date=raw_date)
                    summary.extend(adapt_margin_szse_summary_row(r) for r in rows)
                except Exception as exc:
                    errors.append({"exchange": "SZSE", "section": "summary", **serialize_exception(exc)})

        if "detail" in include:
            if exchange in ("SSE", "both"):
                try:
                    rows = provider.get_margin_sse_detail(date=raw_date)
                    detail.extend(adapt_margin_sse_detail_row(r) for r in rows)
                except Exception as exc:
                    errors.append({"exchange": "SSE", "section": "detail", **serialize_exception(exc)})
            if exchange in ("SZSE", "both"):
                try:
                    rows = provider.get_margin_szse_detail(date=raw_date)
                    detail.extend(adapt_margin_szse_detail_row(r) for r in rows)
                except Exception as exc:
                    errors.append({"exchange": "SZSE", "section": "detail", **serialize_exception(exc)})

            # Sort detail
            if detail:
                detail = self._sort_items(detail, sort_by, descending)
                if top_n:
                    detail = detail[:top_n]

        partial_failure = len(errors) > 0
        summary_text = build_margin_summary_text(summary, detail)

        result = MarginTradingResult(
            summary=summary,
            summary_count=len(summary),
            detail=detail,
            detail_count=len(detail),
            summary_text=summary_text,
        )
        payload = result.model_dump()
        payload["partial_failure"] = partial_failure
        payload["errors"] = errors
        return payload

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        key_map = {
            "financing_buy": "financing_buy",
            "financing_balance": "financing_balance",
            "securities_sell": "securities_sell",
            "securities_volume": "securities_volume",
        }
        attr = key_map.get(key, "financing_buy")

        def _get_val(item):
            v = getattr(item, attr, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

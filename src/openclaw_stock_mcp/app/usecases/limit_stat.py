from __future__ import annotations

from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.models.limit_stat import LimitStatSummary
from openclaw_stock_mcp.providers.adapters.akshare_limit_stat_adapters import (
    build_limit_stat_summary,
    build_limit_stat_summary_text,
)
from openclaw_stock_mcp.providers.errors import ProviderError


class LimitStatUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self._limit_down_error: dict | None = None

    def _resolve_effective_trade_date(self, requested_trade_date: str | None) -> tuple[str, dict]:
        from datetime import datetime

        calendar_provider = self.router.get_provider("akshare")
        resolved_requested_trade_date = requested_trade_date or datetime.now().strftime("%Y-%m-%d")
        calendar = calendar_provider.get_trading_calendar(
            market="CN",
            date=resolved_requested_trade_date,
            recent_limit=5,
        )
        is_trading_day = bool(calendar.get("is_trading_day"))
        effective_trade_date = resolved_requested_trade_date if is_trading_day else calendar.get("previous_trading_day")
        if not effective_trade_date:
            raise ProviderError(
                "INVALID_ARGUMENT",
                f"No effective trading day found for requested date: {resolved_requested_trade_date}",
                retryable=False,
            )
        return effective_trade_date, {
            "requested_trade_date": resolved_requested_trade_date,
            "effective_trade_date": effective_trade_date,
            "requested_is_trading_day": is_trading_day,
            "adjusted_to_previous_trading_day": effective_trade_date != resolved_requested_trade_date,
            "previous_trading_day": calendar.get("previous_trading_day"),
            "next_trading_day": calendar.get("next_trading_day"),
            "source": calendar.get("source"),
        }

    def _get_limit_down_count(self, trade_date: str) -> int:
        """Get limit-down count from zhitu market_pool."""
        try:
            provider = self.router.get_provider("zhitu")
            items = provider.get_market_pool(pool_type="limit_down", trade_date=trade_date)
            self._limit_down_error = None
            return len(items)
        except Exception as exc:
            self._limit_down_error = {
                "section": "limit_down",
                "error_code": getattr(exc, "code", "PROVIDER_UNAVAILABLE"),
                "message": str(exc),
                "retryable": getattr(exc, "retryable", True),
                "provider": "zhitu",
            }
            return 0

    def execute(self, request) -> dict:
        effective_trade_date, calendar_meta = self._resolve_effective_trade_date(
            getattr(request, "trade_date", None)
        )

        include = getattr(request, "include", ["summary", "limit_up", "broken_limit", "previous_day"])
        provider = self.router.get_provider("akshare")

        limit_up_items = []
        broken_limit_items = []
        previous_limit_items = []
        limit_down_count = 0

        if "limit_up" in include or "summary" in include:
            limit_up_items = provider.get_limit_up_pool(effective_trade_date)

        if "broken_limit" in include or "summary" in include:
            broken_limit_items = provider.get_broken_limit_pool(effective_trade_date)

        if "previous_day" in include:
            previous_limit_items = provider.get_previous_day_limit_pool(effective_trade_date)

        if "limit_down" in include or "summary" in include:
            limit_down_count = self._get_limit_down_count(effective_trade_date)

        errors = []
        if self._limit_down_error is not None:
            errors.append(self._limit_down_error)

        summary = build_limit_stat_summary(
            trade_date=effective_trade_date,
            limit_up_items=limit_up_items,
            broken_limit_items=broken_limit_items,
            previous_limit_items=previous_limit_items,
            limit_down_count=limit_down_count,
        )

        summary_text = build_limit_stat_summary_text(summary)

        result: dict = {
            "trade_date": effective_trade_date,
            "requested_trade_date": calendar_meta["requested_trade_date"],
            "summary_text": summary_text,
            "calendar": calendar_meta,
            "source": "akshare+ zhitu(limit_down)",
        }

        if "summary" in include:
            result["stat"] = summary

        if "limit_up" in include:
            # Apply filters
            min_boards = getattr(request, "min_consecutive_boards", None)
            if min_boards:
                limit_up_items = [it for it in limit_up_items if (it.consecutive_boards or 1) >= min_boards]
            top_n = getattr(request, "top_n", None)
            if top_n:
                limit_up_items = limit_up_items[:top_n]
            result["limit_up_items"] = limit_up_items
            result["limit_up_count"] = len(limit_up_items)

        if "broken_limit" in include:
            result["broken_limit_items"] = broken_limit_items
            result["broken_limit_count"] = len(broken_limit_items)

        if "previous_day" in include:
            result["previous_day_items"] = previous_limit_items
            result["previous_day_count"] = len(previous_limit_items)

        if "limit_down" in include:
            result["limit_down_count"] = limit_down_count

        result["partial_failure"] = len(errors) > 0
        result["errors"] = errors

        return result

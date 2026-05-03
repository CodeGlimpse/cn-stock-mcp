from __future__ import annotations

from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.providers.errors import ProviderError


class StockReviewUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request):
        resolved = self.resolver.resolve(request.symbol, "stock")
        if request.start_date and request.end_date:
            return self._execute_range_review(resolved.symbol, request)
        return self._execute_trade_date_review(resolved.symbol, request)

    def _execute_trade_date_review(self, symbol: str, request):
        calendar_provider = self.router.get_provider("akshare")
        calendar = calendar_provider.get_trading_calendar(market="CN", date=request.trade_date, recent_limit=20)
        requested_trade_date = request.trade_date
        effective_trade_date = requested_trade_date if calendar.get("is_trading_day") else calendar.get("previous_trading_day")
        if not effective_trade_date:
            raise ProviderError("INVALID_ARGUMENT", f"No effective trading day for {requested_trade_date}", retryable=False)

        daily, daily_meta = self._fetch_history(symbol, "1d", end_date=effective_trade_date, limit=20, adjust=request.adjust)
        weekly, weekly_meta = self._fetch_history(symbol, "1w", end_date=effective_trade_date, limit=8, adjust=request.adjust)
        monthly, monthly_meta = self._fetch_history(symbol, "1M", end_date=effective_trade_date, limit=6, adjust=request.adjust)

        latest = daily[-1] if daily else None
        if latest is None:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"No daily history returned for {symbol}", retryable=True)

        latest_close = latest.close
        daily_change = None
        daily_change_percent = None
        if latest.close is not None and latest.prev_close not in (None, 0):
            daily_change = latest.close - latest.prev_close
            daily_change_percent = (daily_change / latest.prev_close) * 100

        stats = {
            "return_5d": self._window_return(daily, 5),
            "return_20d": self._window_return(daily, 20),
            "range_20d_high": self._max_field(daily[-20:], "high"),
            "range_20d_low": self._min_field(daily[-20:], "low"),
            "weekly_return_4w": self._window_return(weekly, 4),
            "monthly_return_3m": self._window_return(monthly, 3),
        }

        summary = self._build_trade_date_summary(
            symbol=symbol,
            requested_trade_date=requested_trade_date,
            effective_trade_date=effective_trade_date,
            latest_close=latest_close,
            daily_change_percent=daily_change_percent,
            stats=stats,
            adjusted=(effective_trade_date != requested_trade_date),
        )

        return {
            "symbol": symbol,
            "mode": "trade_date_review",
            "trade_date": effective_trade_date,
            "requested_trade_date": requested_trade_date,
            "latest_bar": latest,
            "daily_change": daily_change,
            "daily_change_percent": daily_change_percent,
            "stats": stats,
            "windows": {
                "daily": daily,
                "weekly": weekly,
                "monthly": monthly,
            },
            "summary": summary,
            "source": daily_meta["final_provider"],
            "meta": {
                "calendar": {
                    "requested_trade_date": requested_trade_date,
                    "effective_trade_date": effective_trade_date,
                    "requested_is_trading_day": bool(calendar.get("is_trading_day")),
                    "adjusted_to_previous_trading_day": effective_trade_date != requested_trade_date,
                    "previous_trading_day": calendar.get("previous_trading_day"),
                    "next_trading_day": calendar.get("next_trading_day"),
                },
                "history": {
                    "daily": daily_meta,
                    "weekly": weekly_meta,
                    "monthly": monthly_meta,
                },
            },
        }

    def _execute_range_review(self, symbol: str, request):
        calendar_provider = self.router.get_provider("akshare")
        start_calendar = calendar_provider.get_trading_calendar(market="CN", date=request.start_date, recent_limit=5)
        end_calendar = calendar_provider.get_trading_calendar(market="CN", date=request.end_date, recent_limit=5)

        effective_start = request.start_date if start_calendar.get("is_trading_day") else start_calendar.get("next_trading_day")
        effective_end = request.end_date if end_calendar.get("is_trading_day") else end_calendar.get("previous_trading_day")
        if not effective_start or not effective_end or effective_start > effective_end:
            raise ProviderError("INVALID_ARGUMENT", "No effective trading range after calendar adjustment", retryable=False)

        daily, daily_meta = self._fetch_history(symbol, "1d", start_date=effective_start, end_date=effective_end, limit=1000, adjust=request.adjust)
        weekly, weekly_meta = self._fetch_history(symbol, "1w", start_date=effective_start, end_date=effective_end, limit=200, adjust=request.adjust)
        monthly, monthly_meta = self._fetch_history(symbol, "1M", start_date=effective_start, end_date=effective_end, limit=120, adjust=request.adjust)

        if not daily:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"No daily history returned for {symbol}", retryable=True)

        base = self._period_base(daily[0])
        latest = daily[-1]
        total_return = None
        if base not in (None, 0) and latest.close is not None:
            total_return = ((latest.close - base) / base) * 100

        stats = {
            "bars": len(daily),
            "period_return": total_return,
            "period_high": self._max_field(daily, "high"),
            "period_low": self._min_field(daily, "low"),
            "avg_turnover": self._avg_field(daily, "turnover"),
            "avg_volume": self._avg_field(daily, "volume"),
            "weekly_return": self._window_return(weekly, len(weekly)),
            "monthly_return": self._window_return(monthly, len(monthly)),
        }

        summary = self._build_range_summary(
            symbol=symbol,
            requested_start=request.start_date,
            requested_end=request.end_date,
            effective_start=effective_start,
            effective_end=effective_end,
            stats=stats,
            adjusted=(effective_start != request.start_date or effective_end != request.end_date),
        )

        return {
            "symbol": symbol,
            "mode": "range_review",
            "start_date": effective_start,
            "end_date": effective_end,
            "requested_start_date": request.start_date,
            "requested_end_date": request.end_date,
            "latest_bar": latest,
            "stats": stats,
            "windows": {
                "daily": daily,
                "weekly": weekly,
                "monthly": monthly,
            },
            "summary": summary,
            "source": daily_meta["final_provider"],
            "meta": {
                "calendar": {
                    "requested_start_date": request.start_date,
                    "requested_end_date": request.end_date,
                    "effective_start_date": effective_start,
                    "effective_end_date": effective_end,
                    "adjusted_range": effective_start != request.start_date or effective_end != request.end_date,
                },
                "history": {
                    "daily": daily_meta,
                    "weekly": weekly_meta,
                    "monthly": monthly_meta,
                },
            },
        }

    def _fetch_history(self, symbol: str, interval: str, start_date=None, end_date=None, limit=None, adjust="none"):
        selection = self.router.choose_provider(
            tool_name="stock_history",
            symbol=symbol,
            sec_type="stock",
            preferred="akshare",
        )
        items, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_history(
                symbol=symbol,
                sec_type="stock",
                interval=interval,
                start=start_date,
                end=end_date,
                limit=limit,
                adjust=adjust,
            ),
        )
        return items, {
            "selected_primary": fallback_meta.selected_primary,
            "selected_fallback": fallback_meta.selected_fallback,
            "attempted": fallback_meta.attempted,
            "final_provider": fallback_meta.final_provider or selection.primary,
            "used_fallback": fallback_meta.used_fallback,
            "interval": interval,
        }

    def _period_base(self, bar):
        return bar.prev_close if bar.prev_close is not None else (bar.open if bar.open is not None else bar.close)

    def _window_return(self, bars, window: int | None):
        if not bars:
            return None
        subset = bars if not window or len(bars) <= window else bars[-window:]
        if not subset:
            return None
        base = self._period_base(subset[0])
        last_close = subset[-1].close
        if base in (None, 0) or last_close is None:
            return None
        return ((last_close - base) / base) * 100

    def _max_field(self, bars, field: str):
        vals = [getattr(b, field, None) for b in bars if getattr(b, field, None) is not None]
        return max(vals) if vals else None

    def _min_field(self, bars, field: str):
        vals = [getattr(b, field, None) for b in bars if getattr(b, field, None) is not None]
        return min(vals) if vals else None

    def _avg_field(self, bars, field: str):
        vals = [getattr(b, field, None) for b in bars if getattr(b, field, None) is not None]
        return (sum(vals) / len(vals)) if vals else None

    def _fmt_pct(self, value):
        return "未知" if value is None else f"{value:.2f}%"

    def _fmt_num(self, value):
        return "未知" if value is None else f"{value:.2f}"

    def _build_trade_date_summary(self, symbol: str, requested_trade_date: str, effective_trade_date: str, latest_close, daily_change_percent, stats: dict, adjusted: bool):
        prefix = f"{requested_trade_date}（按 {effective_trade_date} 复盘）" if adjusted else f"{effective_trade_date} 个股复盘"
        return (
            f"{prefix}：{symbol} 收于 {self._fmt_num(latest_close)}，日涨跌 {self._fmt_pct(daily_change_percent)}；"
            f"近5日 {self._fmt_pct(stats.get('return_5d'))}，近20日 {self._fmt_pct(stats.get('return_20d'))}，"
            f"4周 {self._fmt_pct(stats.get('weekly_return_4w'))}，3月 {self._fmt_pct(stats.get('monthly_return_3m'))}。"
        )

    def _build_range_summary(self, symbol: str, requested_start: str, requested_end: str, effective_start: str, effective_end: str, stats: dict, adjusted: bool):
        if adjusted:
            prefix = f"{requested_start}~{requested_end}（按 {effective_start}~{effective_end} 复盘）"
        else:
            prefix = f"{effective_start}~{effective_end} 区间复盘"
        return (
            f"{prefix}：{symbol} 区间涨跌 {self._fmt_pct(stats.get('period_return'))}，"
            f"区间高/低 {self._fmt_num(stats.get('period_high'))}/{self._fmt_num(stats.get('period_low'))}，"
            f"日均成交额 {self._fmt_num(stats.get('avg_turnover'))}。"
        )

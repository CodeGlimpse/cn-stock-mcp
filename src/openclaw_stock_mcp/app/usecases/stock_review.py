from __future__ import annotations

from statistics import pstdev

from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.metric_schema import REVIEW_METRIC_SCHEMA, REVIEW_WINDOWS
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
            return self._execute_range_review(resolved, request)
        return self._execute_trade_date_review(resolved, request)

    def _execute_trade_date_review(self, resolved, request):
        calendar_provider = self.router.get_provider("akshare")
        calendar = calendar_provider.get_trading_calendar(market="CN", date=request.trade_date, recent_limit=20)
        requested_trade_date = request.trade_date
        effective_trade_date = requested_trade_date if calendar.get("is_trading_day") else calendar.get("previous_trading_day")
        if not effective_trade_date:
            raise ProviderError("INVALID_ARGUMENT", f"No effective trading day for {requested_trade_date}", retryable=False)

        daily, daily_meta = self._fetch_history(resolved.symbol, "1d", end_date=effective_trade_date, limit=20, adjust=request.adjust)
        weekly, weekly_meta = self._fetch_history(resolved.symbol, "1w", end_date=effective_trade_date, limit=8, adjust=request.adjust)
        monthly, monthly_meta = self._fetch_history(resolved.symbol, "1M", end_date=effective_trade_date, limit=6, adjust=request.adjust)

        latest = daily[-1] if daily else None
        if latest is None:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"No daily history returned for {resolved.symbol}", retryable=True)

        latest_close = latest.close
        daily_change = None
        daily_change_percent = None
        if latest.close is not None and latest.prev_close not in (None, 0):
            daily_change = latest.close - latest.prev_close
            daily_change_percent = (daily_change / latest.prev_close) * 100

        streaks = self._streaks(daily)
        stats = {
            "return_pct_5d": self._window_return(daily, 5),
            "return_pct": self._window_return(daily, 20),
            "high": self._max_field(daily[-20:], "high"),
            "low": self._min_field(daily[-20:], "low"),
            "return_pct_4w": self._window_return(weekly, 4),
            "return_pct_3m": self._window_return(monthly, 3),
            "volatility_pct": self._volatility(daily[-20:]),
            "max_drawdown_pct": self._max_drawdown(daily[-20:]),
            "up_streak": streaks["up_streak"],
            "down_streak": streaks["down_streak"],
            "volume_ratio": self._ratio_to_prev_avg(daily, "volume", 5),
            "turnover_ratio": self._ratio_to_prev_avg(daily, "turnover", 5),
            "distance_to_high_pct": self._distance_to_level(latest.close, self._max_field(daily[-20:], "high")),
            "distance_to_low_pct": self._distance_to_level(latest.close, self._min_field(daily[-20:], "low")),
        }

        benchmark = self._build_benchmark_context(
            resolved,
            start_date=daily[0].time if daily else effective_trade_date,
            end_date=effective_trade_date,
            adjust=request.adjust,
            range_mode=False,
        )
        stats["relative_strength_pct"] = self._relative_strength(stats.get("return_pct"), benchmark.get("return_pct"))

        summary = self._build_trade_date_summary(
            symbol=resolved.symbol,
            requested_trade_date=requested_trade_date,
            effective_trade_date=effective_trade_date,
            latest_close=latest_close,
            daily_change_percent=daily_change_percent,
            stats=stats,
            benchmark=benchmark,
            adjusted=(effective_trade_date != requested_trade_date),
        )

        return {
            "symbol": resolved.symbol,
            "mode": "trade_date_review",
            "trade_date": effective_trade_date,
            "requested_trade_date": requested_trade_date,
            "latest_bar": latest,
            "daily_change": daily_change,
            "daily_change_percent": daily_change_percent,
            "stats": stats,
            "benchmark": benchmark,
            "windows": {
                "daily": daily,
                "weekly": weekly,
                "monthly": monthly,
            },
            "summary": summary,
            "source": daily_meta["final_provider"],
            "meta": {
                "metric_schema": REVIEW_METRIC_SCHEMA,
                "metric_windows": REVIEW_WINDOWS.get("trade_date", {}),
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

    def _execute_range_review(self, resolved, request):
        calendar_provider = self.router.get_provider("akshare")
        start_calendar = calendar_provider.get_trading_calendar(market="CN", date=request.start_date, recent_limit=5)
        end_calendar = calendar_provider.get_trading_calendar(market="CN", date=request.end_date, recent_limit=5)

        effective_start = request.start_date if start_calendar.get("is_trading_day") else start_calendar.get("next_trading_day")
        effective_end = request.end_date if end_calendar.get("is_trading_day") else end_calendar.get("previous_trading_day")
        if not effective_start or not effective_end or effective_start > effective_end:
            raise ProviderError("INVALID_ARGUMENT", "No effective trading range after calendar adjustment", retryable=False)

        daily, daily_meta = self._fetch_history(resolved.symbol, "1d", start_date=effective_start, end_date=effective_end, limit=1000, adjust=request.adjust)
        weekly, weekly_meta = self._fetch_history(resolved.symbol, "1w", start_date=effective_start, end_date=effective_end, limit=200, adjust=request.adjust)
        monthly, monthly_meta = self._fetch_history(resolved.symbol, "1M", start_date=effective_start, end_date=effective_end, limit=120, adjust=request.adjust)

        if not daily:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"No daily history returned for {resolved.symbol}", retryable=True)

        base = self._period_base(daily[0])
        latest = daily[-1]
        total_return = None
        if base not in (None, 0) and latest.close is not None:
            total_return = ((latest.close - base) / base) * 100

        streaks = self._streaks(daily)
        stats = {
            "bars": len(daily),
            "return_pct": total_return,
            "high": self._max_field(daily, "high"),
            "low": self._min_field(daily, "low"),
            "avg_turnover": self._avg_field(daily, "turnover"),
            "avg_volume": self._avg_field(daily, "volume"),
            "return_pct_weekly": self._window_return(weekly, len(weekly)),
            "return_pct_monthly": self._window_return(monthly, len(monthly)),
            "volatility_pct": self._volatility(daily),
            "max_drawdown_pct": self._max_drawdown(daily),
            "up_streak": streaks["up_streak"],
            "down_streak": streaks["down_streak"],
            "volume_ratio": self._ratio_to_prev_avg(daily, "volume", 5),
            "turnover_ratio": self._ratio_to_prev_avg(daily, "turnover", 5),
        }

        benchmark = self._build_benchmark_context(
            resolved,
            start_date=effective_start,
            end_date=effective_end,
            adjust=request.adjust,
            range_mode=True,
        )
        stats["relative_strength_pct"] = self._relative_strength(stats.get("return_pct"), benchmark.get("return_pct"))

        summary = self._build_range_summary(
            symbol=resolved.symbol,
            requested_start=request.start_date,
            requested_end=request.end_date,
            effective_start=effective_start,
            effective_end=effective_end,
            stats=stats,
            benchmark=benchmark,
            adjusted=(effective_start != request.start_date or effective_end != request.end_date),
        )

        return {
            "symbol": resolved.symbol,
            "mode": "range_review",
            "start_date": effective_start,
            "end_date": effective_end,
            "requested_start_date": request.start_date,
            "requested_end_date": request.end_date,
            "latest_bar": latest,
            "stats": stats,
            "benchmark": benchmark,
            "windows": {
                "daily": daily,
                "weekly": weekly,
                "monthly": monthly,
            },
            "summary": summary,
            "source": daily_meta["final_provider"],
            "meta": {
                "metric_schema": REVIEW_METRIC_SCHEMA,
                "metric_windows": REVIEW_WINDOWS.get("range_review", {}),
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
            sec_type="stock" if interval in {"1d", "1w", "1M"} else "stock",
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

    def _fetch_index_history(self, symbol: str, start_date: str, end_date: str):
        selection = self.router.choose_provider(
            tool_name="stock_history",
            symbol=symbol,
            sec_type="index",
            preferred=None,
        )
        items, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_history(
                symbol=symbol,
                sec_type="index",
                interval="1d",
                start=start_date,
                end=end_date,
                limit=1000,
                adjust="none",
            ),
        )
        return items, {
            "selected_primary": fallback_meta.selected_primary,
            "selected_fallback": fallback_meta.selected_fallback,
            "attempted": fallback_meta.attempted,
            "final_provider": fallback_meta.final_provider or selection.primary,
            "used_fallback": fallback_meta.used_fallback,
            "interval": "1d",
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

    def _volatility(self, bars):
        returns = []
        for bar in bars:
            if bar.close is not None and bar.prev_close not in (None, 0):
                returns.append(((bar.close - bar.prev_close) / bar.prev_close) * 100)
        if len(returns) < 2:
            return None
        return pstdev(returns)

    def _max_drawdown(self, bars):
        closes = [bar.close for bar in bars if bar.close is not None]
        if len(closes) < 2:
            return None
        peak = closes[0]
        max_dd = 0.0
        for close in closes:
            if close > peak:
                peak = close
            if peak not in (None, 0):
                drawdown = ((peak - close) / peak) * 100
                if drawdown > max_dd:
                    max_dd = drawdown
        return max_dd

    def _streaks(self, bars):
        up = 0
        down = 0
        for bar in reversed(bars):
            if bar.close is None or bar.prev_close in (None, 0):
                break
            if bar.close > bar.prev_close:
                if down > 0:
                    break
                up += 1
            elif bar.close < bar.prev_close:
                if up > 0:
                    break
                down += 1
            else:
                break
        return {"up_streak": up, "down_streak": down}

    def _ratio_to_prev_avg(self, bars, field: str, lookback: int = 5):
        if len(bars) < lookback + 1:
            return None
        latest = getattr(bars[-1], field, None)
        prev_vals = [getattr(bar, field, None) for bar in bars[-(lookback + 1):-1] if getattr(bar, field, None) is not None]
        if latest is None or not prev_vals:
            return None
        avg = sum(prev_vals) / len(prev_vals)
        if avg == 0:
            return None
        return latest / avg

    def _distance_to_level(self, latest_close, level):
        if latest_close is None or level in (None, 0):
            return None
        return ((latest_close - level) / level) * 100

    def _benchmark_for(self, resolved):
        if resolved.exchange == "BJ":
            return {"symbol": "899050.BJ", "name": "北证50"}
        if resolved.board == "chinext":
            return {"symbol": "399006.SZ", "name": "创业板指"}
        if resolved.exchange == "SZ":
            return {"symbol": "399001.SZ", "name": "深证成指"}
        return {"symbol": "000001.SH", "name": "上证指数"}

    def _build_benchmark_context(self, resolved, start_date: str, end_date: str, adjust: str, range_mode: bool):
        benchmark_ref = self._benchmark_for(resolved)
        try:
            bars, meta = self._fetch_index_history(benchmark_ref["symbol"], start_date=start_date, end_date=end_date)
            bench_return = self._window_return(bars, len(bars))
            return {
                "symbol": benchmark_ref["symbol"],
                "name": benchmark_ref["name"],
                "return_pct": bench_return,
                "latest_bar": bars[-1] if bars else None,
                "source": meta["final_provider"],
                "meta": meta,
                "range_mode": range_mode,
            }
        except Exception as exc:
            return {
                "symbol": benchmark_ref["symbol"],
                "name": benchmark_ref["name"],
                "return_pct": None,
                "latest_bar": None,
                "source": None,
                "meta": {"error": str(exc)},
                "range_mode": range_mode,
            }

    def _relative_strength(self, stock_return, benchmark_return):
        if stock_return is None or benchmark_return is None:
            return None
        return stock_return - benchmark_return

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

    def _fmt_ratio(self, value):
        return "未知" if value is None else f"{value:.2f}x"

    def _build_trade_date_summary(self, symbol: str, requested_trade_date: str, effective_trade_date: str, latest_close, daily_change_percent, stats: dict, benchmark: dict, adjusted: bool):
        prefix = f"{requested_trade_date}（按 {effective_trade_date} 复盘）" if adjusted else f"{effective_trade_date} 个股复盘"
        benchmark_part = ""
        if benchmark.get("return_pct") is not None:
            benchmark_part = f"；相对{benchmark.get('name')} 强弱 {self._fmt_pct(stats.get('relative_strength_pct'))}"
        return (
            f"{prefix}：{symbol} 收于 {self._fmt_num(latest_close)}，日涨跌 {self._fmt_pct(daily_change_percent)}；"
            f"近5日 {self._fmt_pct(stats.get('return_pct_5d'))}，主窗口收益 {self._fmt_pct(stats.get('return_pct'))}，"
            f"4周 {self._fmt_pct(stats.get('return_pct_4w'))}，3月 {self._fmt_pct(stats.get('return_pct_3m'))}；"
            f"波动 {self._fmt_pct(stats.get('volatility_pct'))}，最大回撤 {self._fmt_pct(stats.get('max_drawdown_pct'))}，"
            f"量比(5日) {self._fmt_ratio(stats.get('volume_ratio'))}{benchmark_part}。"
        )

    def _build_range_summary(self, symbol: str, requested_start: str, requested_end: str, effective_start: str, effective_end: str, stats: dict, benchmark: dict, adjusted: bool):
        if adjusted:
            prefix = f"{requested_start}~{requested_end}（按 {effective_start}~{effective_end} 复盘）"
        else:
            prefix = f"{effective_start}~{effective_end} 区间复盘"
        benchmark_part = ""
        if benchmark.get("return_pct") is not None:
            benchmark_part = f"；相对{benchmark.get('name')} 强弱 {self._fmt_pct(stats.get('relative_strength_pct'))}"
        return (
            f"{prefix}：{symbol} 区间涨跌 {self._fmt_pct(stats.get('return_pct'))}，"
            f"区间高/低 {self._fmt_num(stats.get('high'))}/{self._fmt_num(stats.get('low'))}，"
            f"区间波动 {self._fmt_pct(stats.get('volatility_pct'))}，最大回撤 {self._fmt_pct(stats.get('max_drawdown_pct'))}，"
            f"日均成交额 {self._fmt_num(stats.get('avg_turnover'))}{benchmark_part}。"
        )

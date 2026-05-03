from __future__ import annotations

from bisect import bisect_left, bisect_right
from datetime import date, datetime

from openclaw_stock_mcp.providers.errors import ProviderError

try:
    import akshare as ak
except Exception:  # pragma: no cover
    ak = None

from openclaw_stock_mcp.app.models.bar import Bar
from openclaw_stock_mcp.providers.adapters.akshare_adapters import (
    adapt_akshare_fund_list_row,
    adapt_akshare_index_list_row,
    adapt_akshare_stock_list_row,
)
from openclaw_stock_mcp.providers.adapters.akshare_market_adapters import adapt_akshare_tx_bar_row
from openclaw_stock_mcp.infra.time_utils import normalize_symbol


class AKShareProvider:
    name = "akshare"

    def __init__(self) -> None:
        self._trade_dates_cache: list[str] | None = None

    def _require_ak(self):
        if ak is None:
            raise ProviderError("PROVIDER_UNAVAILABLE", "akshare is not installed", retryable=False)
        return ak

    def _load_trade_dates(self) -> list[str]:
        if self._trade_dates_cache is not None:
            return self._trade_dates_cache
        lib = self._require_ak()
        try:
            df = lib.tool_trade_date_hist_sina()
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare trading calendar failed: {exc}", retryable=True) from exc
        self._trade_dates_cache = [str(v) for v in df["trade_date"].tolist()]
        return self._trade_dates_cache

    def _to_tx_symbol(self, normalized: str) -> str:
        code, exchange = normalized.split(".", 1)
        exchange_prefix = exchange.lower()
        return f"{exchange_prefix}{code}"

    def _date_key(self, value) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        text = str(value)
        if " " in text:
            text = text.split(" ", 1)[0]
        return text

    def _sum_or_none(self, values: list[float | None]) -> float | None:
        valid = [v for v in values if v is not None]
        return float(sum(valid)) if valid else None

    def _max_or_none(self, values: list[float | None]) -> float | None:
        valid = [v for v in values if v is not None]
        return max(valid) if valid else None

    def _min_or_none(self, values: list[float | None]) -> float | None:
        valid = [v for v in values if v is not None]
        return min(valid) if valid else None

    def _aggregate_bars(self, bars: list[Bar], interval: str) -> list[Bar]:
        if interval not in {"1w", "1M"}:
            raise ProviderError("UNSUPPORTED_INTERVAL", f"Unsupported stock interval: {interval}", retryable=False)
        if not bars:
            return []

        groups: list[list[Bar]] = []
        current_group: list[Bar] = []
        current_key = None

        for bar in bars:
            d = date.fromisoformat(str(bar.time)[:10])
            key = (d.isocalendar().year, d.isocalendar().week) if interval == "1w" else (d.year, d.month)
            if current_key is None or key == current_key:
                current_group.append(bar)
                current_key = key
                continue
            groups.append(current_group)
            current_group = [bar]
            current_key = key

        if current_group:
            groups.append(current_group)

        aggregated: list[Bar] = []
        for group in groups:
            first = group[0]
            last = group[-1]
            aggregated.append(
                Bar(
                    time=last.time,
                    open=first.open,
                    high=self._max_or_none([b.high for b in group]),
                    low=self._min_or_none([b.low for b in group]),
                    close=last.close,
                    volume=self._sum_or_none([b.volume for b in group]),
                    turnover=self._sum_or_none([b.turnover for b in group]),
                    prev_close=first.prev_close,
                )
            )

        prev_close = None
        for bar in aggregated:
            if prev_close is not None:
                bar.prev_close = prev_close
            prev_close = bar.close if bar.close is not None else prev_close

        return aggregated

    def search_instruments(self, query: str, sec_types=None, market: str | None = None, limit: int = 10):
        lib = self._require_ak()
        sec_types = sec_types or ["stock", "index", "fund"]
        items = []

        if "stock" in sec_types:
            try:
                df = lib.stock_info_a_code_name()
                for row in df.to_dict(orient="records"):
                    item = adapt_akshare_stock_list_row(row)
                    if query in item.symbol or (item.name and query in item.name):
                        items.append(item)
            except Exception:
                pass

        if "index" in sec_types:
            try:
                if hasattr(lib, "index_stock_info"):
                    df = lib.index_stock_info()
                    for row in df.to_dict(orient="records"):
                        item = adapt_akshare_index_list_row(row)
                        if query in item.symbol or (item.name and query in item.name):
                            items.append(item)
            except Exception:
                pass

        if "fund" in sec_types:
            try:
                df = lib.fund_name_em()
                for row in df.to_dict(orient="records"):
                    item = adapt_akshare_fund_list_row(row)
                    if query in item.symbol or (item.name and query in item.name):
                        items.append(item)
            except Exception:
                pass

        return items[:limit]

    def get_quote(self, symbol: str, sec_type: str):
        raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare quote not implemented in minimal version", retryable=False)

    def get_quotes(self, symbols: list[str], sec_type: str | None = None):
        return [self.get_quote(symbol, sec_type or "stock") for symbol in symbols]

    def get_history(self, symbol: str, sec_type: str, interval: str, start=None, end=None, limit=None, adjust=None):
        lib = self._require_ak()
        if sec_type != "stock":
            raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare history minimal version supports stock only", retryable=False)
        if interval not in {"1d", "1w", "1M"}:
            raise ProviderError("UNSUPPORTED_INTERVAL", "AKShare review mode currently supports 1d/1w/1M only", retryable=False)

        normalized = normalize_symbol(symbol)
        tx_symbol = self._to_tx_symbol(normalized)
        adjust_map = {"none": "", "qfq": "qfq", "hfq": "hfq"}
        try:
            tx_df = lib.stock_zh_a_hist_tx(
                symbol=tx_symbol,
                start_date=(start or "19000101").replace("-", ""),
                end_date=(end or "20500101").replace("-", ""),
                adjust=adjust_map.get(adjust or "none", ""),
            )
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare TX history failed: {exc}", retryable=True) from exc

        tx_rows = tx_df.to_dict(orient="records")
        bars = [adapt_akshare_tx_bar_row(row) for row in tx_rows]

        # best-effort: fill/normalize volume+turnover from stock_zh_a_daily
        # turnover here is standardized to 成交额(amount)口径
        try:
            daily_df = lib.stock_zh_a_daily(
                symbol=tx_symbol,
                start_date=(start or "19000101").replace("-", ""),
                end_date=(end or "20500101").replace("-", ""),
                adjust=adjust_map.get(adjust or "none", ""),
            )
            daily_map = {}
            for row in daily_df.to_dict(orient="records"):
                key = self._date_key(row.get("date") or row.get("日期"))
                if key:
                    daily_map[key] = row
            for bar in bars:
                row = daily_map.get(bar.time)
                if not row:
                    continue
                if bar.volume is None:
                    try:
                        v = row.get("volume") or row.get("成交量")
                        bar.volume = float(v) if v is not None else None
                    except Exception:
                        pass
                # 统一 turnover 为成交额口径（daily.amount 优先）
                try:
                    amt = row.get("amount") or row.get("成交额")
                    if amt is not None:
                        bar.turnover = float(amt)
                except Exception:
                    pass
        except Exception:
            pass

        # derive prev_close from previous bar close when upstream doesn't provide it
        prev_close = None
        for bar in bars:
            if bar.prev_close is None:
                bar.prev_close = prev_close
            prev_close = bar.close if bar.close is not None else prev_close

        if interval == "1d":
            result = bars
        else:
            result = self._aggregate_bars(bars, interval)

        if limit:
            result = result[-limit:]
        return result

    def get_orderbook(self, symbol: str, sec_type: str):
        raise ProviderError("UNSUPPORTED_MARKET", "AKShare orderbook not implemented", retryable=False)

    def get_indicator(self, symbol: str, sec_type: str, interval: str, indicator: str, start=None, end=None, limit=None):
        raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare indicator not implemented", retryable=False)

    def get_market_overview(self, market: str = "CN"):
        return {"market": market, "indices": [], "source": "akshare"}

    def get_market_pool(self, pool_type: str, trade_date: str | None = None):
        raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare market pool not implemented", retryable=False)

    def get_trading_calendar(self, market: str = "CN", date: str | None = None, start_date: str | None = None, end_date: str | None = None, recent_limit: int = 5):
        if market != "CN":
            raise ProviderError("UNSUPPORTED_MARKET", f"Unsupported market: {market}", retryable=False)

        trade_dates = self._load_trade_dates()

        if start_date and end_date:
            left = bisect_left(trade_dates, start_date)
            right = bisect_right(trade_dates, end_date)
            items = trade_dates[left:right]
            return {
                "market": market,
                "start_date": start_date,
                "end_date": end_date,
                "items": items,
                "count": len(items),
                "source": self.name,
            }

        target = date or datetime.now().date().isoformat()
        idx_left = bisect_left(trade_dates, target)
        is_trading_day = idx_left < len(trade_dates) and trade_dates[idx_left] == target
        previous_trading_day = trade_dates[idx_left - 1] if idx_left > 0 else None
        if is_trading_day:
            next_idx = idx_left + 1
        else:
            next_idx = idx_left
        next_trading_day = trade_dates[next_idx] if next_idx < len(trade_dates) else None

        recent_trading_days = trade_dates[max(0, idx_left - recent_limit):idx_left] if not is_trading_day else trade_dates[max(0, idx_left - recent_limit + 1):idx_left + 1]

        return {
            "market": market,
            "date": target,
            "is_trading_day": is_trading_day,
            "previous_trading_day": previous_trading_day,
            "next_trading_day": next_trading_day,
            "recent_trading_days": recent_trading_days,
            "source": self.name,
        }

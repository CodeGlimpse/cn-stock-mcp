from __future__ import annotations

from bisect import bisect_left, bisect_right
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timedelta
from io import StringIO
from threading import Lock, local

import requests

from cn_stock_mcp.infra.time_utils import normalize_symbol
from cn_stock_mcp.infra.config import Settings, get_settings
from cn_stock_mcp.providers.errors import ProviderError

try:
    import akshare as ak
except Exception:  # pragma: no cover
    ak = None


from cn_stock_mcp.app.models.bar import Bar
from cn_stock_mcp.app.models.instrument import Instrument
from cn_stock_mcp.app.models.quote import Quote
from cn_stock_mcp.providers.adapters.akshare_adapters import (
    adapt_akshare_fund_list_row,
    adapt_akshare_index_list_row,
    adapt_akshare_stock_list_row,
)
from cn_stock_mcp.providers.adapters.akshare_market_adapters import adapt_akshare_bar_row, adapt_akshare_quote_row, adapt_akshare_tx_bar_row
from cn_stock_mcp.providers.adapters.akshare_capital_flow_adapters import (
    adapt_akshare_individual_fund_flow,
    adapt_akshare_market_fund_flow,
    adapt_akshare_sector_fund_flow,
    build_market_fund_flow_summary,
)
from cn_stock_mcp.providers.adapters.akshare_financial_adapters import (
    adapt_akshare_financial_detail_row,
    build_financial_history_from_abstract,
    build_financial_snapshot_from_abstract,
)
from cn_stock_mcp.providers.adapters.akshare_limit_stat_adapters import (
    adapt_em_broken_limit_item,
    adapt_em_limit_up_item,
    adapt_em_previous_limit_item,
)
from cn_stock_mcp.providers.adapters.akshare_northbound_adapters import (
    adapt_em_hist_row,
    build_daily_summary_from_flow_summary,
)
from cn_stock_mcp.app.models.capital_flow import CapitalFlowRecord, MarketFundFlowSummary, SectorFundFlowItem
from cn_stock_mcp.app.models.financial import FinancialDetailItem, FinancialSnapshot, FinancialHistoryPoint
from cn_stock_mcp.app.models.limit_stat import BrokenLimitItem, LimitUpItem, PreviousDayLimitItem
from cn_stock_mcp.app.models.northbound import NorthboundFlowRecord, NorthboundDailySummary
from cn_stock_mcp.infra.time_utils import normalize_symbol


_request_timeout_state = local()
_request_patch_lock = Lock()
_original_session_request = requests.sessions.Session.request


def _request_with_thread_timeout(session, method, url, *args, **kwargs):
    timeout = getattr(_request_timeout_state, "timeout", None)
    if timeout is not None and kwargs.get("timeout") is None:
        kwargs["timeout"] = timeout
    return _original_session_request(session, method, url, *args, **kwargs)


def _install_request_timeout_wrapper() -> None:
    global _original_session_request
    with _request_patch_lock:
        current = requests.sessions.Session.request
        if current is not _request_with_thread_timeout:
            _original_session_request = current
            requests.sessions.Session.request = _request_with_thread_timeout


class AKShareProvider:
    name = "akshare"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.akshare_timeout_seconds = max(int(self.settings.akshare_timeout_seconds or 20), 1)
        self._trade_dates_cache: list[str] | None = None
        self._bj_spot_cache: tuple[float, dict[str, dict]] | None = None  # (fetched_at, code->row)
        self._bj_spot_cache_ttl: int = 10  # seconds
        self._kc_spot_cache: tuple[float, dict[str, dict]] | None = None  # (fetched_at, code->row)
        self._kc_spot_cache_ttl: int = 10  # seconds

    def _require_ak(self):
        if ak is None:
            raise ProviderError("PROVIDER_UNAVAILABLE", "akshare is not installed", retryable=False)
        return ak

    def _call_ak_quietly(self, fn, *args, **kwargs):
        _install_request_timeout_wrapper()
        previous_timeout = getattr(_request_timeout_state, "timeout", None)
        _request_timeout_state.timeout = self.akshare_timeout_seconds
        sink = StringIO()
        try:
            with redirect_stdout(sink), redirect_stderr(sink):
                return fn(*args, **kwargs)
        finally:
            if previous_timeout is None:
                del _request_timeout_state.timeout
            else:
                _request_timeout_state.timeout = previous_timeout

    def _load_trade_dates(self) -> list[str]:
        if self._trade_dates_cache is not None:
            return self._trade_dates_cache
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.tool_trade_date_hist_sina)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare trading calendar failed: {exc}", retryable=True) from exc
        self._trade_dates_cache = [str(v) for v in df["trade_date"].tolist()]
        return self._trade_dates_cache

    def _to_tx_symbol(self, normalized: str) -> str:
        code, exchange = normalized.split(".", 1)
        exchange_prefix = exchange.lower()
        return f"{exchange_prefix}{code}"

    def _to_index_symbol(self, normalized: str) -> str:
        return normalized.split(".", 1)[0]

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

    def _fill_prev_close(self, bars: list[Bar]) -> list[Bar]:
        prev_close = None
        for bar in bars:
            if bar.prev_close is None:
                bar.prev_close = prev_close
            prev_close = bar.close if bar.close is not None else prev_close
        return bars

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

        return self._fill_prev_close(aggregated)

    def _matches_query(self, item: Instrument, query: str) -> bool:
        query_norm = (query or "").strip().lower()
        if not query_norm:
            return False
        symbol_text = (item.symbol or "").strip().lower()
        raw_symbol_text = (item.raw_symbol or "").strip().lower()
        name_text = (item.name or "").strip().lower()
        return (
            query_norm in symbol_text
            or query_norm in raw_symbol_text
            or query_norm in name_text
        )

    def _search_rank(self, item: Instrument, query: str) -> tuple:
        query_norm = (query or "").strip().lower()
        symbol_text = (item.symbol or "").strip().lower()
        raw_symbol_text = (item.raw_symbol or "").strip().lower()
        name_text = (item.name or "").strip().lower()

        exact_symbol = query_norm == symbol_text or query_norm == raw_symbol_text
        exact_name = query_norm == name_text
        symbol_prefix = symbol_text.startswith(query_norm) or raw_symbol_text.startswith(query_norm)
        name_prefix = name_text.startswith(query_norm)
        sec_type_priority = {"stock": 0, "index": 1, "fund": 2, "sector": 3}.get(item.sec_type, 9)
        return (
            0 if exact_symbol else 1,
            0 if exact_name else 1,
            0 if symbol_prefix else 1,
            0 if name_prefix else 1,
            sec_type_priority,
            len(name_text) if name_text else 9999,
            symbol_text,
        )

    def search_instruments(self, query: str, sec_types=None, market: str | None = None, limit: int = 10):
        lib = self._require_ak()
        sec_types = sec_types or ["stock", "index", "fund"]
        items: list[Instrument] = []
        seen: set[tuple[str, str]] = set()

        def add_item(item: Instrument):
            if not self._matches_query(item, query):
                return
            key = (item.sec_type, item.symbol)
            if key in seen:
                return
            seen.add(key)
            items.append(item)

        if "stock" in sec_types:
            try:
                df = self._call_ak_quietly(lib.stock_info_a_code_name)
                for row in df.to_dict(orient="records"):
                    add_item(adapt_akshare_stock_list_row(row))
            except Exception:
                pass

        if "index" in sec_types:
            try:
                if hasattr(lib, "index_stock_info"):
                    df = self._call_ak_quietly(lib.index_stock_info)
                    for row in df.to_dict(orient="records"):
                        add_item(adapt_akshare_index_list_row(row))
            except Exception:
                pass

        if "fund" in sec_types:
            try:
                df = self._call_ak_quietly(lib.fund_name_em)
                for row in df.to_dict(orient="records"):
                    add_item(adapt_akshare_fund_list_row(row))
            except Exception:
                pass

        items.sort(key=lambda item: self._search_rank(item, query))
        return items[:limit]

    def _get_bj_spot_map(self) -> dict[str, dict]:
        """Fetch full BJ spot table and return {code: row_dict}. Cached for _bj_spot_cache_ttl seconds."""
        import time as _time

        now = _time.time()
        if self._bj_spot_cache is not None and (now - self._bj_spot_cache[0]) < self._bj_spot_cache_ttl:
            return self._bj_spot_cache[1]

        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_bj_a_spot_em)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare BJ spot failed: {exc}", retryable=True) from exc

        code_map: dict[str, dict] = {}
        for _, row in df.iterrows():
            code = str(row.get("代码", "")).strip()
            if code:
                code_map[code] = row.to_dict()
        self._bj_spot_cache = (now, code_map)
        return code_map

    def _get_kc_spot_map(self) -> dict[str, dict]:
        """Fetch full A-share spot table via Sina and return {code: row_dict} for 688xxx stocks.

        Uses stock_zh_a_spot() (Sina source) which is more reliable than the
        Eastmoney source for KC stocks in proxy-restricted environments.
        Only 688-prefixed rows are kept to limit memory. Cached for _kc_spot_cache_ttl seconds.
        Missing fields (PE/PB/market_cap/turnover_rate/amplitude) will be None — acceptable for fallback.
        """
        import time as _time

        now = _time.time()
        if self._kc_spot_cache is not None and (now - self._kc_spot_cache[0]) < self._kc_spot_cache_ttl:
            return self._kc_spot_cache[1]

        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_zh_a_spot)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare KC spot (Sina) failed: {exc}", retryable=True) from exc

        code_map: dict[str, dict] = {}
        for _, row in df.iterrows():
            raw_code = str(row.get("代码", "")).strip()
            # Sina returns codes like "sh688001" — extract the 6-digit code
            code = raw_code.lstrip("sh").lstrip("sz")
            if code.startswith("688") and len(code) == 6:
                code_map[code] = row.to_dict()
        self._kc_spot_cache = (now, code_map)
        return code_map

    def get_quote(self, symbol: str, sec_type: str):
        normalized = normalize_symbol(symbol)
        code = normalized.split(".", 1)[0]

        if sec_type == "stock" and normalized.endswith(".BJ"):
            spot_map = self._get_bj_spot_map()
            row = spot_map.get(code)
            if row is None:
                raise ProviderError("UNSUPPORTED_MARKET", f"AKShare BJ quote: code {code} not found in spot data", retryable=False)
            return adapt_akshare_quote_row(row, normalized, sec_type)

        if sec_type == "stock" and code.startswith("688"):
            spot_map = self._get_kc_spot_map()
            row = spot_map.get(code)
            if row is None:
                raise ProviderError("UNSUPPORTED_MARKET", f"AKShare KC quote: code {code} not found in spot data", retryable=False)
            return adapt_akshare_quote_row(row, normalized, sec_type)

        raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare quote not implemented for this sec_type/market", retryable=False)

    def get_quotes(self, symbols: list[str], sec_type: str | None = None):
        resolved_sec_type = sec_type or "stock"

        # Fast path: all BJ stocks — one spot pull
        bj_symbols = []
        kc_symbols = []
        other_symbols = []
        for sym in symbols:
            normalized = normalize_symbol(sym)
            if resolved_sec_type == "stock" and normalized.endswith(".BJ"):
                bj_symbols.append(sym)
            elif resolved_sec_type == "stock" and normalized.split(".", 1)[0].startswith("688"):
                kc_symbols.append(sym)
            else:
                other_symbols.append(sym)

        results: dict[str, Quote] = {}

        if bj_symbols:
            spot_map = self._get_bj_spot_map()
            for sym in bj_symbols:
                normalized = normalize_symbol(sym)
                code = normalized.split(".", 1)[0]
                row = spot_map.get(code)
                if row is not None:
                    results[sym] = adapt_akshare_quote_row(row, normalized, resolved_sec_type)

        if kc_symbols:
            spot_map = self._get_kc_spot_map()
            for sym in kc_symbols:
                normalized = normalize_symbol(sym)
                code = normalized.split(".", 1)[0]
                row = spot_map.get(code)
                if row is not None:
                    results[sym] = adapt_akshare_quote_row(row, normalized, resolved_sec_type)

        # Non-BJ symbols still not supported for quote
        for sym in other_symbols:
            try:
                results[sym] = self.get_quote(sym, resolved_sec_type)
            except ProviderError:
                pass

        return [results.get(sym) for sym in symbols if results.get(sym) is not None]

    @staticmethod
    def _prepush_start(start: str | None, days: int = 10) -> str:
        """Push start_date back by *days* calendar days to ensure at least one
        earlier bar is fetched for prev_close derivation."""
        if not start:
            return "19000101"
        d = date.fromisoformat(start.replace("-", ""))
        earlier = d - timedelta(days=days)
        return earlier.strftime("%Y%m%d")

    @staticmethod
    def _trim_before(bars: list[Bar], original_start: str | None) -> list[Bar]:
        """Drop bars before *original_start* (used after pre-pushing for prev_close)."""
        if not original_start or not bars:
            return bars
        cutoff = original_start.replace("-", "")
        return [b for b in bars if str(b.time)[:10].replace("-", "") >= cutoff]

    def get_history(self, symbol: str, sec_type: str, interval: str, start=None, end=None, limit=None, adjust=None):
        lib = self._require_ak()

        original_start = start

        if sec_type == "index":
            if interval not in {"1d", "1w", "1M"}:
                raise ProviderError("UNSUPPORTED_INTERVAL", "AKShare index history currently supports 1d/1w/1M only", retryable=False)
            normalized = normalize_symbol(symbol)
            index_symbol = self._to_index_symbol(normalized)
            period_map = {"1d": "daily", "1w": "weekly", "1M": "monthly"}
            try:
                df = self._call_ak_quietly(
                    lib.index_zh_a_hist,
                    symbol=index_symbol,
                    period=period_map[interval],
                    start_date=self._prepush_start(start),
                    end_date=(end or "20500101").replace("-", ""),
                )
            except Exception as exc:
                raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare index history failed: {exc}", retryable=True) from exc
            rows = df.to_dict(orient="records")
            bars = [adapt_akshare_bar_row(row) for row in rows]
            bars = self._fill_prev_close(bars)
            bars = self._trim_before(bars, original_start)
            if limit:
                bars = bars[-limit:]
            return bars

        if sec_type != "stock":
            raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare history minimal version supports stock only", retryable=False)
        if interval not in {"1d", "1w", "1M"}:
            raise ProviderError("UNSUPPORTED_INTERVAL", "AKShare review mode currently supports 1d/1w/1M only", retryable=False)

        normalized = normalize_symbol(symbol)
        tx_symbol = self._to_tx_symbol(normalized)
        tx_start = self._prepush_start(start)
        adjust_map = {"none": "", "qfq": "qfq", "hfq": "hfq"}
        try:
            tx_df = self._call_ak_quietly(
                lib.stock_zh_a_hist_tx,
                symbol=tx_symbol,
                start_date=tx_start,
                end_date=(end or "20500101").replace("-", ""),
                adjust=adjust_map.get(adjust or "none", ""),
            )
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare TX history failed: {exc}", retryable=True) from exc

        tx_rows = tx_df.to_dict(orient="records")
        bars = [adapt_akshare_tx_bar_row(row) for row in tx_rows]

        try:
            daily_df = self._call_ak_quietly(
                lib.stock_zh_a_daily,
                symbol=tx_symbol,
                start_date=tx_start,
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
                try:
                    amt = row.get("amount") or row.get("成交额")
                    if amt is not None:
                        bar.turnover = float(amt)
                except Exception:
                    pass
        except Exception:
            pass

        bars = self._fill_prev_close(bars)
        bars = self._trim_before(bars, original_start)

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

    def _resolve_market_code(self, normalized: str) -> tuple[str, str]:
        """Resolve (code, market) for ak.stock_individual_fund_flow()."""
        code = normalized.split(".", 1)[0]
        exchange = normalized.split(".", 1)[1] if "." in normalized else "SZ"
        if exchange == "SH":
            return code, "sh"
        return code, "sz"

    def get_market_capital_flow(self, limit: int | None = None) -> tuple[list[CapitalFlowRecord], MarketFundFlowSummary]:
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_market_fund_flow)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare market fund flow failed: {exc}", retryable=True) from exc

        rows = df.to_dict(orient="records")
        records = [adapt_akshare_market_fund_flow(row) for row in rows]
        if limit:
            records = records[-limit:]
        summary = build_market_fund_flow_summary(records)
        return records, summary

    def get_individual_capital_flow(self, symbol: str, limit: int | None = None) -> list[CapitalFlowRecord]:
        lib = self._require_ak()
        normalized = normalize_symbol(symbol)
        code, market = self._resolve_market_code(normalized)
        try:
            df = self._call_ak_quietly(lib.stock_individual_fund_flow, stock=code, market=market)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare individual fund flow failed for {symbol}: {exc}", retryable=True) from exc

        rows = df.to_dict(orient="records")
        records = [adapt_akshare_individual_fund_flow(row) for row in rows]
        if limit:
            records = records[-limit:]
        return records

    def get_sector_capital_flow(self, flow_type: str = "industry") -> list[SectorFundFlowItem]:
        lib = self._require_ak()
        if flow_type == "concept":
            fn = lib.stock_fund_flow_concept
        else:
            fn = lib.stock_fund_flow_industry

        try:
            df = self._call_ak_quietly(fn)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare sector fund flow ({flow_type}) failed: {exc}", retryable=True) from exc

        rows = df.to_dict(orient="records")
        return [adapt_akshare_sector_fund_flow(row) for row in rows]

    def _resolve_symbol_code(self, symbol: str) -> str:
        """Resolve the 6-digit code from a normalized symbol like 000001.SZ."""
        return normalize_symbol(symbol).split(".", 1)[0]

    def get_financial_abstract(self, symbol: str) -> tuple[list[dict], FinancialSnapshot, list[FinancialHistoryPoint]]:
        """Fetch abstract financial metrics (core indicators) via stock_financial_abstract_new_ths.

        Returns (raw_rows, snapshot, history).
        """
        lib = self._require_ak()
        code = self._resolve_symbol_code(symbol)
        try:
            df = self._call_ak_quietly(lib.stock_financial_abstract_new_ths, symbol=code)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare financial abstract failed for {symbol}: {exc}", retryable=True) from exc

        rows = df.to_dict(orient="records")
        snapshot = build_financial_snapshot_from_abstract(symbol, rows)
        history = build_financial_history_from_abstract(rows)
        return rows, snapshot, history

    def get_financial_detail(self, symbol: str, statement: str = "income") -> list[FinancialDetailItem]:
        """Fetch detailed financial statement data.

        statement: "income" (利润表), "balance" (资产负债表), "cashflow" (现金流量表)
        """
        lib = self._require_ak()
        code = self._resolve_symbol_code(symbol)

        fn_map = {
            "income": lib.stock_financial_benefit_ths,
            "balance": lib.stock_financial_debt_new_ths,
            "cashflow": lib.stock_financial_cash_new_ths,
        }
        fn = fn_map.get(statement)
        if not fn:
            raise ProviderError("INVALID_ARGUMENT", f"Unsupported statement type: {statement}", retryable=False)

        try:
            df = self._call_ak_quietly(fn, symbol=code)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare financial detail ({statement}) failed for {symbol}: {exc}", retryable=True) from exc

        if statement == "income":
            # benefit_ths is wide format; convert to long format
            rows = df.to_dict(orient="records")
            items: list[FinancialDetailItem] = []
            for row in rows:
                report_date_raw = str(row.get("报告期", ""))[:10]
                if not report_date_raw:
                    continue
                for col_name, cell_value in row.items():
                    if col_name in ("报告期", "报表核心指标"):
                        continue
                    items.append(FinancialDetailItem(
                        report_date=report_date_raw,
                        report_name=row.get("报表核心指标", ""),
                        quarter_name="",
                        metric_name=col_name,
                        value=self._to_detail_float(cell_value),
                    ))
            return items
        else:
            # debt_new_ths / cash_new_ths are already long format
            rows = df.to_dict(orient="records")
            return [adapt_akshare_financial_detail_row(row) for row in rows]

    def _to_detail_float(self, value) -> float | None:
        if value is None or value == "" or value is False:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def get_limit_up_pool(self, trade_date: str) -> list[LimitUpItem]:
        """Fetch limit-up pool from ak.stock_zt_pool_em()."""
        lib = self._require_ak()
        date_str = trade_date.replace("-", "")
        try:
            df = self._call_ak_quietly(lib.stock_zt_pool_em, date=date_str)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare limit-up pool failed for {trade_date}: {exc}", retryable=True) from exc
        rows = df.to_dict(orient="records")
        return [adapt_em_limit_up_item(row) for row in rows]

    def get_broken_limit_pool(self, trade_date: str) -> list[BrokenLimitItem]:
        """Fetch broken limit pool from ak.stock_zt_pool_zbgc_em()."""
        lib = self._require_ak()
        date_str = trade_date.replace("-", "")
        try:
            df = self._call_ak_quietly(lib.stock_zt_pool_zbgc_em, date=date_str)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare broken limit pool failed for {trade_date}: {exc}", retryable=True) from exc
        rows = df.to_dict(orient="records")
        return [adapt_em_broken_limit_item(row) for row in rows]

    def get_previous_day_limit_pool(self, trade_date: str) -> list[PreviousDayLimitItem]:
        """Fetch yesterday's limit-up stocks' today performance from ak.stock_zt_pool_previous_em()."""
        lib = self._require_ak()
        date_str = trade_date.replace("-", "")
        try:
            df = self._call_ak_quietly(lib.stock_zt_pool_previous_em, date=date_str)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare previous limit pool failed for {trade_date}: {exc}", retryable=True) from exc
        rows = df.to_dict(orient="records")
        return [adapt_em_previous_limit_item(row) for row in rows]

    def get_northbound_history(self, symbol: str = "北向资金", limit: int | None = None) -> list[NorthboundFlowRecord]:
        """Fetch northbound historical flow from ak.stock_hsgt_hist_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_hsgt_hist_em, symbol=symbol)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare northbound history failed: {exc}", retryable=True) from exc
        rows = df.to_dict(orient="records")
        records = [adapt_em_hist_row(row) for row in rows]
        if limit:
            records = records[-limit:]
        return records

    def get_northbound_daily_summary(self) -> NorthboundDailySummary:
        """Fetch today's northbound flow summary from ak.stock_hsgt_fund_flow_summary_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_hsgt_fund_flow_summary_em)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare northbound daily summary failed: {exc}", retryable=True) from exc
        rows = df.to_dict(orient="records")
        return build_daily_summary_from_flow_summary(rows)

    def get_macro_raw(self, func_name: str, **kwargs) -> "pd.DataFrame":
        """Call an AKShare macro function by name and return the raw DataFrame."""
        lib = self._require_ak()
        fn = getattr(lib, func_name, None)
        if fn is None:
            raise ProviderError("INVALID_ARGUMENT", f"AKShare has no function: {func_name}", retryable=False)
        try:
            df = self._call_ak_quietly(fn, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare macro {func_name} failed: {exc}", retryable=True) from exc
        return df

    # ── Dragon Tiger (龙虎榜) ──────────────────────────────

    def get_dragon_tiger_daily(self, start_date: str, end_date: str | None = None) -> list[dict]:
        """Fetch daily dragon-tiger board detail from ak.stock_lhb_detail_em()."""
        from cn_stock_mcp.providers.adapters.akshare_dragon_tiger_adapters import adapt_daily_detail_row
        lib = self._require_ak()
        if end_date is None:
            end_date = start_date
        try:
            df = self._call_ak_quietly(lib.stock_lhb_detail_em, start_date=start_date, end_date=end_date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dragon_tiger_daily failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_dragon_tiger_institution(self, start_date: str, end_date: str | None = None) -> list[dict]:
        """Fetch institution buy/sell stats from ak.stock_lhb_jgmmtj_em()."""
        lib = self._require_ak()
        if end_date is None:
            end_date = start_date
        try:
            df = self._call_ak_quietly(lib.stock_lhb_jgmmtj_em, start_date=start_date, end_date=end_date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dragon_tiger_institution failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_dragon_tiger_active_broker(self, start_date: str, end_date: str | None = None) -> list[dict]:
        """Fetch active broker data from ak.stock_lhb_hyyyb_em()."""
        lib = self._require_ak()
        if end_date is None:
            end_date = start_date
        try:
            df = self._call_ak_quietly(lib.stock_lhb_hyyyb_em, start_date=start_date, end_date=end_date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dragon_tiger_active_broker failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_dragon_tiger_broker_rank(self, period: str = "近一月") -> list[dict]:
        """Fetch broker success-rate ranking from ak.stock_lhb_yybph_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_lhb_yybph_em, symbol=period)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dragon_tiger_broker_rank failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_dragon_tiger_stock_stat(self, period: str = "近一月") -> list[dict]:
        """Fetch stock board statistics from ak.stock_lhb_stock_statistic_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_lhb_stock_statistic_em, symbol=period)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dragon_tiger_stock_stat failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── ETF Snapshot ──────────────────────────────────────

    def get_etf_spot_em(self) -> list[dict]:
        """Fetch full-market ETF real-time snapshot from ak.fund_etf_spot_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.fund_etf_spot_em)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare etf_spot failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_etf_scale_sse(self) -> list[dict]:
        """Fetch SSE ETF share/scale from ak.fund_etf_scale_sse()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.fund_etf_scale_sse)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare etf_scale failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_etf_nav(self, fund: str, start_date: str = "20000101", end_date: str = "20500101") -> list[dict]:
        """Fetch ETF NAV series from ak.fund_etf_fund_info_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.fund_etf_fund_info_em, fund=fund, start_date=start_date, end_date=end_date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare etf_nav failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Convertible Bond (可转债) ────────────────────────

    def get_cb_spot(self) -> list[dict]:
        """Fetch convertible bond snapshot from ak.bond_cb_jsl()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.bond_cb_jsl)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare cb_spot failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_cb_redeem(self) -> list[dict]:
        """Fetch convertible bond call/redeem data from ak.bond_cb_redeem_jsl()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.bond_cb_redeem_jsl)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare cb_redeem failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_cb_index(self) -> list[dict]:
        """Fetch convertible bond index from ak.bond_cb_index_jsl()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.bond_cb_index_jsl)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare cb_index failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Derivatives (期货/期权) ───────────────────────────

    def get_futures_spot(self) -> list[dict]:
        """Fetch futures real-time quotes from ak.futures_zh_realtime()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.futures_zh_realtime)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare futures_spot failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_futures_hist(self, symbol: str) -> list[dict]:
        """Fetch futures daily history from ak.futures_zh_daily_sina()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.futures_zh_daily_sina, symbol=symbol)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare futures_hist failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_option_list_sse(self) -> list[dict]:
        """Fetch SSE option contracts from ak.option_current_day_sse()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.option_current_day_sse)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare option_list_sse failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_option_list_szse(self) -> list[dict]:
        """Fetch SZSE option contracts from ak.option_current_day_szse()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.option_current_day_szse)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare option_list_szse failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_qvix(self, underlying: str = "50etf") -> list[dict]:
        """Fetch QVIX implied volatility from ak.index_option_*_qvix()."""
        lib = self._require_ak()
        qvix_map = {
            "50etf": lib.index_option_50etf_qvix,
            "300etf": lib.index_option_300etf_qvix,
            "500etf": lib.index_option_500etf_qvix,
            "100etf": lib.index_option_100etf_qvix,
            "50index": lib.index_option_50index_qvix,
            "300index": lib.index_option_300index_qvix,
            "1000index": lib.index_option_1000index_qvix,
            "kcb": lib.index_option_kcb_qvix,
            "cyb": lib.index_option_cyb_qvix,
        }
        fn = qvix_map.get(underlying)
        if fn is None:
            available = "/".join(qvix_map.keys())
            raise ProviderError("INVALID_ARGUMENT", f"Unknown QVIX underlying '{underlying}'. Available: {available}", retryable=False)
        try:
            df = self._call_ak_quietly(fn)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare qvix({underlying}) failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Margin Trading (融资融券) ────────────────────────

    def get_margin_sse_summary(self, start_date: str, end_date: str | None = None) -> list[dict]:
        """Fetch SSE margin summary from ak.stock_margin_sse()."""
        lib = self._require_ak()
        kwargs = {"start_date": start_date}
        if end_date:
            kwargs["end_date"] = end_date
        try:
            df = self._call_ak_quietly(lib.stock_margin_sse, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare margin_sse_summary failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_margin_szse_summary(self, date: str) -> list[dict]:
        """Fetch SZSE margin summary from ak.stock_margin_szse()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_margin_szse, date=date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare margin_szse_summary failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_margin_sse_detail(self, date: str) -> list[dict]:
        """Fetch SSE margin detail from ak.stock_margin_detail_sse()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_margin_detail_sse, date=date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare margin_sse_detail failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_margin_szse_detail(self, date: str) -> list[dict]:
        """Fetch SZSE margin detail from ak.stock_margin_detail_szse()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_margin_detail_szse, date=date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare margin_szse_detail failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Block Trade (大宗交易) ────────────────────────────

    def get_block_trade_daily(self, start_date: str, end_date: str | None = None) -> list[dict]:
        """Fetch block trade daily detail from ak.stock_dzjy_mrmx()."""
        lib = self._require_ak()
        kwargs = {"start_date": start_date.replace("-", ""), "end_date": (end_date or start_date).replace("-", "")}
        try:
            df = self._call_ak_quietly(lib.stock_dzjy_mrmx, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare block_trade_daily failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_block_trade_daily_stat(self, start_date: str, end_date: str | None = None) -> list[dict]:
        """Fetch block trade daily stock summary from ak.stock_dzjy_mrtj()."""
        lib = self._require_ak()
        kwargs = {"start_date": start_date.replace("-", ""), "end_date": (end_date or start_date).replace("-", "")}
        try:
            df = self._call_ak_quietly(lib.stock_dzjy_mrtj, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare block_trade_daily_stat failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_block_trade_industry(self, period: str = "近3日") -> list[dict]:
        """Fetch block trade industry summary from ak.stock_dzjy_hyyybtj()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_dzjy_hyyybtj, symbol=period)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare block_trade_industry failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_block_trade_broker_rank(self, period: str = "近一月") -> list[dict]:
        """Fetch block trade broker ranking from ak.stock_dzjy_yybph()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_dzjy_yybph, symbol=period)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare block_trade_broker_rank failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_block_trade_active_stock(self, period: str = "近一月") -> list[dict]:
        """Fetch block trade active stock ranking from ak.stock_dzjy_hygtj()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_dzjy_hygtj, symbol=period)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare block_trade_active_stock failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Institute Hold (机构持仓) ──────────────────────────

    def get_institute_hold(self, quarter: str) -> list[dict]:
        """Fetch quarterly institute holding summary from ak.stock_institute_hold().

        quarter format: YYYYQ, e.g. "20243" for 2024Q3.
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_institute_hold, symbol=quarter)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare institute_hold failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_institute_hold_detail(self, stock: str, quarter: str) -> list[dict]:
        """Fetch per-stock institute holding detail from ak.stock_institute_hold_detail().

        stock: 6-digit code, e.g. "600519"
        quarter: YYYYQ, e.g. "20243"
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_institute_hold_detail, stock=stock, quarter=quarter)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare institute_hold_detail failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Money Rate (货币市场利率) ──────────────────────────

    def get_shibor_all(self) -> list[dict]:
        """Fetch SHIBOR full-term curve from ak.macro_china_shibor_all()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.macro_china_shibor_all)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare shibor_all failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_interbank_rate(self, indicator: str = "隔夜") -> list[dict]:
        """Fetch interbank rate from ak.rate_interbank().

        indicator: 隔夜/1周/2周/1月/3月/6月/9月/1年
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(
                lib.rate_interbank,
                market="上海银行同业拆借市场",
                symbol="Shibor人民币",
                indicator=indicator,
            )
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare interbank_rate failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_repo_rate_latest(self) -> list[dict]:
        """Fetch latest repo fixing rates from ak.repo_rate_query()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.repo_rate_query, symbol="回购定盘利率")
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare repo_rate_latest failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_repo_rate_hist(self, start_date: str, end_date: str) -> list[dict]:
        """Fetch repo rate history from ak.repo_rate_hist().

        start_date/end_date: YYYYMMDD format.
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(
                lib.repo_rate_hist,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
            )
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare repo_rate_hist failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Stock Screen (选股筛选) ──────────────────────────────

    def get_a_share_spot_all(self) -> list[dict]:
        """Fetch full A-share spot table from ak.stock_zh_a_spot() (Sina source)."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_zh_a_spot)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare a_share_spot_all failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Insider Trade (高管增减持/十大股东) ────────────────

    def get_insider_top10(self, symbol: str, date: str) -> list[dict]:
        """Fetch top 10 free-float shareholders from ak.stock_gdfx_free_top_10_em().

        symbol: sh600519 format
        date: YYYYMMDD quarter-end, e.g. "20250930"
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_gdfx_free_top_10_em, symbol=symbol, date=date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare insider_top10 failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_insider_change(self, symbol: str) -> list[dict]:
        """Fetch insider/shareholder trade changes from ak.stock_shareholder_change_ths().

        symbol: 6-digit code, e.g. "600519"
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_shareholder_change_ths, symbol=symbol)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare insider_change failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Dividend Rank (股息率/分红排名) ──────────────────────

    def get_dividend_history_rank(self) -> list[dict]:
        """Fetch full-market historical dividend ranking from ak.stock_history_dividend()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_history_dividend)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dividend_history_rank failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_dividend_plan(self, date: str) -> list[dict]:
        """Fetch dividend distribution plan by report period from ak.stock_fhps_em().

        date: YYYYMMDD, e.g. "20241231"
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_fhps_em, date=date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dividend_plan failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_dividend_detail(self, symbol: str) -> list[dict]:
        """Fetch per-stock historical dividend detail from ak.stock_history_dividend_detail().

        symbol: 6-digit code, e.g. "000002"
        indicator: "分红" for dividend history
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_history_dividend_detail, symbol=symbol, indicator="分红")
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare dividend_detail failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Shareholder Change (股东变动) ──────────────────────

    def get_shareholder_top10(self, symbol: str, date: str) -> list[dict]:
        """Fetch top 10 shareholders from ak.stock_gdfx_top_10_em().

        symbol: sh600519 format
        date: YYYYMMDD, e.g. "20250930"
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_gdfx_top_10_em, symbol=symbol, date=date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare shareholder_top10 failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_shareholder_change(self, date: str) -> list[dict]:
        """Fetch shareholder holding change summary from ak.stock_gdfx_free_holding_change_em().

        date: YYYYMMDD, e.g. "20250930"
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_gdfx_free_holding_change_em, date=date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare shareholder_change failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Disclosure Calendar (披露日历) ──────────────────────

    def get_disclosure_calendar(self, market: str = "沪深京", period: str = "2024年报") -> list[dict]:
        """Fetch disclosure calendar from ak.stock_report_disclosure().

        market: 沪深京/深市/沪市/京市
        period: YYYY年报/YYYY一季/YYYY半年/YYYY三季
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_report_disclosure, market=market, period=period)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare disclosure_calendar failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Stock Repurchase (回购明细) ──────────────────────────

    def get_stock_repurchase(self) -> list[dict]:
        """Fetch stock repurchase data from ak.stock_repurchase_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_repurchase_em)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare stock_repurchase failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Industry Chain (产业链上下游) ──────────────────────

    def get_industry_summary(self) -> list[dict]:
        """Fetch industry board summary from ak.stock_board_industry_summary_ths()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_board_industry_summary_ths)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare industry_summary failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_concept_summary(self) -> list[dict]:
        """Fetch concept board summary from ak.stock_board_concept_summary_ths()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_board_concept_summary_ths)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare concept_summary failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Stock Warrant (权证/期权) ──────────────────────────

    def get_etf_option(self, symbol: str = "50ETF期权") -> list[dict]:
        """Fetch ETF option quotes from ak.option_sina_sse().

        symbol: 50ETF期权/300ETF期权/500ETF期权/创业板ETF期权/科创50ETF期权
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.option_sina_sse, symbol=symbol, exchange="null")
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare etf_option failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_commodity_option(self, exchange: str = "郑商所") -> list[dict]:
        """Fetch commodity option quotes from ak.option_sina_sse().

        exchange: 郑商所/大商所/上期所/广期所
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.option_sina_sse, symbol="商品期权", exchange=exchange)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare commodity_option failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_index_option(self, date: str = "") -> list[dict]:
        """Fetch CFFEX index option from ak.option_cffex_cks().

        date: YYYYMMDD, e.g. "20260513"
        """
        lib = self._require_ak()
        try:
            kwargs = {"date": date} if date else {}
            df = self._call_ak_quietly(lib.option_cffex_cks, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare index_option failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Fund Flow (主力资金流向) ───────────────────────────

    def get_market_fund_flow(self) -> list[dict]:
        """Fetch market-level fund flow from ak.stock_market_fund_flow()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_market_fund_flow)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare market_fund_flow failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_industry_fund_flow(self, symbol: str = "即时") -> list[dict]:
        """Fetch industry fund flow from ak.stock_fund_flow_industry().

        symbol: 即时/3日/5日/10日
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_fund_flow_industry, symbol=symbol)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare industry_fund_flow failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_stock_fund_flow(self, stock: str, market: str = "sh") -> list[dict]:
        """Fetch individual stock fund flow from ak.stock_individual_fund_flow().

        stock: 6-digit code, e.g. "600519"
        market: sh/sz
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_individual_fund_flow, stock=stock, market=market)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare stock_fund_flow failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Limit Up Pool (涨停/跌停股池) ─────────────────────

    def get_limit_up_pool_raw(self, date: str = "") -> list[dict]:
        """Fetch raw limit-up pool from ak.stock_zt_pool_em()."""
        lib = self._require_ak()
        try:
            kwargs = {"date": date} if date else {}
            df = self._call_ak_quietly(lib.stock_zt_pool_em, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare limit_up_pool failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_limit_down_pool(self, date: str = "") -> list[dict]:
        """Fetch limit-down pool from ak.stock_zt_pool_dtgc_em()."""
        lib = self._require_ak()
        try:
            kwargs = {"date": date} if date else {}
            df = self._call_ak_quietly(lib.stock_zt_pool_dtgc_em, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare limit_down_pool failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_strong_pool(self, date: str = "") -> list[dict]:
        """Fetch strong/continuous limit-up pool from ak.stock_zt_pool_strong_em()."""
        lib = self._require_ak()
        try:
            kwargs = {"date": date} if date else {}
            df = self._call_ak_quietly(lib.stock_zt_pool_strong_em, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare strong_pool failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_previous_limit_pool(self, date: str = "") -> list[dict]:
        """Fetch previous day limit-up performance from ak.stock_zt_pool_previous_em()."""
        lib = self._require_ak()
        try:
            kwargs = {"date": date} if date else {}
            df = self._call_ak_quietly(lib.stock_zt_pool_previous_em, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare previous_limit_pool failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_sub_new_pool(self, date: str = "") -> list[dict]:
        """Fetch sub-new stock limit-up pool from ak.stock_zt_pool_sub_new_em()."""
        lib = self._require_ak()
        try:
            kwargs = {"date": date} if date else {}
            df = self._call_ak_quietly(lib.stock_zt_pool_sub_new_em, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare sub_new_pool failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_broken_pool(self, date: str = "") -> list[dict]:
        """Fetch broken limit-up pool from ak.stock_zt_pool_zbgc_em()."""
        lib = self._require_ak()
        try:
            kwargs = {"date": date} if date else {}
            df = self._call_ak_quietly(lib.stock_zt_pool_zbgc_em, **kwargs)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare broken_pool failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    # ── Sec Reveal (龙虎榜机构席位深度) ───────────────────

    def get_lhb_stock_seat_detail(self, symbol: str, date: str, flag: str = "买入") -> list[dict]:
        """Fetch stock-level dragon-tiger seat details from ak.stock_lhb_stock_detail_em().

        symbol: 6-digit stock code, e.g. "300965"
        date: YYYYMMDD
        flag: 买入/卖出
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_lhb_stock_detail_em, symbol=symbol, date=date, flag=flag)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare lhb_stock_seat_detail failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_lhb_active_broker(self, start_date: str, end_date: str | None = None) -> list[dict]:
        """Fetch active broker seats from ak.stock_lhb_hyyyb_em()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_lhb_hyyyb_em, start_date=start_date, end_date=end_date or start_date)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare lhb_active_broker failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_lhb_institution_detail_sina(self) -> list[dict]:
        """Fetch recent institution dragon-tiger detail from ak.stock_lhb_jgmx_sina()."""
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_lhb_jgmx_sina)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare lhb_institution_detail_sina failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

    def get_lhb_institution_trace_sina(self, period: str = "5") -> list[dict]:
        """Fetch institution tracking stats from ak.stock_lhb_jgzz_sina().

        period: 5/10/30/60
        """
        lib = self._require_ak()
        try:
            df = self._call_ak_quietly(lib.stock_lhb_jgzz_sina, symbol=period)
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"AKShare lhb_institution_trace_sina failed: {exc}", retryable=True) from exc
        return df.to_dict(orient="records")

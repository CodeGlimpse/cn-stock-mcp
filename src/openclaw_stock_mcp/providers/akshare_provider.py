from __future__ import annotations

from datetime import date, datetime

from openclaw_stock_mcp.providers.errors import ProviderError

try:
    import akshare as ak
except Exception:  # pragma: no cover
    ak = None

from openclaw_stock_mcp.providers.adapters.akshare_adapters import (
    adapt_akshare_fund_list_row,
    adapt_akshare_index_list_row,
    adapt_akshare_stock_list_row,
)
from openclaw_stock_mcp.providers.adapters.akshare_market_adapters import adapt_akshare_tx_bar_row
from openclaw_stock_mcp.infra.time_utils import normalize_symbol


class AKShareProvider:
    name = "akshare"

    def _require_ak(self):
        if ak is None:
            raise ProviderError("PROVIDER_UNAVAILABLE", "akshare is not installed", retryable=False)
        return ak

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
        if interval != "1d":
            raise ProviderError("UNSUPPORTED_INTERVAL", "AKShare minimal version supports 1d only", retryable=False)

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
        if limit:
            tx_rows = tx_rows[-limit:]
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

        return bars

    def get_orderbook(self, symbol: str, sec_type: str):
        raise ProviderError("UNSUPPORTED_MARKET", "AKShare orderbook not implemented", retryable=False)

    def get_indicator(self, symbol: str, sec_type: str, interval: str, indicator: str, start=None, end=None, limit=None):
        raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare indicator not implemented", retryable=False)

    def get_market_overview(self, market: str = "CN"):
        return {"market": market, "indices": [], "source": "akshare"}

    def get_market_pool(self, pool_type: str, trade_date: str | None = None):
        raise ProviderError("UNSUPPORTED_SEC_TYPE", "AKShare market pool not implemented", retryable=False)

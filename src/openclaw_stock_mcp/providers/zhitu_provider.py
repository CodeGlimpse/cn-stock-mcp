from __future__ import annotations

import httpx

from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.infra.http_client import build_http_client
from openclaw_stock_mcp.infra.time_utils import detect_board, normalize_symbol
from openclaw_stock_mcp.providers.adapters.zhitu_instrument_adapters import (
    adapt_zhitu_fund_list_item,
    adapt_zhitu_index_list_item,
    adapt_zhitu_primary_sector_item,
    adapt_zhitu_sector_list_item,
    adapt_zhitu_sector_member_item,
    adapt_zhitu_stock_list_item,
)
from openclaw_stock_mcp.providers.adapters.zhitu_market_adapters import adapt_zhitu_orderbook, adapt_zhitu_quote
from openclaw_stock_mcp.providers.adapters.zhitu_series_adapters import (
    adapt_zhitu_bar,
    adapt_zhitu_indicator_series,
    adapt_zhitu_limit_down_item,
    adapt_zhitu_limit_up_item,
    adapt_zhitu_strong_item,
)
from openclaw_stock_mcp.providers.errors import ProviderAuthError, ProviderError, ProviderTimeoutError


class ZhituProvider:
    name = "zhitu"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.zhitu_base_url.rstrip("/")
        self.token = self.settings.resolve_zhitu_token()
        self.client = build_http_client(self.settings.zhitu_timeout_seconds)

    def _get_json(self, path: str, params: dict | None = None):
        if not self.token:
            raise ProviderAuthError("PROVIDER_AUTH_FAILED", "Zhitu token is empty", retryable=False)
        params = params.copy() if params else {}
        params["token"] = self.token
        url = f"{self.base_url}{path}"
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("PROVIDER_TIMEOUT", f"Zhitu request timed out: {path}", retryable=True) from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403):
                raise ProviderAuthError("PROVIDER_AUTH_FAILED", "Zhitu authentication failed", retryable=False) from exc
            raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu http error: {exc.response.status_code}", retryable=True) from exc
        except Exception as exc:
            raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu request failed: {exc}", retryable=True) from exc

    def search_instruments(self, query: str, sec_types=None, market: str | None = None, limit: int = 10):
        sec_types = sec_types or ["stock", "index", "fund"]
        items = []

        if "stock" in sec_types:
            for raw in self._get_json("/hs/list/all"):
                if query in str(raw.get("dm", "")) or query in str(raw.get("mc", "")):
                    items.append(adapt_zhitu_stock_list_item(raw))
        if "index" in sec_types:
            for raw in self._get_json("/hz/list/hszs"):
                if query in str(raw.get("dm", "")) or query in str(raw.get("mc", "")):
                    items.append(adapt_zhitu_index_list_item(raw))
        if "fund" in sec_types:
            for raw in self._get_json("/fund/list/all"):
                if query in str(raw.get("dm", "")) or query in str(raw.get("mc", "")):
                    items.append(adapt_zhitu_fund_list_item(raw))
        if "sector" in sec_types:
            for raw in self._get_json("/hs/list/sectors"):
                if query in str(raw.get("dm", "")) or query in str(raw.get("mc", "")):
                    items.append(adapt_zhitu_sector_list_item(raw))

        return items[:limit]

    def _normalize_sector_mode(self, mode: str) -> str:
        if mode == "members":
            return "children"
        return mode

    def _slice_items(self, items: list, limit: int) -> list:
        return items[:limit] if limit and limit > 0 else items

    def _extract_sector_children_items(self, raw):
        if isinstance(raw, dict):
            stocks = raw.get("stocks")
            if isinstance(stocks, list):
                return [adapt_zhitu_sector_member_item(item) for item in stocks if isinstance(item, dict)]
            return []
        if isinstance(raw, list):
            return [adapt_zhitu_sector_member_item(item) for item in raw if isinstance(item, dict)]
        return []

    def get_sector_lookup(self, mode: str, sector_type: str | None = None, sector_name: str | None = None, limit: int = 100):
        normalized_mode = self._normalize_sector_mode(mode)

        if normalized_mode == "list":
            if sector_type == "primary":
                raw = self._get_json("/hs/list/primary")
                items = [adapt_zhitu_primary_sector_item(item) for item in raw if isinstance(item, dict)]
                return self._slice_items(items, limit)

            raw = self._get_json("/hs/list/sectors")
            items = [adapt_zhitu_sector_list_item(item) for item in raw if isinstance(item, dict)]
            return self._slice_items(items, limit)

        if normalized_mode == "children":
            if not sector_name:
                raise ProviderError("INVALID_ARGUMENT", "sector_name is required when mode=children", retryable=False)
            raw = self._get_json(f"/hs/sectors/{sector_name}")
            items = self._extract_sector_children_items(raw)
            return self._slice_items(items, limit)

        raise ProviderError("INVALID_ARGUMENT", f"Unsupported mode: {mode}", retryable=False)

    def get_quote(self, symbol: str, sec_type: str):
        normalized = normalize_symbol(symbol)
        code = normalized.split(".", 1)[0]
        exchange = normalized.split(".", 1)[1] if "." in normalized else None
        board = detect_board(normalized, sec_type)

        if sec_type == "index" and normalized.endswith(".BJ"):
            raw = self._get_json(f"/bj/index/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            return adapt_zhitu_quote(raw, normalized, sec_type, exchange="BJ", board="index")

        if sec_type == "index":
            raw = self._get_json(f"/hz/real/ssjy/{normalized}")
            if isinstance(raw, list):
                raw = raw[0]
            return adapt_zhitu_quote(raw, normalized, sec_type, exchange=exchange, board=board)

        if sec_type == "fund":
            raw = self._get_json(f"/fund/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            return adapt_zhitu_quote(raw, normalized, sec_type, exchange=exchange, board="fund")

        if sec_type == "stock" and normalized.endswith(".BJ"):
            raw = self._get_json(f"/bj/stock/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            return adapt_zhitu_quote(raw, normalized, sec_type, exchange="BJ", board="beijing")

        if sec_type == "stock" and code.startswith("688"):
            raw = self._get_json(f"/tech/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            return adapt_zhitu_quote(raw, normalized, sec_type, exchange="SH", board="star")

        if sec_type == "stock" and exchange in {"SH", "SZ"}:
            raw = self._get_json(f"/hs/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            if isinstance(raw, dict) and raw.get("error"):
                raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu quote unavailable for {symbol}: {raw.get('error')}", retryable=True)
            return adapt_zhitu_quote(raw, normalized, sec_type, exchange=exchange, board=board)

        raise ProviderError("UNSUPPORTED_MARKET", f"Zhitu quote route not implemented for {symbol}/{sec_type}", retryable=False)

    def get_quotes(self, symbols: list[str], sec_type: str | None = None):
        return [self.get_quote(symbol, sec_type or "stock") for symbol in symbols]

    def get_history(self, symbol: str, sec_type: str, interval: str, start=None, end=None, limit=None, adjust=None):
        normalized = normalize_symbol(symbol)
        if sec_type != "index":
            raise ProviderError("UNSUPPORTED_SEC_TYPE", "Zhitu history currently supports index route only", retryable=False)

        interval_map = {"5m": "5", "15m": "15", "30m": "30", "60m": "60", "1d": "d", "1w": "w", "1M": "m", "1y": "y"}
        mapped = interval_map.get(interval)
        if not mapped:
            raise ProviderError("UNSUPPORTED_INTERVAL", f"Unsupported interval: {interval}", retryable=False)

        params = {}
        if start:
            params["st"] = start.replace("-", "")
        if end:
            params["et"] = end.replace("-", "")

        raw = self._get_json(f"/hz/history/fsjy/{normalized}/{mapped}", params=params)
        if isinstance(raw, dict) and raw.get("error"):
            raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu history unavailable for {symbol}: {raw.get('error')}", retryable=True)
        if limit:
            raw = raw[-limit:]
        return [adapt_zhitu_bar(item) for item in raw]

    def get_orderbook(self, symbol: str, sec_type: str):
        normalized = normalize_symbol(symbol)
        code = normalized.split(".", 1)[0]

        if normalized.endswith(".BJ"):
            raw = self._get_json(f"/bj/stock/real/mmwp/{code}")
        elif code.startswith("688"):
            raw = self._get_json(f"/tech/real/mmwp/{code}")
        else:
            raise ProviderError("UNSUPPORTED_MARKET", f"Zhitu orderbook route not implemented for {symbol}", retryable=False)

        if isinstance(raw, list):
            raw = raw[0]
        return adapt_zhitu_orderbook(raw, normalized)

    def get_indicator(self, symbol: str, sec_type: str, interval: str, indicator: str, start=None, end=None, limit=None):
        normalized = normalize_symbol(symbol)
        interval_map = {"5m": "5", "15m": "15", "30m": "30", "60m": "60", "1d": "d", "1w": "w", "1M": "m", "1y": "y"}
        mapped = interval_map.get(interval)
        if not mapped:
            raise ProviderError("UNSUPPORTED_INTERVAL", f"Unsupported interval: {interval}", retryable=False)

        params = {}
        if start:
            params["st"] = start.replace("-", "")
        if end:
            params["et"] = end.replace("-", "")
        if limit:
            params["lt"] = limit

        raw = self._get_json(f"/hz/history/{indicator}/{normalized}/{mapped}", params=params)
        return adapt_zhitu_indicator_series(normalized, sec_type, interval, indicator, raw)

    def get_market_overview(self, market: str = "CN"):
        index_list = self._get_json("/hz/list/hszs")
        selected = []
        target_names = {"上证指数", "深证成指", "创业板指", "北证50"}
        for raw in index_list:
            name = str(raw.get("mc", ""))
            symbol = str(raw.get("dm", ""))
            if name in target_names or symbol in {"000001.SH", "399001.SZ", "399006.SZ", "899050.BJ"}:
                try:
                    selected.append(self.get_quote(symbol, "index"))
                except Exception:
                    continue
        return {"market": market, "indices": selected, "source": "zhitu"}

    def get_market_pool(self, pool_type: str, trade_date: str | None = None):
        if not trade_date:
            raise ProviderError("INVALID_ARGUMENT", "trade_date is required for market_pool in minimal version", retryable=False)
        path_map = {
            "limit_up": f"/hs/pool/ztgc/{trade_date}",
            "limit_down": f"/hs/pool/dtgc/{trade_date}",
            "strong": f"/hs/pool/qsgc/{trade_date}",
        }
        path = path_map.get(pool_type)
        if not path:
            raise ProviderError("INVALID_ARGUMENT", f"Unsupported pool_type: {pool_type}", retryable=False)
        raw = self._get_json(path)
        if pool_type == "limit_up":
            return [adapt_zhitu_limit_up_item(item) for item in raw]
        if pool_type == "limit_down":
            return [adapt_zhitu_limit_down_item(item) for item in raw]
        return [adapt_zhitu_strong_item(item) for item in raw]

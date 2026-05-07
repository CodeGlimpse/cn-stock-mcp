from __future__ import annotations

import time

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
    adapt_zhitu_broken_limit_item,
    adapt_zhitu_indicator_series,
    adapt_zhitu_limit_down_item,
    adapt_zhitu_limit_up_item,
    adapt_zhitu_strong_item,
    adapt_zhitu_sub_new_item,
)
from openclaw_stock_mcp.providers.errors import ProviderAuthError, ProviderError, ProviderRateLimitError, ProviderTimeoutError


class ZhituProvider:
    name = "zhitu"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.zhitu_base_url.rstrip("/")
        self.tokens = self.settings.resolve_zhitu_tokens()
        self.token = self.tokens[0] if self.tokens else ""
        self.client = build_http_client(self.settings.zhitu_timeout_seconds)
        self._instrument_name_cache: dict[tuple[str, str], str] = {}
        self._token_cooldowns: dict[str, float] = {}
        self._token_stats: dict[str, dict[str, float | int | None]] = {
            token: {
                "total_requests": 0,
                "success_count": 0,
                "failure_count": 0,
                "rate_limit_count": 0,
                "last_success_at": None,
                "last_failure_at": None,
            }
            for token in self.tokens
        }

    def _now(self) -> float:
        return time.time()

    def _ensure_token_state(self, token: str):
        if token not in self._token_stats:
            self._token_stats[token] = {
                "total_requests": 0,
                "success_count": 0,
                "failure_count": 0,
                "rate_limit_count": 0,
                "last_success_at": None,
                "last_failure_at": None,
            }

    def _token_score(self, token: str, now: float | None = None) -> float:
        self._ensure_token_state(token)
        stats = self._token_stats[token]
        now = now if now is not None else self._now()

        total = int(stats.get("total_requests", 0) or 0)
        success = int(stats.get("success_count", 0) or 0)
        failures = int(stats.get("failure_count", 0) or 0)
        rate_limits = int(stats.get("rate_limit_count", 0) or 0)
        cooldown_until = float(self._token_cooldowns.get(token, 0) or 0)
        last_failure_at = stats.get("last_failure_at")

        success_rate = (success / total) if total > 0 else 0.5
        base = success_rate * 100.0
        penalty = failures * 1.5 + rate_limits * 8.0

        if cooldown_until > now:
            penalty += 100.0

        if isinstance(last_failure_at, (int, float)):
            age = max(0.0, now - float(last_failure_at))
            if age < 300:
                penalty += (300 - age) / 30.0

        return base - penalty

    def _available_tokens(self) -> list[str]:
        if not self.tokens:
            return []

        now = self._now()
        available = [token for token in self.tokens if self._token_cooldowns.get(token, 0) <= now]
        candidates = available or list(self.tokens)
        return sorted(candidates, key=lambda token: self._token_score(token, now), reverse=True)

    def _mark_token_rate_limited(self, token: str):
        cooldown_seconds = max(int(getattr(self.settings, "zhitu_token_cooldown_seconds", 60) or 60), 1)
        self._token_cooldowns[token] = self._now() + cooldown_seconds
        self._record_token_failure(token, rate_limited=True)

    def _record_token_success(self, token: str):
        self._ensure_token_state(token)
        stats = self._token_stats[token]
        stats["total_requests"] = int(stats.get("total_requests", 0) or 0) + 1
        stats["success_count"] = int(stats.get("success_count", 0) or 0) + 1
        stats["last_success_at"] = self._now()

    def _record_token_failure(self, token: str, rate_limited: bool = False):
        self._ensure_token_state(token)
        stats = self._token_stats[token]
        stats["total_requests"] = int(stats.get("total_requests", 0) or 0) + 1
        stats["failure_count"] = int(stats.get("failure_count", 0) or 0) + 1
        if rate_limited:
            stats["rate_limit_count"] = int(stats.get("rate_limit_count", 0) or 0) + 1
        stats["last_failure_at"] = self._now()

    def _get_json(self, path: str, params: dict | None = None):
        tokens = self._available_tokens()
        if not tokens:
            raise ProviderAuthError("PROVIDER_AUTH_FAILED", "Zhitu token is empty", retryable=False)

        url = f"{self.base_url}{path}"
        last_error: Exception | None = None

        for idx, token in enumerate(tokens):
            request_params = params.copy() if params else {}
            request_params["token"] = token
            self.token = token
            try:
                response = self.client.get(url, params=request_params)
                response.raise_for_status()
                self._record_token_success(token)
                return response.json()
            except httpx.TimeoutException as exc:
                self._record_token_failure(token)
                last_error = ProviderTimeoutError("PROVIDER_TIMEOUT", f"Zhitu request timed out: {path}", retryable=True)
                break
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code in (401, 403):
                    self._record_token_failure(token)
                    last_error = ProviderAuthError("PROVIDER_AUTH_FAILED", "Zhitu authentication failed", retryable=False)
                    continue
                if status_code == 429:
                    self._mark_token_rate_limited(token)
                    last_error = ProviderRateLimitError("PROVIDER_RATE_LIMIT", f"Zhitu rate limited: {path}", retryable=True)
                    if idx < len(tokens) - 1:
                        continue
                    raise last_error from exc
                self._record_token_failure(token)
                last_error = ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu http error: {status_code}", retryable=True)
                raise last_error from exc
            except ProviderError:
                self._record_token_failure(token)
                raise
            except Exception as exc:
                self._record_token_failure(token)
                last_error = ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu request failed: {exc}", retryable=True)
                raise last_error from exc

        if last_error:
            raise last_error
        raise ProviderAuthError("PROVIDER_AUTH_FAILED", "Zhitu token is empty", retryable=False)

    def _cache_instrument_name(self, sec_type: str, symbol: str | None, name: str | None):
        if symbol and name:
            self._instrument_name_cache[(sec_type, symbol)] = name

    def _warm_name_cache_for_symbol(self, sec_type: str, symbol: str):
        if (sec_type, symbol) in self._instrument_name_cache:
            return

        if sec_type == "index":
            for raw in self._get_json("/hz/list/hszs"):
                item = adapt_zhitu_index_list_item(raw)
                self._cache_instrument_name("index", item.symbol, item.name)
            return

        if sec_type == "fund":
            for raw in self._get_json("/fund/list/all"):
                item = adapt_zhitu_fund_list_item(raw)
                self._cache_instrument_name("fund", item.symbol, item.name)
            return

        if sec_type == "stock":
            for raw in self._get_json("/hs/list/all"):
                item = adapt_zhitu_stock_list_item(raw)
                self._cache_instrument_name("stock", item.symbol, item.name)
            return

    def _fill_quote_name(self, quote, sec_type: str, symbol: str):
        if getattr(quote, "name", None):
            return quote
        name = self._instrument_name_cache.get((sec_type, symbol))
        if not name:
            try:
                self._warm_name_cache_for_symbol(sec_type, symbol)
            except Exception:
                pass
            name = self._instrument_name_cache.get((sec_type, symbol))
        if name:
            quote.name = name
        return quote

    def search_instruments(self, query: str, sec_types=None, market: str | None = None, limit: int = 10):
        sec_types = sec_types or ["stock", "index", "fund"]
        items = []

        if "stock" in sec_types:
            for raw in self._get_json("/hs/list/all"):
                if query in str(raw.get("dm", "")) or query in str(raw.get("mc", "")):
                    item = adapt_zhitu_stock_list_item(raw)
                    self._cache_instrument_name("stock", item.symbol, item.name)
                    items.append(item)
        if "index" in sec_types:
            for raw in self._get_json("/hz/list/hszs"):
                if query in str(raw.get("dm", "")) or query in str(raw.get("mc", "")):
                    item = adapt_zhitu_index_list_item(raw)
                    self._cache_instrument_name("index", item.symbol, item.name)
                    items.append(item)
        if "fund" in sec_types:
            for raw in self._get_json("/fund/list/all"):
                if query in str(raw.get("dm", "")) or query in str(raw.get("mc", "")):
                    item = adapt_zhitu_fund_list_item(raw)
                    self._cache_instrument_name("fund", item.symbol, item.name)
                    items.append(item)
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
                items = [adapt_zhitu_sector_member_item(item) for item in stocks if isinstance(item, dict)]
                for item in items:
                    self._cache_instrument_name("stock", item.symbol, item.name)
                return items
            return []
        if isinstance(raw, list):
            items = [adapt_zhitu_sector_member_item(item) for item in raw if isinstance(item, dict)]
            for item in items:
                self._cache_instrument_name("stock", item.symbol, item.name)
            return items
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
            quote = adapt_zhitu_quote(raw, normalized, sec_type, exchange="BJ", board="index")
            return self._fill_quote_name(quote, sec_type, normalized)

        if sec_type == "index":
            raw = self._get_json(f"/hz/real/ssjy/{normalized}")
            if isinstance(raw, list):
                raw = raw[0]
            quote = adapt_zhitu_quote(raw, normalized, sec_type, exchange=exchange, board=board)
            return self._fill_quote_name(quote, sec_type, normalized)

        if sec_type == "fund":
            raw = self._get_json(f"/fund/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            quote = adapt_zhitu_quote(raw, normalized, sec_type, exchange=exchange, board="fund")
            return self._fill_quote_name(quote, sec_type, normalized)

        if sec_type == "stock" and normalized.endswith(".BJ"):
            raw = self._get_json(f"/bj/stock/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            quote = adapt_zhitu_quote(raw, normalized, sec_type, exchange="BJ", board="beijing")
            return self._fill_quote_name(quote, sec_type, normalized)

        if sec_type == "stock" and code.startswith("688"):
            raw = self._get_json(f"/tech/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            quote = adapt_zhitu_quote(raw, normalized, sec_type, exchange="SH", board="star")
            return self._fill_quote_name(quote, sec_type, normalized)

        if sec_type == "stock" and exchange in {"SH", "SZ"}:
            raw = self._get_json(f"/hs/real/ssjy/{code}")
            if isinstance(raw, list):
                raw = raw[0]
            if isinstance(raw, dict) and raw.get("error"):
                raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu quote unavailable for {symbol}: {raw.get('error')}", retryable=True)
            quote = adapt_zhitu_quote(raw, normalized, sec_type, exchange=exchange, board=board)
            return self._fill_quote_name(quote, sec_type, normalized)

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
                self._cache_instrument_name("index", symbol, name)
                try:
                    selected.append(self.get_quote(symbol, "index"))
                except Exception:
                    continue
        return {"market": market, "indices": selected, "source": "zhitu"}

    def get_market_pool(self, pool_type: str, trade_date: str | None = None):
        if not trade_date:
            raise ProviderError("INVALID_ARGUMENT", "trade_date is required before calling zhitu market_pool provider", retryable=False)
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

    def get_token_health(self) -> list[dict]:
        now = self._now()
        rows: list[dict] = []
        for token in self.tokens:
            self._ensure_token_state(token)
            stats = self._token_stats[token]
            total = int(stats.get("total_requests", 0) or 0)
            success = int(stats.get("success_count", 0) or 0)
            failures = int(stats.get("failure_count", 0) or 0)
            rate_limits = int(stats.get("rate_limit_count", 0) or 0)
            cooldown_until = float(self._token_cooldowns.get(token, 0) or 0)
            success_rate = (success / total) if total > 0 else None
            rows.append(
                {
                    "token": token,
                    "score": round(self._token_score(token, now), 3),
                    "total_requests": total,
                    "success_count": success,
                    "failure_count": failures,
                    "rate_limit_count": rate_limits,
                    "success_rate": success_rate,
                    "cooldown_until": cooldown_until if cooldown_until > now else None,
                    "cooldown_remaining_seconds": max(0, int(cooldown_until - now)) if cooldown_until > now else 0,
                    "last_success_at": stats.get("last_success_at"),
                    "last_failure_at": stats.get("last_failure_at"),
                    "is_current": token == self.token,
                }
            )
        rows.sort(key=lambda item: item["score"], reverse=True)
        return rows

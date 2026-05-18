from __future__ import annotations

import time
from typing import Any

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
from openclaw_stock_mcp.providers.adapters.zhitu_market_adapters import adapt_zhitu_batch_quote, adapt_zhitu_orderbook, adapt_zhitu_quote
from openclaw_stock_mcp.providers.adapters.zhitu_profile_adapters import (
    adapt_zhitu_dividend,
    adapt_zhitu_profile,
    adapt_zhitu_quarter_profit,
    adapt_zhitu_unlock,
    build_dividend_summary,
    build_unlock_risk,
)
from openclaw_stock_mcp.providers.adapters.zhitu_sector_adapters import adapt_zhitu_sector_quote
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
from openclaw_stock_mcp.app.models.profile import ValuationSnapshot


class ZhituProvider:
    name = "zhitu"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.zhitu_base_url.rstrip("/")
        self.tokens = self.settings.resolve_zhitu_tokens()
        self.token = self.tokens[0] if self.tokens else ""
        self.client = build_http_client(self.settings.zhitu_timeout_seconds)
        self._instrument_name_cache: dict[tuple[str, str], str] = {}
        self._concept_name_map: dict[str, str] | None = None  # display_name -> zhitu_mc
        self._token_cooldowns: dict[str, float] = {}
        self._daily_quota: int = max(int(self.settings.zhitu_daily_quota_per_token or 500), 1)
        self._daily_counters: dict[str, dict[str, int | str]] = {
            token: {"date": "", "count": 0}
            for token in self.tokens
        }
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
        self.last_batch_meta: dict[str, Any] | None = None

    def _now(self) -> float:
        return time.time()

    def _today_str(self) -> str:
        from datetime import date
        return date.today().isoformat()

    def _ensure_daily_counter(self, token: str) -> dict[str, int | str]:
        if token not in self._daily_counters:
            self._daily_counters[token] = {"date": "", "count": 0}
        counter = self._daily_counters[token]
        today = self._today_str()
        if counter["date"] != today:
            counter["date"] = today
            counter["count"] = 0
        return counter

    def _daily_remaining(self, token: str) -> int:
        counter = self._ensure_daily_counter(token)
        return max(0, self._daily_quota - int(counter.get("count", 0)))

    def _increment_daily(self, token: str) -> None:
        counter = self._ensure_daily_counter(token)
        counter["count"] = int(counter.get("count", 0)) + 1

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

        if self._daily_remaining(token) <= 0:
            penalty += 200.0

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
        # If all available tokens have exhausted daily quota, fall back to
        # the full list so we can still try (the upstream may allow some
        # overage or the quota config might be too conservative).
        candidates = available or list(self.tokens)
        with_quota = [t for t in candidates if self._daily_remaining(t) > 0]
        if with_quota:
            candidates = with_quota
        return sorted(candidates, key=lambda token: self._token_score(token, now), reverse=True)

    def _mark_token_rate_limited(self, token: str):
        cooldown_seconds = max(int(getattr(self.settings, "zhitu_token_cooldown_seconds", 60) or 60), 1)
        self._token_cooldowns[token] = self._now() + cooldown_seconds
        self._record_token_failure(token, rate_limited=True)

    def _record_token_success(self, token: str):
        self._ensure_token_state(token)
        self._increment_daily(token)
        stats = self._token_stats[token]
        stats["total_requests"] = int(stats.get("total_requests", 0) or 0) + 1
        stats["success_count"] = int(stats.get("success_count", 0) or 0) + 1
        stats["last_success_at"] = self._now()

    def _record_token_failure(self, token: str, rate_limited: bool = False):
        self._ensure_token_state(token)
        self._increment_daily(token)
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

    def _load_concept_name_map(self) -> dict[str, str]:
        """Build a mapping from user-friendly names to zhitu mc values.

        For a concept like {dm: "101798.BKZS", mc: "GN人工智能"}, the map
        stores both "GN人工智能" -> "GN人工智能" (exact) and
        "人工智能" -> "GN人工智能" (prefix-stripped) so users can type
        just the concept keyword without the GN/TGN prefix.
        """
        if self._concept_name_map is not None:
            return self._concept_name_map

        raw = self._get_json("/hs/list/sectors")
        name_map: dict[str, str] = {}
        for item in raw:
            mc = str(item.get("mc", "")).strip()
            if not mc:
                continue
            # Exact mc → mc (always works)
            name_map[mc] = mc
            # Strip GN/TGN prefix for convenience
            for prefix in ("GN", "TGN"):
                if mc.startswith(prefix):
                    stripped = mc[len(prefix):]
                    if stripped and stripped not in name_map:
                        name_map[stripped] = mc
                    break
        self._concept_name_map = name_map
        return name_map

    def _resolve_concept_name(self, sector_name: str) -> str | None:
        """Resolve a user-supplied sector_name to the zhitu mc value.

        Resolution order:
        1. Exact match in concept name map (includes GN/TGN prefixed names)
        2. Case-insensitive match
        3. Substring match (user input contained in mc, or mc contained in user input)
        Returns None if no match found.
        """
        name_map = self._load_concept_name_map()

        # 1. Exact
        if sector_name in name_map:
            return name_map[sector_name]

        # 2. Case-insensitive
        lower_map = {k.lower(): v for k, v in name_map.items()}
        lower_input = sector_name.lower()
        if lower_input in lower_map:
            return lower_map[lower_input]

        # 3. Substring — prefer shortest mc (most specific), and prefer GN over TGN
        candidates = []
        for key, mc in name_map.items():
            if lower_input in key.lower() or key.lower() in lower_input:
                candidates.append(mc)
        if not candidates:
            return None

        # Deduplicate and prefer GN over TGN, then shortest name
        def _sort_key(m: str) -> tuple:
            is_tgn = m.startswith("TGN")
            return (is_tgn, len(m), m)

        candidates.sort(key=_sort_key)
        return candidates[0]

    def _find_concept_candidates(self, sector_name: str, max_candidates: int = 5) -> list[dict]:
        """Find multiple candidate concepts for an ambiguous name.

        Returns list of {mc, dm} dicts sorted by preference (GN first, shortest first).
        """
        raw = self._get_json("/hs/list/sectors")
        lower_input = sector_name.lower()
        candidates = []
        for item in raw:
            mc = str(item.get("mc", "")).strip()
            dm = str(item.get("dm", "")).strip()
            if not mc:
                continue
            # Match: exact, prefix-stripped, or substring
            stripped = mc
            for prefix in ("GN", "TGN"):
                if mc.startswith(prefix):
                    stripped = mc[len(prefix):]
                    break
            if lower_input == mc.lower() or lower_input == stripped.lower():
                candidates.append({"mc": mc, "dm": dm, "match": "exact"})
            elif lower_input in mc.lower() or lower_input in stripped.lower():
                candidates.append({"mc": mc, "dm": dm, "match": "substring"})

        def _sort_key(c: dict) -> tuple:
            is_tgn = c["mc"].startswith("TGN")
            match_rank = 0 if c["match"] == "exact" else 1
            return (match_rank, is_tgn, len(c["mc"]), c["mc"])

        candidates.sort(key=_sort_key)
        return candidates[:max_candidates]

    def _resolve_primary_sector_name(self, sector_name: str) -> str | None:
        """Resolve a user-friendly primary sector name to a Zhitu-recognized sector identifier."""
        raw = self._get_json("/hs/list/primary")
        lower_input = sector_name.lower()
        candidates: list[dict] = []

        for item in raw:
            mc = str(item.get("mc", "")).strip()
            dm = str(item.get("dm", "")).strip()
            if not mc and not dm:
                continue

            names = [value for value in (mc, dm) if value]
            stripped_names: list[str] = []
            for value in names:
                stripped = value
                for prefix in ("1000SW1", "300SW1", "500SW1", "SW1"):
                    if stripped.startswith(prefix):
                        stripped = stripped[len(prefix):]
                        break
                stripped_names.append(stripped)

            exact = any(lower_input == value.lower() for value in [*names, *stripped_names])
            contains = any(lower_input in value.lower() for value in [*names, *stripped_names])
            if exact or contains:
                candidates.append({
                    "mc": mc,
                    "dm": dm,
                    "match": "exact" if exact else "substring",
                    "is_sw1": mc.startswith("1000SW1") or dm.startswith("1000SW1"),
                })

        if not candidates:
            return None

        def _sort_key(c: dict) -> tuple:
            match_rank = 0 if c["match"] == "exact" else 1
            sw1_rank = 0 if c["is_sw1"] else 1
            mc = c["mc"] or c["dm"]
            return (match_rank, sw1_rank, len(mc), mc)

        candidates.sort(key=_sort_key)
        best = candidates[0]
        return best["mc"] or best["dm"]

    def _find_primary_sector_candidates(self, sector_name: str, max_candidates: int = 5) -> list[dict]:
        raw = self._get_json("/hs/list/primary")
        lower_input = sector_name.lower()
        candidates: list[dict] = []

        for item in raw:
            mc = str(item.get("mc", "")).strip()
            dm = str(item.get("dm", "")).strip()
            if not mc and not dm:
                continue

            names = [value for value in (mc, dm) if value]
            stripped_names: list[str] = []
            for value in names:
                stripped = value
                for prefix in ("1000SW1", "300SW1", "500SW1", "SW1"):
                    if stripped.startswith(prefix):
                        stripped = stripped[len(prefix):]
                        break
                stripped_names.append(stripped)

            exact = any(lower_input == value.lower() for value in [*names, *stripped_names])
            contains = any(lower_input in value.lower() for value in [*names, *stripped_names])
            if exact or contains:
                candidates.append({
                    "mc": mc,
                    "dm": dm,
                    "match": "exact" if exact else "substring",
                })

        def _sort_key(c: dict) -> tuple:
            match_rank = 0 if c["match"] == "exact" else 1
            name = c["mc"] or c["dm"]
            return (match_rank, len(name), name)

        candidates.sort(key=_sort_key)
        return candidates[:max_candidates]

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

            # Concept sector: resolve user-friendly name to zhitu mc value
            if sector_type == "concept":
                resolved_mc = self._resolve_concept_name(sector_name)
                if resolved_mc is None:
                    # No match — try the name as-is (might be a valid mc already)
                    # If that also fails, return empty list with diagnostic info
                    candidates = self._find_concept_candidates(sector_name)
                    if candidates:
                        candidate_names = [c["mc"] for c in candidates[:3]]
                        raise ProviderError(
                            "INVALID_ARGUMENT",
                            f"Concept '{sector_name}' not found. Similar: {', '.join(candidate_names)}",
                            retryable=False,
                        )
                    raise ProviderError(
                        "INVALID_ARGUMENT",
                        f"Concept '{sector_name}' not found in sector list",
                        retryable=False,
                    )
                try:
                    raw = self._get_json(f"/hs/sectors/{resolved_mc}")
                    items = self._extract_sector_children_items(raw)
                    return self._slice_items(items, limit)
                except ProviderError as exc:
                    if "404" in str(exc):
                        # Concept exists in list but has no member data yet
                        return []
                    raise

            # Primary sector: resolve user-friendly name to zhitu-recognized primary identifier
            resolved_primary = self._resolve_primary_sector_name(sector_name)
            if resolved_primary is None:
                candidates = self._find_primary_sector_candidates(sector_name)
                if candidates:
                    candidate_names = [c["mc"] or c["dm"] for c in candidates[:3]]
                    raise ProviderError(
                        "INVALID_ARGUMENT",
                        f"Primary sector '{sector_name}' not found. Similar: {', '.join(candidate_names)}",
                        retryable=False,
                    )
                raise ProviderError(
                    "INVALID_ARGUMENT",
                    f"Primary sector '{sector_name}' not found in primary sector list",
                    retryable=False,
                )

            raw = self._get_json(f"/hs/sectors/{resolved_primary}")
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

    def get_quotes_with_meta(self, symbols: list[str], sec_type: str | None = None) -> tuple[list[Quote], dict[str, Any]]:
        self.last_batch_meta = None
        resolved_sec_type = sec_type or "stock"
        if resolved_sec_type != "stock":
            quotes = [self.get_quote(symbol, resolved_sec_type) for symbol in symbols]
            meta = {
                "batch_attempted": False,
                "batch_failed": False,
                "batch_fallback_used": False,
                "batch_fallback_mode": None,
                "batch_provider": None,
                "batch_error": None,
                "requested_symbols": list(symbols),
                "returned_symbols": [q.symbol for q in quotes],
                "missing_symbols": [],
                "per_symbol": {},
            }
            self.last_batch_meta = meta
            return quotes, meta

        main_board_items = []
        other_symbols = []
        for sym in symbols:
            normalized = normalize_symbol(sym)
            code = normalized.split(".", 1)[0]
            exchange = normalized.split(".", 1)[1] if "." in normalized else None
            is_main_board = exchange in {"SH", "SZ"} and not code.startswith("688") and not normalized.endswith(".BJ")
            if is_main_board:
                main_board_items.append((sym, code, exchange))
            else:
                other_symbols.append(sym)

        results: dict[str, Quote] = {}
        per_symbol_meta: dict[str, dict[str, Any]] = {
            sym: {
                "batch_attempted": False,
                "batch_failed": False,
                "batch_fallback_used": False,
                "batch_fallback_mode": None,
                "batch_provider": None,
                "batch_error": None,
            }
            for sym in symbols
        }
        batch_attempted = False
        batch_failed = False
        batch_fallback_used = False
        batch_error: dict[str, Any] | None = None

        if main_board_items:
            batch_groups = [main_board_items[i : i + 20] for i in range(0, len(main_board_items), 20)]
            for batch in batch_groups:
                batch_attempted = True
                codes = [code for _, code, _ in batch]
                code_to_orig = {code: orig for orig, code, _ in batch}
                exchange_map = {code: ex for _, code, ex in batch}
                requested_batch_symbols = [orig for orig, _, _ in batch]
                for orig_sym in requested_batch_symbols:
                    per_symbol_meta[orig_sym].update({
                        "batch_attempted": True,
                        "batch_provider": self.name,
                    })
                try:
                    raw_list = self._get_json("/hs/public/ssjymore", params={"stock_codes": ",".join(codes)})
                    if isinstance(raw_list, dict):
                        if raw_list.get("error"):
                            raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu batch quote unavailable: {raw_list.get('error')}", retryable=True)
                        raw_list = raw_list.get("data") or raw_list.get("items") or raw_list.get("list") or []
                    if not isinstance(raw_list, list):
                        raise ProviderError("PROVIDER_UNAVAILABLE", "Zhitu batch quote returned unexpected payload", retryable=True)
                    returned_in_batch: set[str] = set()
                    for raw in raw_list:
                        if not isinstance(raw, dict):
                            continue
                        dm = raw.get("dm", "")
                        code = dm[2:] if dm.startswith(("sh", "sz")) else dm
                        if not code:
                            continue
                        exchange = exchange_map.get(code, "SH" if dm.startswith("sh") else "SZ")
                        quote = adapt_zhitu_batch_quote(raw, code, exchange)
                        orig_sym = code_to_orig.get(code, quote.symbol)
                        returned_in_batch.add(orig_sym)
                        results[orig_sym] = quote
                        self._cache_instrument_name("stock", quote.symbol, quote.name)
                    missing_after_batch = [orig for orig, _, _ in batch if orig not in returned_in_batch]
                    if missing_after_batch:
                        batch_failed = True
                        batch_fallback_used = True
                        for orig_sym in missing_after_batch:
                            per_symbol_meta[orig_sym].update({
                                "batch_failed": True,
                                "batch_fallback_used": True,
                                "batch_fallback_mode": "single_quote",
                                "batch_error": {
                                    "error_code": "PARTIAL_RESULT",
                                    "message": "symbol missing from batch response",
                                    "retryable": True,
                                },
                            })
                            try:
                                quote = self.get_quote(orig_sym, "stock")
                                results[orig_sym] = quote
                            except ProviderError:
                                pass
                except Exception as exc:
                    batch_failed = True
                    batch_fallback_used = True
                    if isinstance(exc, ProviderError):
                        batch_error = {"error_code": exc.code, "message": exc.message, "retryable": exc.retryable}
                    else:
                        batch_error = {"error_code": "INTERNAL_ERROR", "message": str(exc), "retryable": False}
                    for orig_sym, _, _ in batch:
                        per_symbol_meta[orig_sym].update({
                            "batch_failed": True,
                            "batch_fallback_used": True,
                            "batch_fallback_mode": "single_quote",
                            "batch_error": batch_error,
                        })
                        try:
                            quote = self.get_quote(orig_sym, "stock")
                            results[orig_sym] = quote
                        except ProviderError:
                            pass

        for sym in other_symbols:
            try:
                quote = self.get_quote(sym, "stock")
                results[sym] = quote
            except ProviderError:
                pass

        ordered: list[Quote] = []
        for sym in symbols:
            if sym in results:
                ordered.append(results[sym])

        meta = {
            "batch_attempted": batch_attempted,
            "batch_failed": batch_failed,
            "batch_fallback_used": batch_fallback_used,
            "batch_fallback_mode": "single_quote" if batch_fallback_used else None,
            "batch_provider": self.name if batch_attempted else None,
            "batch_error": batch_error,
            "requested_symbols": list(symbols),
            "returned_symbols": [q.symbol for q in ordered],
            "missing_symbols": [sym for sym in symbols if sym not in results],
            "per_symbol": per_symbol_meta,
        }
        self.last_batch_meta = meta
        return ordered, meta

    def get_quotes(self, symbols: list[str], sec_type: str | None = None):
        quotes, meta = self.get_quotes_with_meta(symbols, sec_type)
        self.last_batch_meta = meta
        return quotes

    def _map_zhitu_interval(self, interval: str) -> str:
        interval_map = {"5m": "5", "15m": "15", "30m": "30", "60m": "60", "1d": "d", "1w": "w", "1M": "m", "1y": "y"}
        mapped = interval_map.get(interval)
        if not mapped:
            raise ProviderError("UNSUPPORTED_INTERVAL", f"Unsupported interval: {interval}", retryable=False)
        return mapped

    def _map_zhitu_adjust(self, interval: str, adjust: str | None) -> str:
        raw = (adjust or "none").strip().lower()
        alias = {
            "none": "n",
            "n": "n",
            "qfq": "f",
            "f": "f",
            "hfq": "b",
            "b": "b",
            "fr": "fr",
            "br": "br",
        }
        mapped = alias.get(raw)
        if not mapped:
            raise ProviderError("INVALID_ARGUMENT", f"Unsupported adjust: {adjust}", retryable=False)
        if interval in {"5m", "15m", "30m", "60m"}:
            return "n"
        return mapped

    def _build_zhitu_history_params(self, start=None, end=None, limit=None) -> dict:
        params = {}
        if start:
            params["st"] = str(start).replace("-", "")
        if end:
            params["et"] = str(end).replace("-", "")
        if limit:
            params["lt"] = limit
        return params

    def get_history(self, symbol: str, sec_type: str, interval: str, start=None, end=None, limit=None, adjust=None):
        normalized = normalize_symbol(symbol)
        mapped = self._map_zhitu_interval(interval)

        if sec_type == "index":
            params = self._build_zhitu_history_params(start=start, end=end, limit=limit)
            raw = self._get_json(f"/hz/history/fsjy/{normalized}/{mapped}", params=params)
            if isinstance(raw, dict) and raw.get("error"):
                raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu history unavailable for {symbol}: {raw.get('error')}", retryable=True)
            if limit and isinstance(raw, list):
                raw = raw[-limit:]
            return [adapt_zhitu_bar(item) for item in raw]

        if sec_type != "stock":
            raise ProviderError("UNSUPPORTED_SEC_TYPE", "Zhitu history currently supports stock and index routes only", retryable=False)

        adjust_code = self._map_zhitu_adjust(interval, adjust)
        params = self._build_zhitu_history_params(start=start, end=end, limit=limit)
        raw = self._get_json(f"/hs/history/{normalized}/{mapped}/{adjust_code}", params=params)
        if isinstance(raw, dict) and raw.get("error"):
            raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu history unavailable for {symbol}: {raw.get('error')}", retryable=True)
        if limit and isinstance(raw, list):
            raw = raw[-limit:]
        return [adapt_zhitu_bar(item) for item in raw]

    def get_orderbook(self, symbol: str, sec_type: str):
        normalized = normalize_symbol(symbol)
        code = normalized.split(".", 1)[0]
        exchange = normalized.split(".", 1)[1] if "." in normalized else None

        if normalized.endswith(".BJ"):
            raw = self._get_json(f"/bj/stock/real/mmwp/{code}")
        elif code.startswith("688"):
            raw = self._get_json(f"/tech/real/mmwp/{code}")
        elif sec_type == "stock" and exchange in {"SH", "SZ"}:
            raw = self._get_json(f"/hs/real/five/{code}")
        else:
            raise ProviderError("UNSUPPORTED_MARKET", f"Zhitu orderbook route not implemented for {symbol}", retryable=False)

        if isinstance(raw, list):
            raw = raw[0]
        return adapt_zhitu_orderbook(raw, normalized)

    def get_indicator(self, symbol: str, sec_type: str, interval: str, indicator: str, start=None, end=None, limit=None):
        normalized = normalize_symbol(symbol)
        mapped = self._map_zhitu_interval(interval)
        params = self._build_zhitu_history_params(start=start, end=end, limit=limit)

        if sec_type == "index":
            raw = self._get_json(f"/hz/history/{indicator}/{normalized}/{mapped}", params=params)
            if isinstance(raw, dict) and raw.get("error"):
                raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu indicator unavailable for {symbol}: {raw.get('error')}", retryable=True)
            return adapt_zhitu_indicator_series(normalized, sec_type, interval, indicator, raw)

        if sec_type != "stock":
            raise ProviderError("UNSUPPORTED_SEC_TYPE", "Zhitu indicator currently supports stock and index routes only", retryable=False)

        adjust_code = self._map_zhitu_adjust(interval, "none")
        raw = self._get_json(f"/hs/history/{indicator}/{normalized}/{mapped}/{adjust_code}", params=params)
        if isinstance(raw, dict) and raw.get("error"):
            raise ProviderError("PROVIDER_UNAVAILABLE", f"Zhitu indicator unavailable for {symbol}: {raw.get('error')}", retryable=True)
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
            daily_used = int(self._ensure_daily_counter(token).get("count", 0))
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
                    "daily_quota": self._daily_quota,
                    "daily_used": daily_used,
                    "daily_remaining": max(0, self._daily_quota - daily_used),
                }
            )
        rows.sort(key=lambda item: item["score"], reverse=True)
        return rows

    def get_profile(self, symbol: str, include: list[str] | None = None):
        from openclaw_stock_mcp.app.models.profile import StockProfile, StockProfileDetail

        normalized = normalize_symbol(symbol)
        code = normalized.split(".", 1)[0]
        include = include or ["profile", "dividends", "unlocks", "profits", "valuation"]

        profile = None
        dividends = []
        unlocks = []
        quarter_profits = []
        valuation = None

        if "profile" in include:
            raw = self._get_json(f"/hs/gs/gsjj/{code}")
            if isinstance(raw, list) and raw:
                raw = raw[0]
            profile = adapt_zhitu_profile(raw, normalized)

        if "dividends" in include:
            raw = self._get_json(f"/hs/gs/jnff/{code}")
            dividends = [adapt_zhitu_dividend(item) for item in raw if isinstance(item, dict)]

        if "unlocks" in include:
            raw = self._get_json(f"/hs/gs/jjxs/{code}")
            unlocks = [adapt_zhitu_unlock(item) for item in raw if isinstance(item, dict)]

        if "profits" in include:
            raw = self._get_json(f"/hs/gs/jdlr/{code}")
            quarter_profits = [adapt_zhitu_quarter_profit(item) for item in raw if isinstance(item, dict)]

        if "valuation" in include:
            quote = self.get_quote(normalized, "stock")
            valuation = ValuationSnapshot(
                price=quote.price,
                pe=quote.pe,
                pb=quote.pb,
                market_cap=quote.market_cap,
                float_market_cap=quote.float_market_cap,
                source=quote.source,
            )

        dividend_summary = build_dividend_summary(dividends) if dividends else None
        unlock_risk = build_unlock_risk(unlocks) if unlocks else None

        return StockProfileDetail(
            profile=profile or StockProfile(symbol=normalized, source="zhitu"),
            dividends=dividends,
            unlocks=unlocks,
            quarter_profits=quarter_profits,
            valuation=valuation,
            dividend_summary=dividend_summary,
            unlock_risk=unlock_risk,
            source="zhitu",
        )

    def get_sector_quote(self, symbol: str, sector_type: str | None = None):
        normalized = normalize_symbol(symbol)
        raw = self._get_json(f"/hz/real/ssjy/{normalized}")
        if isinstance(raw, list):
            raw = raw[0]
        return adapt_zhitu_sector_quote(raw, normalized, sector_type)

    def get_sector_quotes(self, symbols: list[str], sector_type: str | None = None):
        return [self.get_sector_quote(symbol, sector_type) for symbol in symbols]

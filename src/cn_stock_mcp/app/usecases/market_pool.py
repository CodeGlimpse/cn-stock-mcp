from datetime import datetime

from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.errors import ProviderError


class MarketPoolUseCase:
    _shared_pool_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if MarketPoolUseCase._shared_pool_cache is None:
            MarketPoolUseCase._shared_pool_cache = CacheService(
                maxsize=256, ttl=max(int(settings.cache_ttl_pool_seconds or 600), 10)
            )
        self.pool_cache = MarketPoolUseCase._shared_pool_cache

    def _annotate_anomalies(self, items: list[dict] | list) -> list:
        for item in items:
            extra = getattr(item, "extra", None)
            if not isinstance(extra, dict):
                continue

            anomaly_flags: list[str] = []
            if getattr(item, "price", None) == 0:
                anomaly_flags.append("zero_price")
            if getattr(item, "turnover", None) == 0:
                anomaly_flags.append("zero_turnover")
            if getattr(item, "market_cap", None) == 0:
                anomaly_flags.append("zero_market_cap")
            if getattr(item, "float_market_cap", None) == 0:
                anomaly_flags.append("zero_float_market_cap")

            if anomaly_flags:
                extra["anomaly_flags"] = anomaly_flags
                extra["data_quality"] = "suspect"
            else:
                extra.setdefault("data_quality", "normal")
        return items

    def _resolve_effective_trade_date(self, requested_trade_date: str | None) -> tuple[str, dict]:
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
            "recent_trading_days": calendar.get("recent_trading_days", []),
            "source": calendar.get("source"),
        }

    @staticmethod
    def _limit_cached_result(cached: dict, limit: int | None) -> dict:
        items = cached["items"]
        if limit:
            items = items[:limit]
        result = {
            **cached,
            "items": items,
        }
        if "count" in result:
            result["count"] = len(items)
        return result

    def execute(self, request):
        requested_trade_date = getattr(request, "trade_date", None)

        # An explicit date can be looked up without consulting the trading
        # calendar first. This keeps a valid cache hit offline and avoids an
        # unnecessary upstream call for every repeated historical request.
        if requested_trade_date:
            requested_cache_key = f"pool:{request.pool_type}:{requested_trade_date}"
            cached = self.pool_cache.get(requested_cache_key)
            if cached is not None:
                return self._limit_cached_result(cached, request.limit)

        effective_trade_date, calendar_meta = self._resolve_effective_trade_date(getattr(request, "trade_date", None))

        cache_key = f"pool:{request.pool_type}:{effective_trade_date}"
        cached = self.pool_cache.get(cache_key)
        if cached is not None:
            return self._limit_cached_result(cached, request.limit)

        selection = self.router.choose_provider(
            tool_name="market_pool",
            sec_type="stock",
            preferred=(getattr(request, "provider", None) or "zhitu"),
        )
        items, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_market_pool(
                pool_type=request.pool_type,
                trade_date=effective_trade_date,
            ),
        )
        items = self._annotate_anomalies(items)
        # Cache the full result before applying limit
        cached_result = {
            "pool_type": request.pool_type,
            "trade_date": effective_trade_date,
            "requested_trade_date": calendar_meta["requested_trade_date"],
            "items": items,
            "count": len(items),
            "source": fallback_meta.final_provider or selection.primary,
            "meta": {
                "selected_primary": fallback_meta.selected_primary,
                "selected_fallback": fallback_meta.selected_fallback,
                "attempted": fallback_meta.attempted,
                "final_provider": fallback_meta.final_provider,
                "used_fallback": fallback_meta.used_fallback,
                "calendar": calendar_meta,
            },
        }
        self.pool_cache.set(cache_key, cached_result)
        if requested_trade_date and requested_trade_date != effective_trade_date:
            self.pool_cache.set(
                f"pool:{request.pool_type}:{requested_trade_date}",
                cached_result,
            )
        return self._limit_cached_result(cached_result, request.limit)

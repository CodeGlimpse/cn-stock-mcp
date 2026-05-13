from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.infra.config import get_settings


class MarketOverviewUseCase:
    _shared_overview_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        settings = get_settings()
        if MarketOverviewUseCase._shared_overview_cache is None:
            MarketOverviewUseCase._shared_overview_cache = CacheService(
                maxsize=64, ttl=max(int(settings.cache_ttl_overview_seconds or 10), 1)
            )
        self.overview_cache = MarketOverviewUseCase._shared_overview_cache

    def execute(self, request):
        cache_key = f"overview:{request.market}"
        cached = self.overview_cache.get(cache_key)
        if cached is not None:
            return cached

        selection = self.router.choose_provider(
            tool_name="market_overview",
            sec_type="index",
            preferred=(None if request.provider == "mixed" else request.provider),
        )
        result, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_market_overview(request.market),
        )
        payload = result if isinstance(result, dict) else {"data": result}
        payload.setdefault("meta", {})
        payload["meta"].update(
            {
                "selected_primary": fallback_meta.selected_primary,
                "selected_fallback": fallback_meta.selected_fallback,
                "attempted": fallback_meta.attempted,
                "final_provider": fallback_meta.final_provider,
                "used_fallback": fallback_meta.used_fallback,
            }
        )
        payload["source"] = fallback_meta.final_provider or selection.primary
        self.overview_cache.set(cache_key, payload)
        return payload

from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.infra.config import get_settings


class OrderbookUseCase:
    _shared_orderbook_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()
        settings = get_settings()
        if OrderbookUseCase._shared_orderbook_cache is None:
            OrderbookUseCase._shared_orderbook_cache = CacheService(
                maxsize=2048, ttl=max(int(settings.cache_ttl_orderbook_seconds or 3), 1)
            )
        self.orderbook_cache = OrderbookUseCase._shared_orderbook_cache

    def execute(self, request):
        resolved = self.resolver.resolve(request.symbol, request.sec_type)
        cache_key = f"orderbook:{resolved.symbol}:{resolved.sec_type}"
        cached = self.orderbook_cache.get(cache_key)
        if cached is not None:
            return cached

        selection = self.router.choose_provider(
            tool_name="stock_orderbook",
            symbol=resolved.symbol,
            sec_type=resolved.sec_type,
            preferred=getattr(request, "provider", None),
        )
        result, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_orderbook(
                symbol=resolved.symbol,
                sec_type=resolved.sec_type,
            ),
        )
        payload = result.model_dump() if hasattr(result, "model_dump") else result
        if isinstance(payload, dict):
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
        self.orderbook_cache.set(cache_key, payload)
        return payload

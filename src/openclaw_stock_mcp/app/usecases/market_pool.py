from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter


class MarketPoolUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request):
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
                trade_date=request.trade_date,
            ),
        )
        if request.limit:
            items = items[: request.limit]
        return {
            "pool_type": request.pool_type,
            "trade_date": request.trade_date,
            "items": items,
            "count": len(items),
            "source": fallback_meta.final_provider or selection.primary,
            "meta": {
                "selected_primary": fallback_meta.selected_primary,
                "selected_fallback": fallback_meta.selected_fallback,
                "attempted": fallback_meta.attempted,
                "final_provider": fallback_meta.final_provider,
                "used_fallback": fallback_meta.used_fallback,
            },
        }

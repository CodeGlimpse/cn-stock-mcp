from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter


class StockSearchUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request):
        selection = self.router.choose_provider(
            tool_name="stock_search",
            sec_type=None,
            preferred=getattr(request, "provider", None),
        )
        result, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.search_instruments(
                query=request.query,
                sec_types=request.sec_types,
                market=request.market,
                limit=request.limit,
            ),
        )
        return {
            "items": result,
            "total": len(result),
            "source": fallback_meta.final_provider or selection.primary,
            "meta": {
                "selected_primary": fallback_meta.selected_primary,
                "selected_fallback": fallback_meta.selected_fallback,
                "attempted": fallback_meta.attempted,
                "final_provider": fallback_meta.final_provider,
                "used_fallback": fallback_meta.used_fallback,
            },
        }

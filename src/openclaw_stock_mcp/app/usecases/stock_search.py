from openclaw_stock_mcp.app.services.fallback import run_with_fallback
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
        result = run_with_fallback(
            self.router,
            selection,
            lambda provider: provider.search_instruments(
                query=request.query,
                sec_types=request.sec_types,
                market=request.market,
                limit=request.limit,
            ),
        )
        source = selection.primary
        return {
            "items": result,
            "total": len(result),
            "source": source,
        }

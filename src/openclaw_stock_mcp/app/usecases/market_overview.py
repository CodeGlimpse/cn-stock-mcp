from openclaw_stock_mcp.app.services.fallback import run_with_fallback
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter


class MarketOverviewUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request):
        selection = self.router.choose_provider(
            tool_name="market_overview",
            sec_type="index",
            preferred=(None if request.provider == "mixed" else request.provider),
        )
        return run_with_fallback(
            self.router,
            selection,
            lambda provider: provider.get_market_overview(request.market),
        )

from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
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
        return payload

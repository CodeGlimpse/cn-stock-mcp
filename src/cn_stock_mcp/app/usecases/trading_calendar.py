from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_router import ProviderRouter


class TradingCalendarUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request):
        selection = self.router.choose_provider(
            tool_name="trading_calendar",
            preferred=getattr(request, "provider", None),
        )
        result, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_trading_calendar(
                market=request.market,
                date=request.date,
                start_date=request.start_date,
                end_date=request.end_date,
                recent_limit=request.recent_limit,
            ),
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

from openclaw_stock_mcp.app.services.fallback import run_with_fallback
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver


class TechnicalIndicatorUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request):
        resolved = self.resolver.resolve(request.symbol, request.sec_type)
        selection = self.router.choose_provider(
            tool_name="technical_indicator",
            symbol=resolved.symbol,
            sec_type=resolved.sec_type,
            preferred=getattr(request, "provider", None),
        )
        return run_with_fallback(
            self.router,
            selection,
            lambda provider: provider.get_indicator(
                symbol=resolved.symbol,
                sec_type=resolved.sec_type,
                interval=request.interval,
                indicator=request.indicator,
                start=request.start_date,
                end=request.end_date,
                limit=request.limit,
            ),
        )

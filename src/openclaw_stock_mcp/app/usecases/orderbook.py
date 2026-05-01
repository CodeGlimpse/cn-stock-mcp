from openclaw_stock_mcp.app.services.fallback import run_with_fallback
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver


class OrderbookUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request):
        resolved = self.resolver.resolve(request.symbol, request.sec_type)
        selection = self.router.choose_provider(
            tool_name="stock_orderbook",
            symbol=resolved.symbol,
            sec_type=resolved.sec_type,
            preferred=getattr(request, "provider", None),
        )
        result = run_with_fallback(
            self.router,
            selection,
            lambda provider: provider.get_orderbook(
                symbol=resolved.symbol,
                sec_type=resolved.sec_type,
            ),
        )
        return result

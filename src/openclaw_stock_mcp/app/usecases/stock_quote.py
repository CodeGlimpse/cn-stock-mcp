from openclaw_stock_mcp.app.services.fallback import run_with_fallback
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver


class StockQuoteUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request):
        items = []
        errors = []
        for raw_symbol in request.symbols:
            resolved = self.resolver.resolve(raw_symbol, request.sec_type)
            selection = self.router.choose_provider(
                tool_name="stock_quote",
                symbol=resolved.symbol,
                sec_type=resolved.sec_type,
                preferred=getattr(request, "provider", None),
            )
            try:
                quote = run_with_fallback(
                    self.router,
                    selection,
                    lambda provider: provider.get_quote(resolved.symbol, resolved.sec_type),
                )
                items.append(quote)
            except Exception as exc:
                errors.append({"symbol": raw_symbol, "error": str(exc)})
        return {
            "items": items,
            "partial_failure": len(errors) > 0,
            "errors": errors,
        }

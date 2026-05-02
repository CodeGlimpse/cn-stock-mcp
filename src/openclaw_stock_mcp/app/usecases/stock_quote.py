from openclaw_stock_mcp.app.services.fallback import run_with_fallback
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.provider_types import ProviderSelection
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver


class StockQuoteUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def _selection_from_preference(self, preferences: list[str] | None) -> ProviderSelection | None:
        if not preferences:
            return None
        ordered = [p for p in preferences if p in {"akshare", "zhitu"}]
        if not ordered:
            return None
        primary = ordered[0]
        fallback = [p for p in ordered[1:] if p != primary]
        return ProviderSelection(primary=primary, fallback=fallback)

    def execute(self, request):
        items = []
        errors = []
        forced_selection = self._selection_from_preference(getattr(request, "provider_preference", None))

        for raw_symbol in request.symbols:
            resolved = self.resolver.resolve(raw_symbol, request.sec_type)
            selection = forced_selection or self.router.choose_provider(
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

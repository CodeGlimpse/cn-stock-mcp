from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
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
        meta_items = []
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
                quote, fallback_meta = run_with_fallback_meta(
                    self.router,
                    selection,
                    lambda provider: provider.get_quote(resolved.symbol, resolved.sec_type),
                )
                items.append(quote)
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": resolved.symbol,
                        "sec_type": resolved.sec_type,
                        "selected_primary": fallback_meta.selected_primary,
                        "selected_fallback": fallback_meta.selected_fallback,
                        "attempted": fallback_meta.attempted,
                        "final_provider": fallback_meta.final_provider,
                        "used_fallback": fallback_meta.used_fallback,
                    }
                )
            except Exception as exc:
                errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": resolved.symbol,
                        "sec_type": resolved.sec_type,
                        "selected_primary": selection.primary,
                        "selected_fallback": selection.fallback,
                        "attempted": [selection.primary, *selection.fallback],
                        "final_provider": None,
                        "used_fallback": False,
                    }
                )
        return {
            "items": items,
            "partial_failure": len(errors) > 0,
            "errors": errors,
            "meta": {
                "per_symbol": meta_items,
            },
        }

from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.provider_types import ProviderSelection
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.providers.errors import ProviderError


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

    def _validate_symbol_sec_type(self, raw_symbol: str, requested_sec_type: str | None):
        if not requested_sec_type:
            return
        inferred_sec_type = self.resolver.infer_sec_type(raw_symbol)
        if inferred_sec_type != requested_sec_type:
            raise ProviderError(
                "INVALID_ARGUMENT",
                f"Symbol {raw_symbol} is inferred as {inferred_sec_type}, which conflicts with requested sec_type={requested_sec_type}",
                retryable=False,
            )

    def execute(self, request):
        items = []
        errors = []
        meta_items = []
        forced_selection = self._selection_from_preference(getattr(request, "provider_preference", None))

        for raw_symbol in request.symbols:
            try:
                self._validate_symbol_sec_type(raw_symbol, request.sec_type)
                resolved = self.resolver.resolve(raw_symbol, request.sec_type)
                selection = forced_selection or self.router.choose_provider(
                    tool_name="stock_quote",
                    symbol=resolved.symbol,
                    sec_type=resolved.sec_type,
                    preferred=getattr(request, "provider", None),
                )
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
                try:
                    resolved = self.resolver.resolve(raw_symbol, request.sec_type)
                    resolved_symbol = resolved.symbol
                    resolved_sec_type = resolved.sec_type
                except Exception:
                    resolved_symbol = raw_symbol
                    resolved_sec_type = request.sec_type
                selection = forced_selection or self.router.choose_provider(
                    tool_name="stock_quote",
                    symbol=resolved_symbol,
                    sec_type=resolved_sec_type,
                    preferred=getattr(request, "provider", None),
                )
                errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": resolved_symbol,
                        "sec_type": resolved_sec_type,
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

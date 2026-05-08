from __future__ import annotations

from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver


class SectorQuoteUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request):
        items = []
        errors = []
        meta_items = []

        for raw_symbol in request.symbols:
            try:
                resolved = self.resolver.resolve(raw_symbol, "sector")
                selection = self.router.choose_provider(
                    tool_name="sector_quote",
                    symbol=resolved.symbol,
                    sec_type="sector",
                    preferred=getattr(request, "provider", None),
                )
                quote, fallback_meta = run_with_fallback_meta(
                    self.router,
                    selection,
                    lambda provider: provider.get_sector_quote(resolved.symbol, getattr(request, "sector_type", None)),
                )
                items.append(quote)
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": resolved.symbol,
                        "selected_primary": fallback_meta.selected_primary,
                        "selected_fallback": fallback_meta.selected_fallback,
                        "attempted": fallback_meta.attempted,
                        "final_provider": fallback_meta.final_provider,
                        "used_fallback": fallback_meta.used_fallback,
                    }
                )
            except Exception as exc:
                from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
                errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": None,
                        "selected_primary": None,
                        "selected_fallback": None,
                        "attempted": [],
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

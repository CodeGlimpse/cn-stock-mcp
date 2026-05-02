from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
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
        result, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_orderbook(
                symbol=resolved.symbol,
                sec_type=resolved.sec_type,
            ),
        )
        payload = result.model_dump() if hasattr(result, "model_dump") else result
        if isinstance(payload, dict):
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

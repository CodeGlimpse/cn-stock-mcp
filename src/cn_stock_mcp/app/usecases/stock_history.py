import time

from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.app.services.symbol_resolver import SymbolResolver


class StockHistoryUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request):
        started_at = time.perf_counter()
        resolved = self.resolver.resolve(request.symbol, request.sec_type)
        selection = self.router.choose_provider(
            tool_name="stock_history",
            symbol=resolved.symbol,
            sec_type=resolved.sec_type,
            preferred=getattr(request, "provider", None),
        )
        items, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_history(
                symbol=resolved.symbol,
                sec_type=resolved.sec_type,
                interval=request.interval,
                start=request.start_date,
                end=request.end_date,
                limit=request.limit,
                adjust=request.adjust,
            ),
        )
        provider_used = fallback_meta.final_provider or selection.primary
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        meta = {
            "selected_primary": fallback_meta.selected_primary,
            "selected_fallback": fallback_meta.selected_fallback,
            "attempted": fallback_meta.attempted,
            "final_provider": fallback_meta.final_provider,
            "used_fallback": fallback_meta.used_fallback,
            "provider_used": provider_used,
            "fallback_chain": [selection.primary, *selection.fallback],
            "latency_ms": latency_ms,
        }

        if resolved.sec_type == "stock" and request.interval in {"1w", "1M"}:
            meta.update(
                {
                    "derived_from": "1d",
                    "aggregation": "calendar_week" if request.interval == "1w" else "calendar_month",
                    "limit_applied_after_aggregation": True,
                    "partial_period_at_range_edges": bool(request.start_date or request.end_date),
                }
            )

        return {
            "symbol": resolved.symbol,
            "sec_type": resolved.sec_type,
            "interval": request.interval,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "adjust": request.adjust,
            "items": items,
            "count": len(items),
            "source": provider_used,
            "meta": meta,
        }

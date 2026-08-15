from __future__ import annotations

import time

from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.app.services.symbol_resolver import SymbolResolver


class StockProfileUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request):
        started_at = time.perf_counter()
        resolved = self.resolver.resolve(request.symbol, "stock")
        selection = self.router.choose_provider(
            tool_name="stock_profile",
            symbol=resolved.symbol,
            sec_type="stock",
            preferred=getattr(request, "provider", None),
        )

        include = getattr(request, "include", None) or ["profile", "dividends", "unlocks", "profits"]

        profile, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_profile(resolved.symbol, include=include),
        )

        return {
            "symbol": request.symbol,
            "resolved_symbol": resolved.symbol,
            "profile": profile.profile.model_dump(),
            "dividends": [d.model_dump() for d in profile.dividends],
            "unlocks": [u.model_dump() for u in profile.unlocks],
            "quarter_profits": [p.model_dump() for p in profile.quarter_profits],
            "valuation": profile.valuation.model_dump() if profile.valuation else None,
            "dividend_summary": profile.dividend_summary,
            "unlock_risk": profile.unlock_risk,
            "source": profile.source,
            "meta": {
                "selected_primary": fallback_meta.selected_primary,
                "selected_fallback": fallback_meta.selected_fallback,
                "attempted": fallback_meta.attempted,
                "final_provider": fallback_meta.final_provider,
                "used_fallback": fallback_meta.used_fallback,
                "provider_used": fallback_meta.final_provider or selection.primary,
                "fallback_chain": [selection.primary, *selection.fallback],
                "latency_ms": int((time.perf_counter() - started_at) * 1000),
                "include": include,
            },
        }

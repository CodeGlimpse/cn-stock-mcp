from __future__ import annotations

from openclaw_stock_mcp.app.models.industry_valuation_rank import IndustryValuationRankResult
from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.industry_valuation_rank_adapters import (
    build_sector_item,
    rank_items,
    build_summary,
    build_summary_text,
)


class IndustryValuationRankUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        sector_names = request.sector_names
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n
        member_limit = request.member_limit

        selection = self.router.choose_provider(tool_name="sector_lookup", preferred="zhitu")

        items = []
        quote_provider_sel = self.router.choose_provider(tool_name="stock_quote", sec_type="stock", preferred="zhitu")

        for name in sector_names:
            members, _ = run_with_fallback_meta(
                self.router,
                selection,
                lambda provider: provider.get_sector_lookup(mode="children", sector_type="primary", sector_name=name, limit=member_limit),
            )
            symbols = [m.symbol for m in members if getattr(m, "symbol", None)]
            if not symbols:
                items.append(build_sector_item(name, [], []))
                continue

            quotes, _ = run_with_fallback_meta(
                self.router,
                quote_provider_sel,
                lambda provider: provider.get_quotes(symbols=symbols, sec_type="stock"),
            )
            items.append(build_sector_item(name, symbols, quotes))

        items = rank_items(items, sort_by=sort_by, descending=descending)
        if top_n:
            items = items[:top_n]

        summary = build_summary(items)
        summary_text = build_summary_text(summary)

        result = IndustryValuationRankResult(
            sector_type="primary",
            items=items,
            summary=summary,
            source="zhitu+stock_quote",
        )
        payload = result.model_dump()
        payload["summary_text"] = summary_text
        return payload

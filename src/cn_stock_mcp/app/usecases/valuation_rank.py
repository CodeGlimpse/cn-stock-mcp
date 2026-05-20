from __future__ import annotations

from cn_stock_mcp.app.models.valuation_rank import StockValuationItem, ValuationRankResult
from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.providers.adapters.akshare_valuation_rank_adapters import (
    build_market_valuation_snapshot,
    build_valuation_summary,
    build_valuation_summary_text,
    rank_stock_valuation_items,
)


class ValuationRankUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def _fetch_market_snapshot_rows(self):
        ak = self.router.get_provider("akshare")

        # latest rows from market-level valuation series
        pe_df = ak._call_ak_quietly(ak._require_ak().stock_a_ttm_lyr)
        pb_df = ak._call_ak_quietly(ak._require_ak().stock_a_all_pb)
        dy_df = ak._call_ak_quietly(ak._require_ak().stock_a_gxl_lg)
        hl_df = ak._call_ak_quietly(ak._require_ak().stock_a_high_low_statistics)

        pe_row = pe_df.to_dict(orient="records")[-1] if len(pe_df) > 0 else None
        pb_row = pb_df.to_dict(orient="records")[-1] if len(pb_df) > 0 else None
        dy_row = dy_df.to_dict(orient="records")[-1] if len(dy_df) > 0 else None
        hl_row = hl_df.to_dict(orient="records")[-1] if len(hl_df) > 0 else None

        return pe_row, pb_row, dy_row, hl_row

    def execute(self, request) -> dict:
        symbols = request.symbols
        sec_type = getattr(request, "sec_type", "stock")
        sort_by = getattr(request, "sort_by", "pe")
        descending = getattr(request, "descending", False)
        top_n = getattr(request, "top_n", None)

        # 1) market snapshot
        pe_row, pb_row, dy_row, hl_row = self._fetch_market_snapshot_rows()
        market_snapshot = build_market_valuation_snapshot(pe_row, pb_row, dy_row, hl_row)

        # 2) stock-level valuation from stock_quote (zhitu primary, akshare fallback)
        selection = self.router.choose_provider(
            tool_name="stock_quote",
            sec_type=sec_type,
            preferred=(getattr(request, "provider", None) or "zhitu"),
        )
        quotes, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_quotes(symbols=symbols, sec_type=sec_type),
        )

        items: list[StockValuationItem] = []
        for q in quotes:
            items.append(
                StockValuationItem(
                    symbol=q.symbol,
                    name=q.name,
                    pe=q.pe,
                    pb=q.pb,
                    market_cap=q.market_cap,
                    float_market_cap=q.float_market_cap,
                    source=q.source,
                )
            )

        items = rank_stock_valuation_items(items, sort_by=sort_by, descending=descending)
        if top_n:
            items = items[:top_n]

        summary = build_valuation_summary(items, market_snapshot)
        summary_text = build_valuation_summary_text(summary, market_snapshot)

        result = ValuationRankResult(
            market=market_snapshot,
            items=items,
            summary=summary,
            source=f"market:akshare,stock:{fallback_meta.final_provider or selection.primary}",
        )

        payload = result.model_dump()
        payload["summary_text"] = summary_text
        payload["meta"] = {
            "selected_primary": fallback_meta.selected_primary,
            "selected_fallback": fallback_meta.selected_fallback,
            "attempted": fallback_meta.attempted,
            "final_provider": fallback_meta.final_provider,
            "used_fallback": fallback_meta.used_fallback,
        }
        return payload

from __future__ import annotations

from openclaw_stock_mcp.app.models.etf_snapshot import ETFSnapshotResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_etf_snapshot_adapters import (
    adapt_etf_nav_row,
    adapt_etf_scale_row,
    adapt_etf_spot_row,
    build_etf_snapshot_summary_text,
)


class ETFSnapshotUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = request.include
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n
        min_discount = request.min_discount
        max_discount = request.max_discount
        history_n = request.history_n

        provider = self.router.get_provider("akshare")

        spot = []
        scale = []
        nav = []

        if "spot" in include:
            rows = provider.get_etf_spot_em()
            spot = [adapt_etf_spot_row(r) for r in rows]

            # Filter by discount rate
            if min_discount is not None:
                spot = [s for s in spot if s.discount_rate is not None and s.discount_rate >= min_discount]
            if max_discount is not None:
                spot = [s for s in spot if s.discount_rate is not None and s.discount_rate <= max_discount]

            # Sort
            spot = self._sort_items(spot, sort_by, descending)
            if top_n:
                spot = spot[:top_n]

        if "scale" in include:
            rows = provider.get_etf_scale_sse()
            scale = [adapt_etf_scale_row(r) for r in rows]
            # If symbol specified, filter
            if request.symbol:
                raw_code = getattr(request, "_raw_code", None) or request.symbol.split(".")[0]
                scale = [s for s in scale if s.symbol.startswith(raw_code) or s.name and raw_code in s.symbol]

        if "nav" in include and request.symbol:
            raw_code = getattr(request, "_raw_code", None) or request.symbol.split(".")[0]
            rows = provider.get_etf_nav(fund=raw_code)
            nav_items = [adapt_etf_nav_row(r) for r in rows]
            nav = nav_items[-history_n:]

        summary = build_etf_snapshot_summary_text(spot, scale, nav)

        result = ETFSnapshotResult(
            spot=spot,
            spot_count=len(spot),
            scale=scale,
            scale_count=len(scale),
            nav=nav,
            nav_count=len(nav),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        """Sort spot items by a given attribute."""
        key_map = {
            "turnover": "turnover",
            "change_percent": "change_percent",
            "discount_rate": "discount_rate",
            "main_net_inflow": "main_net_inflow",
            "volume": "volume",
            "total_market_cap": "total_market_cap",
        }
        attr = key_map.get(key, "turnover")

        def _get_val(item):
            v = getattr(item, attr, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

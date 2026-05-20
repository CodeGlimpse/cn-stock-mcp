from __future__ import annotations

from cn_stock_mcp.app.models.convertible_bond import ConvertibleBondResult
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.providers.adapters.akshare_convertible_bond_adapters import (
    adapt_cb_index_row,
    adapt_cb_redeem_row,
    adapt_cb_spot_row,
    build_cb_summary_text,
)


class ConvertibleBondUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = request.include
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n
        max_conv_premium = request.max_conv_premium
        min_ytm = request.min_ytm
        min_double_low = request.min_double_low
        max_double_low = request.max_double_low
        call_status_filter = request.call_status_filter
        history_n = request.history_n

        provider = self.router.get_provider("akshare")

        spot = []
        redeem = []
        index = []

        if "spot" in include:
            rows = provider.get_cb_spot()
            spot = [adapt_cb_spot_row(r) for r in rows]

            # Filter
            if max_conv_premium is not None:
                spot = [s for s in spot if s.conv_premium is not None and s.conv_premium <= max_conv_premium]
            if min_ytm is not None:
                spot = [s for s in spot if s.ytm is not None and s.ytm >= min_ytm]
            if min_double_low is not None:
                spot = [s for s in spot if s.double_low is not None and s.double_low >= min_double_low]
            if max_double_low is not None:
                spot = [s for s in spot if s.double_low is not None and s.double_low <= max_double_low]

            # Sort
            spot = self._sort_items(spot, sort_by, descending)
            if top_n:
                spot = spot[:top_n]

        if "redeem" in include:
            rows = provider.get_cb_redeem()
            redeem = [adapt_cb_redeem_row(r) for r in rows]

            # Filter by call status
            if call_status_filter == "called":
                redeem = [r for r in redeem if r.call_status and "已公告" in r.call_status]
            elif call_status_filter == "near_call":
                redeem = [r for r in redeem if r.call_status and "接近" in r.call_status]
            elif call_status_filter == "safe":
                redeem = [r for r in redeem if not r.call_status or ("已公告" not in r.call_status and "接近" not in r.call_status)]

            if top_n:
                redeem = redeem[:top_n]

        if "index" in include:
            rows = provider.get_cb_index()
            index_items = [adapt_cb_index_row(r) for r in rows]
            index = index_items[-history_n:]

        summary = build_cb_summary_text(spot, redeem, index)

        result = ConvertibleBondResult(
            spot=spot,
            spot_count=len(spot),
            redeem=redeem,
            redeem_count=len(redeem),
            index=index,
            index_count=len(index),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        """Sort spot items by a given attribute."""
        key_map = {
            "double_low": "double_low",
            "conv_premium": "conv_premium",
            "ytm": "ytm",
            "change_percent": "change_percent",
            "turnover": "turnover",
            "remaining_years": "remaining_years",
        }
        attr = key_map.get(key, "double_low")

        def _get_val(item):
            v = getattr(item, attr, None)
            if v is None:
                return float("inf") if not descending else float("-inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

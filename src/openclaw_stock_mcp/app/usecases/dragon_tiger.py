from __future__ import annotations

from openclaw_stock_mcp.app.models.dragon_tiger import DragonTigerResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_dragon_tiger_adapters import (
    adapt_active_broker_row,
    adapt_broker_rank_row,
    adapt_daily_detail_row,
    adapt_institution_row,
    adapt_stock_stat_row,
    build_dragon_tiger_summary_text,
)


class DragonTigerUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = request.include
        trade_date = request.trade_date
        start_date = getattr(request, "start_date", None)
        end_date = getattr(request, "end_date", None)
        period = request.period
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        daily_detail = []
        institution = []
        active_broker = []
        broker_rank = []
        stock_stat = []

        # A类: date-range queries
        if "daily_detail" in include:
            rows = provider.get_dragon_tiger_daily(start_date or trade_date, end_date or trade_date)
            daily_detail = [adapt_daily_detail_row(r) for r in rows]

        if "institution" in include:
            rows = provider.get_dragon_tiger_institution(start_date or trade_date, end_date or trade_date)
            institution = [adapt_institution_row(r) for r in rows]

        if "active_broker" in include:
            rows = provider.get_dragon_tiger_active_broker(start_date or trade_date, end_date or trade_date)
            active_broker = [adapt_active_broker_row(r) for r in rows]

        # B类: period-based statistics
        if "broker_rank" in include:
            rows = provider.get_dragon_tiger_broker_rank(period=period)
            broker_rank = [adapt_broker_rank_row(r) for r in rows]

        if "stock_stat" in include:
            rows = provider.get_dragon_tiger_stock_stat(period=period)
            stock_stat = [adapt_stock_stat_row(r) for r in rows]

        # Sort daily_detail and institution by sort_by
        if daily_detail:
            daily_detail = self._sort_items(daily_detail, sort_by, descending)
            if top_n:
                daily_detail = daily_detail[:top_n]

        if institution:
            inst_sort_map = {
                "net_buy_amount": "inst_net_buy",
                "turnover_amount": "inst_net_buy",
                "buy_amount": "inst_buy_total",
                "inst_net_buy": "inst_net_buy",
            }
            inst_key = inst_sort_map.get(sort_by, "inst_net_buy")
            institution = self._sort_items(institution, inst_key, descending)
            if top_n:
                institution = institution[:top_n]

        if active_broker and top_n:
            active_broker = active_broker[:top_n]

        if broker_rank and top_n:
            broker_rank = broker_rank[:top_n]

        if stock_stat:
            stat_sort_map = {
                "net_buy_amount": "net_buy_amount",
                "turnover_amount": "board_turnover",
                "listed_count": "listed_count",
            }
            stat_key = stat_sort_map.get(sort_by, "listed_count")
            stock_stat = self._sort_items(stock_stat, stat_key, descending)
            if top_n:
                stock_stat = stock_stat[:top_n]

        summary = build_dragon_tiger_summary_text(
            daily_detail, institution, active_broker, broker_rank, stock_stat
        )

        result = DragonTigerResult(
            daily_detail=daily_detail,
            daily_detail_count=len(daily_detail),
            institution=institution,
            institution_count=len(institution),
            active_broker=active_broker,
            active_broker_count=len(active_broker),
            broker_rank=broker_rank,
            broker_rank_count=len(broker_rank),
            stock_stat=stock_stat,
            stock_stat_count=len(stock_stat),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        """Sort a list of pydantic models by a given attribute key."""
        def _get_val(item):
            v = getattr(item, key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

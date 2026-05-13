from __future__ import annotations

from openclaw_stock_mcp.app.models.block_trade import BlockTradeResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_block_trade_adapters import (
    adapt_block_trade_active_stock_row,
    adapt_block_trade_broker_rank_row,
    adapt_block_trade_daily_row,
    adapt_block_trade_daily_stat_row,
    adapt_block_trade_industry_row,
    build_block_trade_summary_text,
)


class BlockTradeUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = request.include
        trade_date = request.trade_date
        start_date = getattr(request, "start_date", None)
        end_date = getattr(request, "end_date", None)
        period = request.period
        industry_period = request.industry_period
        sort_by = request.sort_by
        descending = request.descending
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        daily_detail = []
        daily_stat = []
        industry_stat = []
        broker_rank = []
        active_stock = []

        # A类: date-range queries
        if "daily_detail" in include:
            rows = provider.get_block_trade_daily(start_date or trade_date, end_date or trade_date)
            daily_detail = [adapt_block_trade_daily_row(r) for r in rows]

        if "daily_stat" in include:
            rows = provider.get_block_trade_daily_stat(start_date or trade_date, end_date or trade_date)
            daily_stat = [adapt_block_trade_daily_stat_row(r) for r in rows]

        # B类: period-based statistics
        if "industry_stat" in include:
            rows = provider.get_block_trade_industry(period=industry_period)
            industry_stat = [adapt_block_trade_industry_row(r) for r in rows]

        if "broker_rank" in include:
            rows = provider.get_block_trade_broker_rank(period=period)
            broker_rank = [adapt_block_trade_broker_rank_row(r) for r in rows]

        if "active_stock" in include:
            rows = provider.get_block_trade_active_stock(period=period)
            active_stock = [adapt_block_trade_active_stock_row(r) for r in rows]

        # Sort daily_detail
        if daily_detail:
            daily_detail = self._sort_items(daily_detail, sort_by, descending)
            if top_n:
                daily_detail = daily_detail[:top_n]

        # Sort daily_stat
        if daily_stat:
            stat_key_map = {
                "turnover": "total_turnover",
                "discount_rate": "discount_rate",
                "turnover_to_float_cap": "turnover_to_float_cap",
            }
            stat_key = stat_key_map.get(sort_by, "total_turnover")
            daily_stat = self._sort_items(daily_stat, stat_key, descending)
            if top_n:
                daily_stat = daily_stat[:top_n]

        # Sort active_stock
        if active_stock:
            stock_key_map = {
                "total_turnover": "total_turnover",
                "listed_count": "total_listed_count",
                "discount_rate": "avg_discount_rate",
                "avg_return_5d": "avg_return_5d",
            }
            stock_key = stock_key_map.get(sort_by, "total_turnover")
            active_stock = self._sort_items(active_stock, stock_key, descending)
            if top_n:
                active_stock = active_stock[:top_n]

        if broker_rank and top_n:
            broker_rank = broker_rank[:top_n]

        if industry_stat and top_n:
            industry_stat = industry_stat[:top_n]

        summary = build_block_trade_summary_text(
            daily_detail, daily_stat, industry_stat, broker_rank, active_stock
        )

        result = BlockTradeResult(
            daily_detail=daily_detail,
            daily_detail_count=len(daily_detail),
            daily_stat=daily_stat,
            daily_stat_count=len(daily_stat),
            industry_stat=industry_stat,
            industry_stat_count=len(industry_stat),
            broker_rank=broker_rank,
            broker_rank_count=len(broker_rank),
            active_stock=active_stock,
            active_stock_count=len(active_stock),
            summary=summary,
        )
        return result.model_dump()

    @staticmethod
    def _sort_items(items: list, key: str, descending: bool = True) -> list:
        def _get_val(item):
            v = getattr(item, key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v
        return sorted(items, key=_get_val, reverse=descending)

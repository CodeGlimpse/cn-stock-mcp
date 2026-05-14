from __future__ import annotations

from datetime import date

from openclaw_stock_mcp.app.models.sec_reveal import SecRevealResult
from openclaw_stock_mcp.app.services.cache_service import CacheService
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_sec_reveal_adapters import (
    adapt_active_broker_row,
    adapt_institution_detail_row,
    adapt_institution_trace_row,
    adapt_seat_detail_row,
    build_sec_reveal_summary,
)
from openclaw_stock_mcp.providers.adapters.broker_tags import summarize_broker_tags


class SecRevealUseCase:
    _shared_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        if SecRevealUseCase._shared_cache is None:
            SecRevealUseCase._shared_cache = CacheService(maxsize=32, ttl=300)
        self.cache = SecRevealUseCase._shared_cache

    def execute(self, request) -> dict:
        include = request.include
        trade_date = request.trade_date or date.today().strftime("%Y%m%d")
        start_date = request.start_date or trade_date
        end_date = request.end_date or start_date
        period = request.period
        top_n = request.top_n

        provider = self.router.get_provider("akshare")

        stock_seat_buy = []
        stock_seat_sell = []
        active_broker = []
        institution_detail = []
        institution_trace = []

        if "stock_seat_detail" in include:
            if not request.symbol:
                raise ValueError("symbol is required when include contains 'stock_seat_detail'")
            code = request.symbol.split(".", 1)[0]
            cache_key = f"secreveal:seat:{code}:{trade_date}"
            cached = self.cache.get(cache_key)
            if cached is None:
                buy_rows = provider.get_lhb_stock_seat_detail(symbol=code, date=trade_date, flag="买入")
                sell_rows = provider.get_lhb_stock_seat_detail(symbol=code, date=trade_date, flag="卖出")
                cached = {"buy": buy_rows, "sell": sell_rows}
                self.cache.set(cache_key, cached)
            stock_seat_buy = [adapt_seat_detail_row(r, side="buy") for r in cached.get("buy", [])]
            stock_seat_sell = [adapt_seat_detail_row(r, side="sell") for r in cached.get("sell", [])]
            if top_n:
                stock_seat_buy = stock_seat_buy[:top_n]
                stock_seat_sell = stock_seat_sell[:top_n]

        if "active_broker" in include:
            cache_key = f"secreveal:active_broker:{start_date}:{end_date}"
            rows = self.cache.get(cache_key)
            if rows is None:
                rows = provider.get_lhb_active_broker(start_date=start_date, end_date=end_date)
                self.cache.set(cache_key, rows)
            active_broker = [adapt_active_broker_row(r) for r in rows]
            active_broker = self._sort_items(active_broker, request.sort_by, request.descending)
            if top_n:
                active_broker = active_broker[:top_n]

        if "institution_detail" in include:
            cache_key = "secreveal:institution_detail:sina"
            rows = self.cache.get(cache_key)
            if rows is None:
                rows = provider.get_lhb_institution_detail_sina()
                self.cache.set(cache_key, rows)
            institution_detail = [adapt_institution_detail_row(r) for r in rows]
            if request.symbol:
                code = request.symbol.split(".", 1)[0]
                institution_detail = [i for i in institution_detail if i.code == code]
            institution_detail = self._sort_items(institution_detail, request.sort_by, request.descending)
            if top_n:
                institution_detail = institution_detail[:top_n]

        if "institution_trace" in include:
            cache_key = f"secreveal:institution_trace:{period}"
            rows = self.cache.get(cache_key)
            if rows is None:
                rows = provider.get_lhb_institution_trace_sina(period=period)
                self.cache.set(cache_key, rows)
            institution_trace = [adapt_institution_trace_row(r) for r in rows]
            if request.symbol:
                code = request.symbol.split(".", 1)[0]
                institution_trace = [i for i in institution_trace if i.code == code]
            institution_trace = self._sort_items(institution_trace, request.sort_by, request.descending)
            if top_n:
                institution_trace = institution_trace[:top_n]

        summary = build_sec_reveal_summary(
            stock_seat_buy, stock_seat_sell, active_broker, institution_detail, institution_trace
        )
        broker_tag_summary = summarize_broker_tags([*stock_seat_buy, *stock_seat_sell, *active_broker])
        return SecRevealResult(
            stock_seat_buy=stock_seat_buy,
            stock_seat_buy_count=len(stock_seat_buy),
            stock_seat_sell=stock_seat_sell,
            stock_seat_sell_count=len(stock_seat_sell),
            active_broker=active_broker,
            active_broker_count=len(active_broker),
            institution_detail=institution_detail,
            institution_detail_count=len(institution_detail),
            institution_trace=institution_trace,
            institution_trace_count=len(institution_trace),
            broker_tag_summary=broker_tag_summary,
            summary=summary,
        ).model_dump()

    @staticmethod
    def _sort_items(items: list, sort_by: str, descending: bool = True) -> list:
        key_map = {
            "net_amount": "net_amount",
            "buy_amount": "buy_amount",
            "sell_amount": "sell_amount",
            "inst_net_amount": "inst_net_amount",
            "inst_buy_amount": "inst_buy_amount",
            "total_buy_amount": "total_buy_amount",
        }
        sort_key = key_map.get(sort_by, "net_amount")

        def _get_val(item):
            v = getattr(item, sort_key, None)
            if v is None:
                return float("-inf") if descending else float("inf")
            return v

        return sorted(items, key=_get_val, reverse=descending)

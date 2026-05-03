from __future__ import annotations

from types import SimpleNamespace

from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
from openclaw_stock_mcp.app.usecases.stock_review import StockReviewUseCase


class StockReviewBatchUseCase:
    def __init__(self) -> None:
        self.single = StockReviewUseCase()

    def execute(self, request):
        items = []
        errors = []

        for symbol in request.symbols:
            try:
                single_req = SimpleNamespace(
                    symbol=symbol,
                    trade_date=request.trade_date,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    adjust=request.adjust,
                    provider=request.provider,
                )
                review = self.single.execute(single_req)
                items.append(self._to_card(review))
            except Exception as exc:
                errors.append({"symbol": symbol, **serialize_exception(exc)})

        sorted_items = self._sort_items(items, request.sort_by, request.descending)
        top_items = sorted_items[: request.top_n]

        return {
            "mode": top_items[0]["mode"] if top_items else ("range_review" if request.start_date and request.end_date else "trade_date_review"),
            "requested_trade_date": request.trade_date,
            "requested_start_date": request.start_date,
            "requested_end_date": request.end_date,
            "sort_by": request.sort_by,
            "descending": request.descending,
            "items": top_items,
            "count": len(top_items),
            "total_symbols": len(request.symbols),
            "partial_failure": len(errors) > 0,
            "errors": errors,
            "summary": self._build_summary(top_items, request.sort_by),
        }

    def _to_card(self, review: dict) -> dict:
        stats = review.get("stats", {})
        relative_strength = stats.get("relative_strength_20d")
        if relative_strength is None:
            relative_strength = stats.get("relative_strength_period")
        period_return = stats.get("period_return")
        if period_return is None:
            period_return = stats.get("return_20d")
        max_drawdown = stats.get("max_drawdown_period")
        if max_drawdown is None:
            max_drawdown = stats.get("max_drawdown_20d")
        volume_ratio = stats.get("volume_ratio_5d")

        latest_bar = review.get("latest_bar")
        return {
            "symbol": review.get("symbol"),
            "mode": review.get("mode"),
            "trade_date": review.get("trade_date"),
            "start_date": review.get("start_date"),
            "end_date": review.get("end_date"),
            "close": getattr(latest_bar, "close", None) if latest_bar is not None else None,
            "relative_strength": relative_strength,
            "return": period_return,
            "max_drawdown": max_drawdown,
            "volume_ratio": volume_ratio,
            "benchmark": review.get("benchmark"),
            "stats": stats,
            "summary": review.get("summary"),
            "source": review.get("source"),
        }

    def _sort_items(self, items: list[dict], sort_by: str, descending: bool) -> list[dict]:
        key_map = {
            "relative_strength": "relative_strength",
            "return": "return",
            "max_drawdown": "max_drawdown",
            "volume_ratio": "volume_ratio",
        }
        key_name = key_map[sort_by]
        return sorted(
            items,
            key=lambda item: self._sort_value(item.get(key_name), descending),
            reverse=descending,
        )

    def _sort_value(self, value, descending: bool):
        if value is None:
            return float("-inf") if descending else float("inf")
        return value

    def _build_summary(self, items: list[dict], sort_by: str) -> str:
        if not items:
            return "批量复盘无结果。"
        leader = items[0]
        trailer = items[-1]
        metric = {
            "relative_strength": "相对强弱",
            "return": "收益",
            "max_drawdown": "回撤",
            "volume_ratio": "量比",
        }.get(sort_by, sort_by)
        return (
            f"批量复盘完成：共 {len(items)} 只；"
            f"按 {metric} 排序，首位 {leader.get('symbol')}，末位 {trailer.get('symbol')}。"
        )

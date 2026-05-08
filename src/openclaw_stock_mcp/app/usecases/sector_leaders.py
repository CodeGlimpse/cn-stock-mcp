from __future__ import annotations

from types import SimpleNamespace

from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
from openclaw_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase
from openclaw_stock_mcp.providers.errors import ProviderError


class SectorLeadersUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.sector_lookup = SectorLookupUseCase()
        self.batch_review = StockReviewBatchUseCase()

    @staticmethod
    def _rank(items: list[dict], key: str, descending: bool = True, top_n: int = 3) -> list[dict]:
        def _v(item):
            value = item.get(key)
            if value is None:
                return float("-inf") if descending else float("inf")
            return value

        return sorted(items, key=_v, reverse=descending)[:top_n]

    def execute(self, request):
        members_resp = self.sector_lookup.execute(
            SimpleNamespace(
                mode="children",
                sector_type=getattr(request, "sector_type", "primary"),
                sector_name=request.sector_name,
                limit=request.limit,
                provider=request.provider,
            )
        )
        members = members_resp.get("items", [])
        symbols = [item.symbol for item in members if getattr(item, "symbol", None)]
        if not symbols:
            raise ProviderError("EMPTY_RESULT", f"No sector members found for {request.sector_name}", retryable=False)

        batch_resp = self.batch_review.execute(
            SimpleNamespace(
                symbols=symbols,
                trade_date=request.trade_date,
                start_date=request.start_date,
                end_date=request.end_date,
                adjust=request.adjust,
                provider="akshare",
                sort_by=request.sort_by,
                descending=request.descending,
                top_n=request.limit,
                min_relative_strength=request.min_relative_strength,
                min_return=request.min_return,
                max_drawdown_limit=request.max_drawdown_limit,
                min_volume_ratio=request.min_volume_ratio,
            )
        )

        items = batch_resp.get("items", [])
        leaders = self._rank(items, key=request.sort_by, descending=True, top_n=request.top_n)
        followers = [
            item
            for item in self._rank(items, key="relative_strength", descending=True, top_n=max(request.top_n * 3, 10))
            if item.get("symbol") not in {x.get("symbol") for x in leaders}
            and item.get("return") is not None
            and item.get("return") > 0
        ][: request.top_n]
        draggers = self._rank(items, key="return", descending=False, top_n=request.top_n)

        return {
            "subject_type": "sector_leaders",
            "subject_name": request.sector_name,
            "sector_name": request.sector_name,
            "sector_type": getattr(request, "sector_type", "primary"),
            "mode": batch_resp.get("mode"),
            "trade_date": batch_resp.get("requested_trade_date"),
            "requested_trade_date": batch_resp.get("requested_trade_date"),
            "start_date": batch_resp.get("requested_start_date"),
            "end_date": batch_resp.get("requested_end_date"),
            "member_count": len(symbols),
            "reviewed_count": len(items),
            "leaders": leaders,
            "followers": followers,
            "draggers": draggers,
            "items": items,
            "partial_failure": batch_resp.get("partial_failure", False),
            "errors": batch_resp.get("errors", []),
            "meta": {
                "sort_by": request.sort_by,
                "descending": request.descending,
                "top_n": request.top_n,
                "lookup_meta": members_resp.get("meta", {}),
            },
            "summary": (
                f"{request.sector_name} 龙头快照：龙头 {len(leaders)} 只，跟风 {len(followers)} 只，拖累 {len(draggers)} 只。"
            ),
        }

from __future__ import annotations

from datetime import datetime

from openclaw_stock_mcp.app.services.fallback import run_with_fallback
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter


class MarketBriefUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request):
        trade_date = request.trade_date or datetime.now().strftime("%Y-%m-%d")

        overview_selection = self.router.choose_provider(
            tool_name="market_overview",
            sec_type="index",
            preferred=(None if request.provider == "mixed" else request.provider),
        )
        overview = run_with_fallback(
            self.router,
            overview_selection,
            lambda provider: provider.get_market_overview(request.market),
        )

        pools: dict[str, dict] = {}
        if request.include_pools:
            for pool_type in ("limit_up", "limit_down", "strong"):
                pool_selection = self.router.choose_provider(
                    tool_name="market_pool",
                    sec_type="stock",
                    preferred=(getattr(request, "provider", None) or "zhitu"),
                )
                items = run_with_fallback(
                    self.router,
                    pool_selection,
                    lambda provider, _pool_type=pool_type: provider.get_market_pool(
                        pool_type=_pool_type,
                        trade_date=trade_date,
                    ),
                )
                top_items = items[: request.top_n] if request.top_n else items
                pools[pool_type] = {
                    "count": len(items),
                    "top_items": top_items,
                    "source": pool_selection.primary,
                }

        indices = overview.get("indices", []) if isinstance(overview, dict) else []
        summary = self._build_summary(indices, pools, trade_date, request.brief_type)

        return {
            "brief_type": request.brief_type,
            "trade_date": trade_date,
            "market": request.market,
            "overview": overview,
            "pools": pools,
            "summary": summary,
        }

    def _build_summary(self, indices, pools, trade_date: str, brief_type: str) -> str:
        index_parts = []
        for q in indices[:4]:
            name = getattr(q, "name", None) or getattr(q, "symbol", "指数")
            cp = getattr(q, "change_percent", None)
            if cp is None:
                index_parts.append(f"{name} 涨跌幅未知")
            else:
                index_parts.append(f"{name} {cp:.2f}%")

        pool_part = ""
        if pools:
            up = pools.get("limit_up", {}).get("count", 0)
            down = pools.get("limit_down", {}).get("count", 0)
            strong = pools.get("strong", {}).get("count", 0)
            pool_part = f"；涨停 {up} 家，跌停 {down} 家，强势 {strong} 家"

        index_text = "，".join(index_parts) if index_parts else "指数概览暂不可用"
        return f"{trade_date}（{brief_type}）市场简报：{index_text}{pool_part}。"

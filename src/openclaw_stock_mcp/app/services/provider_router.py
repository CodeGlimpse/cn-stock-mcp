from __future__ import annotations

from openclaw_stock_mcp.app.services.provider_types import ProviderSelection
from openclaw_stock_mcp.providers.akshare_provider import AKShareProvider
from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


class ProviderRouter:
    def __init__(self) -> None:
        self.akshare = AKShareProvider()
        self.zhitu = ZhituProvider()

    def choose_provider(self, tool_name: str, symbol: str | None = None, sec_type: str | None = None, preferred: str | None = None) -> ProviderSelection:
        if tool_name in {"trading_calendar", "stock_review"}:
            return ProviderSelection(primary="akshare", fallback=[])

        if preferred == "akshare":
            return ProviderSelection(primary="akshare", fallback=["zhitu"])
        if preferred == "zhitu":
            return ProviderSelection(primary="zhitu", fallback=["akshare"])

        normalized = (symbol or "").upper()

        if tool_name == "stock_search":
            return ProviderSelection(primary="akshare", fallback=["zhitu"])

        if tool_name == "market_overview":
            return ProviderSelection(primary="zhitu", fallback=["akshare"])

        if tool_name == "sector_lookup":
            return ProviderSelection(primary="zhitu", fallback=[])

        if tool_name == "stock_history":
            if sec_type == "index":
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            if sec_type == "stock":
                if normalized.endswith(".BJ") or normalized.startswith(("430", "83", "87", "92")):
                    return ProviderSelection(primary="zhitu", fallback=["akshare"])
                if normalized.startswith("688") or normalized.startswith("688."):
                    return ProviderSelection(primary="zhitu", fallback=["akshare"])
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "technical_indicator":
            if sec_type == "stock" or sec_type == "index":
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            return ProviderSelection(primary="zhitu", fallback=[])

        if tool_name in {"market_pool", "stock_orderbook", "stock_profile", "sector_quote", "event_calendar"}:
            return ProviderSelection(primary="zhitu", fallback=[])

        if tool_name == "capital_flow":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "stock_financial":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "limit_stat":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "northbound":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "valuation_rank":
            return ProviderSelection(primary="zhitu", fallback=["akshare"])

        if tool_name == "index_compose":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "industry_valuation_rank":
            return ProviderSelection(primary="zhitu", fallback=["akshare"])

        if tool_name == "earnings_quality":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "macro_indicator":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "dragon_tiger":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "etf_snapshot":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "convertible_bond":
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "stock_quote":
            if sec_type == "index" or sec_type == "fund":
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            if normalized.endswith(".BJ") or normalized.startswith(("430", "83", "87", "92")):
                return ProviderSelection(primary="zhitu", fallback=[])
            if normalized.startswith("688") or normalized.startswith("688."):
                return ProviderSelection(primary="zhitu", fallback=[])
            # stock-main（SH/SZ 非 688）定稿：zhitu 主，akshare 备
            return ProviderSelection(primary="zhitu", fallback=["akshare"])

        return ProviderSelection(primary="akshare", fallback=["zhitu"])

    def get_provider(self, name: str):
        if name == "zhitu":
            return self.zhitu
        return self.akshare

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

        if tool_name in {"market_pool", "stock_orderbook"}:
            return ProviderSelection(primary="zhitu", fallback=[])

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

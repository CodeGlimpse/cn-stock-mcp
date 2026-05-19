from __future__ import annotations

from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.akshare_northbound_adapters import build_northbound_summary_text


class NorthboundUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        include = getattr(request, "include", ["daily_summary", "history"])
        history_n = getattr(request, "history_n", 30)
        provider = self.router.get_provider("akshare")

        daily_summary = None
        history = []

        if "daily_summary" in include:
            daily_summary = provider.get_northbound_daily_summary()

        if "history" in include:
            history = provider.get_northbound_history(limit=history_n)

        summary_text = build_northbound_summary_text(daily_summary, history)

        result: dict = {
            "source": "akshare",
            "summary": summary_text,
        }

        if daily_summary is not None:
            result["daily_summary"] = daily_summary

        if history:
            result["history"] = history
            result["history_count"] = len(history)

        return result

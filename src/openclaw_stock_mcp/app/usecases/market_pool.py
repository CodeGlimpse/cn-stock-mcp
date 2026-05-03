from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter


class MarketPoolUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def _annotate_anomalies(self, items: list[dict] | list) -> list:
        for item in items:
            extra = getattr(item, "extra", None)
            if not isinstance(extra, dict):
                continue

            anomaly_flags: list[str] = []
            if getattr(item, "price", None) == 0:
                anomaly_flags.append("zero_price")
            if getattr(item, "turnover", None) == 0:
                anomaly_flags.append("zero_turnover")
            if getattr(item, "market_cap", None) == 0:
                anomaly_flags.append("zero_market_cap")
            if getattr(item, "float_market_cap", None) == 0:
                anomaly_flags.append("zero_float_market_cap")

            if anomaly_flags:
                extra["anomaly_flags"] = anomaly_flags
                extra["data_quality"] = "suspect"
            else:
                extra.setdefault("data_quality", "normal")
        return items

    def execute(self, request):
        selection = self.router.choose_provider(
            tool_name="market_pool",
            sec_type="stock",
            preferred=(getattr(request, "provider", None) or "zhitu"),
        )
        items, fallback_meta = run_with_fallback_meta(
            self.router,
            selection,
            lambda provider: provider.get_market_pool(
                pool_type=request.pool_type,
                trade_date=request.trade_date,
            ),
        )
        items = self._annotate_anomalies(items)
        if request.limit:
            items = items[: request.limit]
        return {
            "pool_type": request.pool_type,
            "trade_date": request.trade_date,
            "items": items,
            "count": len(items),
            "source": fallback_meta.final_provider or selection.primary,
            "meta": {
                "selected_primary": fallback_meta.selected_primary,
                "selected_fallback": fallback_meta.selected_fallback,
                "attempted": fallback_meta.attempted,
                "final_provider": fallback_meta.final_provider,
                "used_fallback": fallback_meta.used_fallback,
            },
        }

from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.infra.config import get_settings


class ProviderHealthUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.settings = get_settings()

    def execute(self, request=None):
        checks = []
        zhitu_token = self.settings.resolve_zhitu_token()
        checks.append({
            "name": "zhitu_token",
            "status": "ok" if zhitu_token else "missing",
            "detail": "resolved" if zhitu_token else "not configured",
        })

        zhitu = self.router.get_provider("zhitu")
        try:
            quote = zhitu.get_quote("000001.SH", "index")
            checks.append({
                "name": "zhitu_quote_index",
                "status": "ok",
                "detail": quote.timestamp,
            })
        except Exception as exc:
            checks.append({
                "name": "zhitu_quote_index",
                "status": "error",
                "detail": str(exc),
            })

        try:
            bars = zhitu.get_history("000001.SH", "index", "1d", limit=2)
            checks.append({
                "name": "zhitu_history_index",
                "status": "ok",
                "detail": f"bars={len(bars)}",
            })
        except Exception as exc:
            checks.append({
                "name": "zhitu_history_index",
                "status": "error",
                "detail": str(exc),
            })

        try:
            ob = zhitu.get_orderbook("688001.SH", "stock")
            checks.append({
                "name": "zhitu_orderbook_star",
                "status": "ok",
                "detail": f"bids={len(ob.bids)},asks={len(ob.asks)}",
            })
        except Exception as exc:
            checks.append({
                "name": "zhitu_orderbook_star",
                "status": "error",
                "detail": str(exc),
            })

        akshare = self.router.get_provider("akshare")
        try:
            items = akshare.search_instruments("平安银行", sec_types=["stock"], limit=1)
            checks.append({
                "name": "akshare_search_stock",
                "status": "ok",
                "detail": f"items={len(items)}",
            })
        except Exception as exc:
            checks.append({
                "name": "akshare_search_stock",
                "status": "error",
                "detail": str(exc),
            })

        try:
            bars = akshare.get_history("600519.SH", "stock", "1d", limit=2, adjust="none")
            checks.append({
                "name": "akshare_history_stock",
                "status": "ok",
                "detail": f"bars={len(bars)}",
            })
        except Exception as exc:
            checks.append({
                "name": "akshare_history_stock",
                "status": "error",
                "detail": str(exc),
            })

        overall = "ok"
        if any(item["status"] == "error" for item in checks):
            overall = "degraded"
        if any(item["status"] == "missing" for item in checks):
            overall = "degraded"

        return {
            "overall": overall,
            "checks": checks,
        }

from openclaw_stock_mcp.app.usecases.stock_history import StockHistoryUseCase


class _Bar:
    def __init__(self, t: str):
        self.time = t


class _Provider:
    def get_history(self, **kwargs):
        return [_Bar("2026-04-30"), _Bar("2026-05-30")]


class _Router:
    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="akshare", fallback=[])

    def get_provider(self, name: str):
        return _Provider()


class _Resolver:
    class _Resolved:
        symbol = "600519.SH"
        sec_type = "stock"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_stock_history_stock_monthly_response_contains_review_meta():
    uc = StockHistoryUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type(
        "Req",
        (),
        {
            "symbol": "600519.SH",
            "sec_type": "stock",
            "interval": "1M",
            "start_date": "2026-04-01",
            "end_date": "2026-05-31",
            "limit": 12,
            "adjust": "none",
            "provider": "akshare",
        },
    )()

    result = uc.execute(req)

    assert result["source"] == "akshare"
    assert result["meta"]["derived_from"] == "1d"
    assert result["meta"]["aggregation"] == "calendar_month"
    assert result["meta"]["limit_applied_after_aggregation"] is True
    assert result["meta"]["partial_period_at_range_edges"] is True

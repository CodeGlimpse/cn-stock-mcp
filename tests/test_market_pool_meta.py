from openclaw_stock_mcp.app.usecases.market_pool import MarketPoolUseCase


class _Provider:
    def __init__(self, should_fail: bool):
        self.should_fail = should_fail

    def get_market_pool(self, **kwargs):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "pool failed", retryable=True)
        return [{"symbol": "600000.SH"}, {"symbol": "600519.SH"}]


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider(should_fail=True),
            "akshare": _Provider(should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


def test_market_pool_response_contains_meta():
    uc = MarketPoolUseCase()
    uc.router = _Router()

    req = type("Req", (), {"pool_type": "limit_up", "trade_date": "2026-05-02", "limit": 1, "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["count"] == 1
    assert result["source"] == "akshare"
    assert result["meta"]["used_fallback"] is True

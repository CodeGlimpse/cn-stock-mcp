from openclaw_stock_mcp.app.usecases.market_pool import MarketPoolUseCase


class _Item:
    def __init__(self, symbol, price=None, turnover=None, market_cap=None, float_market_cap=None):
        self.symbol = symbol
        self.price = price
        self.turnover = turnover
        self.market_cap = market_cap
        self.float_market_cap = float_market_cap
        self.extra = {}


class _Provider:
    def __init__(self, should_fail: bool):
        self.should_fail = should_fail

    def get_market_pool(self, **kwargs):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "pool failed", retryable=True)
        return [
            _Item("600000.SH", price=0, turnover=0, market_cap=0, float_market_cap=0),
            _Item("600519.SH", price=1384.79, turnover=7316111748.0, market_cap=1734131271030.0, float_market_cap=1734131271030.0),
        ]


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


def test_market_pool_anomaly_flags_are_added_for_suspect_rows():
    uc = MarketPoolUseCase()
    uc.router = _Router()

    req = type("Req", (), {"pool_type": "limit_down", "trade_date": "2026-05-02", "limit": 2, "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["items"][0].extra["data_quality"] == "suspect"
    assert "zero_price" in result["items"][0].extra["anomaly_flags"]
    assert result["items"][1].extra["data_quality"] == "normal"

from cn_stock_mcp.app.usecases.market_overview import MarketOverviewUseCase


class _Provider:
    def __init__(self, name: str, should_fail: bool):
        self.name = name
        self.should_fail = should_fail

    def get_market_overview(self, market):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "overview failed", retryable=True)
        return {"market": market, "indices": [], "source": self.name}


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider("zhitu", should_fail=True),
            "akshare": _Provider("akshare", should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


def test_market_overview_response_contains_meta_and_source():
    uc = MarketOverviewUseCase()
    uc.router = _Router()

    req = type("Req", (), {"market": "CN", "provider": "mixed"})()
    result = uc.execute(req)

    assert result["source"] == "akshare"
    assert result["meta"]["used_fallback"] is True

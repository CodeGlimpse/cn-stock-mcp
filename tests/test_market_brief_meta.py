from openclaw_stock_mcp.app.usecases.market_brief import MarketBriefUseCase


class _Provider:
    def __init__(self, name: str, should_fail: bool):
        self.name = name
        self.should_fail = should_fail

    def get_market_overview(self, market):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "overview failed", retryable=True)
        return {"market": market, "indices": []}

    def get_market_pool(self, pool_type, trade_date):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "pool failed", retryable=True)
        return [{"symbol": "600000.SH"}]


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider("zhitu", should_fail=True),
            "akshare": _Provider("akshare", should_fail=False),
        }

    def choose_provider(self, tool_name, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        if tool_name == "market_overview":
            return ProviderSelection(primary="zhitu", fallback=["akshare"])
        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


def test_market_brief_response_contains_meta_for_overview_and_pools():
    uc = MarketBriefUseCase()
    uc.router = _Router()

    req = type(
        "Req",
        (),
        {
            "brief_type": "close",
            "market": "CN",
            "trade_date": "2026-05-02",
            "include_pools": True,
            "top_n": 1,
            "provider": "mixed",
        },
    )()

    result = uc.execute(req)

    assert "meta" in result
    assert result["meta"]["overview"]["used_fallback"] is True
    assert result["meta"]["pools"]["limit_up"]["used_fallback"] is True

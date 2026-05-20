from cn_stock_mcp.app.usecases.technical_indicator import TechnicalIndicatorUseCase


class _Series:
    def model_dump(self):
        return {"symbol": "000001.SH", "indicator": "macd", "items": []}


class _Provider:
    def __init__(self, name: str, should_fail: bool):
        self.name = name
        self.should_fail = should_fail

    def get_indicator(self, **kwargs):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "indicator failed", retryable=True)
        return _Series()


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


class _Resolver:
    class _Resolved:
        symbol = "000001.SH"
        sec_type = "index"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_technical_indicator_response_contains_meta():
    uc = TechnicalIndicatorUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type(
        "Req",
        (),
        {
            "symbol": "000001.SH",
            "sec_type": "index",
            "interval": "1d",
            "indicator": "macd",
            "start_date": None,
            "end_date": None,
            "limit": 30,
            "provider": None,
        },
    )()

    result = uc.execute(req)

    assert "meta" in result
    assert result["meta"]["used_fallback"] is True
    assert result["meta"]["final_provider"] == "akshare"

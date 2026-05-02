from openclaw_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase


class _Quote:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def model_dump(self):
        return {"symbol": self.symbol}


class _Provider:
    def __init__(self, name: str, should_fail: bool):
        self.name = name
        self.should_fail = should_fail

    def get_quote(self, symbol: str, sec_type: str):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "failed", retryable=True)
        return _Quote(symbol)


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider("zhitu", should_fail=True),
            "akshare": _Provider("akshare", should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


class _Resolver:
    class _Resolved:
        symbol = "600519.SH"
        sec_type = "stock"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_stock_quote_response_contains_meta():
    uc = StockQuoteUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbols": ["600519.SH"], "sec_type": "stock", "provider": None, "provider_preference": None})()
    result = uc.execute(req)

    assert result["partial_failure"] is False
    assert result["meta"]["per_symbol"][0]["used_fallback"] is True
    assert result["meta"]["per_symbol"][0]["final_provider"] == "akshare"

from cn_stock_mcp.app.usecases.stock_orderbook import OrderbookUseCase


class _Orderbook:
    def model_dump(self):
        return {"bids": [], "asks": []}


class _Provider:
    def __init__(self, should_fail: bool):
        self.should_fail = should_fail

    def get_orderbook(self, **kwargs):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "orderbook failed", retryable=True)
        return _Orderbook()


class _Router:
    def __init__(self):
        self.providers = {
            "zhitu": _Provider(should_fail=True),
            "akshare": _Provider(should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


class _Resolver:
    class _Resolved:
        symbol = "688001.SH"
        sec_type = "stock"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_orderbook_response_contains_meta():
    uc = OrderbookUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type("Req", (), {"symbol": "688001.SH", "sec_type": "stock", "provider": "zhitu"})()
    result = uc.execute(req)

    assert result["source"] == "akshare"
    assert result["meta"]["used_fallback"] is True

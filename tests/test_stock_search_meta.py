from cn_stock_mcp.app.usecases.stock_search import StockSearchUseCase


class _Provider:
    def __init__(self, should_fail: bool, result=None):
        self.should_fail = should_fail
        self.result = result if result is not None else [{"symbol": "000001.SZ"}]

    def search_instruments(self, **kwargs):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "search failed", retryable=True)
        return self.result


class _Router:
    def __init__(self):
        self.providers = {
            "akshare": _Provider(should_fail=True),
            "zhitu": _Provider(should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="akshare", fallback=["zhitu"])

    def get_provider(self, name: str):
        return self.providers[name]


def test_stock_search_response_contains_meta_and_fallback_source():
    uc = StockSearchUseCase()
    uc.router = _Router()

    req = type("Req", (), {"query": "平安", "sec_types": ["stock"], "market": "CN", "limit": 10, "provider": None})()
    result = uc.execute(req)

    assert result["total"] == 1
    assert result["source"] == "zhitu"
    assert result["meta"]["used_fallback"] is True


def test_stock_search_empty_primary_result_falls_back_to_secondary():
    uc = StockSearchUseCase()
    router = _Router()
    router.providers = {
        "akshare": _Provider(should_fail=False, result=[]),
        "zhitu": _Provider(should_fail=False, result=[{"symbol": "000001.SZ"}]),
    }
    uc.router = router

    req = type("Req", (), {"query": "平安", "sec_types": ["stock"], "market": "CN", "limit": 10, "provider": None})()
    result = uc.execute(req)

    assert result["total"] == 1
    assert result["source"] == "zhitu"
    assert result["meta"]["used_fallback"] is True
    assert result["meta"]["attempted"] == ["akshare", "zhitu"]

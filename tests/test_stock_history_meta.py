from openclaw_stock_mcp.app.usecases.stock_history import StockHistoryUseCase


class _Bar:
    def __init__(self, t: str):
        self.time = t


class _Provider:
    def __init__(self, name: str, should_fail: bool):
        self.name = name
        self.should_fail = should_fail

    def get_history(self, **kwargs):
        if self.should_fail:
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "history failed", retryable=True)
        return [_Bar("2026-05-01"), _Bar("2026-05-02")]


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
        symbol = "000001.SH"
        sec_type = "index"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_stock_history_response_contains_meta_and_source_from_fallback():
    uc = StockHistoryUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    req = type(
        "Req",
        (),
        {
            "symbol": "000001.SH",
            "sec_type": "index",
            "interval": "1d",
            "start_date": None,
            "end_date": None,
            "limit": 20,
            "adjust": "none",
            "provider": None,
        },
    )()

    result = uc.execute(req)

    assert result["count"] == 2
    assert result["source"] == "akshare"
    assert result["meta"]["used_fallback"] is True
    assert result["meta"]["final_provider"] == "akshare"

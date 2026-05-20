from cn_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from cn_stock_mcp.app.usecases.technical_indicator import TechnicalIndicatorUseCase


class _Bar:
    def __init__(self, t: str):
        self.time = t


class _Series:
    def model_dump(self):
        return {"symbol": "600519.SH", "indicator": "macd", "items": []}


class _ProviderHistory:
    def __init__(self, should_fail: bool):
        self.should_fail = should_fail

    def get_history(self, **kwargs):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "history failed", retryable=True)
        return [_Bar("2026-05-07 09:35:00"), _Bar("2026-05-07 09:40:00")]


class _ProviderIndicator:
    def __init__(self, should_fail: bool):
        self.should_fail = should_fail

    def get_indicator(self, **kwargs):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "indicator failed", retryable=True)
        return _Series()


class _RouterHistory:
    def __init__(self):
        self.providers = {
            "zhitu": _ProviderHistory(should_fail=False),
            "akshare": _ProviderHistory(should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


class _RouterIndicator:
    def __init__(self):
        self.providers = {
            "zhitu": _ProviderIndicator(should_fail=False),
            "akshare": _ProviderIndicator(should_fail=False),
        }

    def choose_provider(self, **kwargs):
        from cn_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name: str):
        return self.providers[name]


class _ResolverStock:
    class _Resolved:
        symbol = "600519.SH"
        sec_type = "stock"

    def resolve(self, symbol, sec_type):
        return self._Resolved()


def test_stock_history_stock_intraday_prefers_zhitu_without_derived_meta():
    uc = StockHistoryUseCase()
    uc.router = _RouterHistory()
    uc.resolver = _ResolverStock()

    req = type(
        "Req",
        (),
        {
            "symbol": "600519.SH",
            "sec_type": "stock",
            "interval": "5m",
            "start_date": "2026-05-07",
            "end_date": "2026-05-07",
            "limit": 20,
            "adjust": "qfq",
            "provider": None,
        },
    )()

    result = uc.execute(req)

    assert result["source"] == "zhitu"
    assert result["count"] == 2
    assert result["meta"]["used_fallback"] is False
    assert "derived_from" not in result["meta"]


def test_technical_indicator_stock_prefers_zhitu_and_contains_meta():
    uc = TechnicalIndicatorUseCase()
    uc.router = _RouterIndicator()
    uc.resolver = _ResolverStock()

    req = type(
        "Req",
        (),
        {
            "symbol": "600519.SH",
            "sec_type": "stock",
            "interval": "1d",
            "indicator": "macd",
            "start_date": "2026-05-01",
            "end_date": "2026-05-07",
            "limit": 30,
            "provider": None,
        },
    )()

    result = uc.execute(req)

    assert result["symbol"] == "600519.SH"
    assert result["indicator"] == "macd"
    assert result["meta"]["used_fallback"] is False
    assert result["meta"]["final_provider"] == "zhitu"

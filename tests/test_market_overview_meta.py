import pytest

from cn_stock_mcp.app.usecases.market_overview import MarketOverviewUseCase
from cn_stock_mcp.providers.errors import ProviderError


class _Provider:
    def __init__(self, name: str, should_fail: bool, indices=None):
        self.name = name
        self.should_fail = should_fail
        self.indices = indices if indices is not None else []

    def get_market_overview(self, market):
        if self.should_fail:
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "overview failed", retryable=True)
        return {"market": market, "indices": self.indices, "source": self.name}


class _Router:
    def __init__(self, *, zhitu_fail=True, zhitu_indices=None, akshare_fail=False, akshare_indices=None):
        if akshare_indices is None:
            akshare_indices = [{"symbol": "000001.SH", "value": 3000.0}]
        self.providers = {
            "zhitu": _Provider("zhitu", should_fail=zhitu_fail, indices=zhitu_indices),
            "akshare": _Provider("akshare", should_fail=akshare_fail, indices=akshare_indices),
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


def test_market_overview_falls_back_when_primary_returns_empty():
    uc = MarketOverviewUseCase()
    uc.router = _Router(
        zhitu_indices=[],
        akshare_indices=[{"symbol": "000001.SH", "value": 3000.0}],
    )

    req = type("Req", (), {"market": "CN-P1-empty-fallback", "provider": "mixed"})()
    result = uc.execute(req)

    assert result["source"] == "akshare"
    assert result["indices"] == [{"symbol": "000001.SH", "value": 3000.0}]
    assert result["meta"]["attempted"] == ["zhitu", "akshare"]
    assert result["meta"]["used_fallback"] is True


def test_market_overview_raises_when_all_providers_return_empty():
    uc = MarketOverviewUseCase()
    uc.router = _Router(zhitu_indices=[], akshare_indices=[])

    req = type("Req", (), {"market": "CN-P1-all-empty", "provider": "mixed"})()

    with pytest.raises(ProviderError, match="no index data"):
        uc.execute(req)

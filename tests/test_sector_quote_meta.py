from openclaw_stock_mcp.app.usecases.sector_quote import SectorQuoteUseCase


class _Quote:
    def __init__(self, symbol: str, change_percent: float | None, turnover: float | None):
        self.symbol = symbol
        self.change_percent = change_percent
        self.turnover = turnover

    def model_dump(self):
        return {
            "symbol": self.symbol,
            "change_percent": self.change_percent,
            "turnover": self.turnover,
        }


class _Provider:
    name = "zhitu"

    def get_sector_quote(self, symbol: str, sector_type: str | None = None):
        if symbol == "BAD.BKZS":
            from openclaw_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "failed", retryable=True)

        if symbol == "A.BKZS":
            return _Quote(symbol, 3.0, 100.0)
        if symbol == "B.BKZS":
            return _Quote(symbol, 1.0, 300.0)
        return _Quote(symbol, None, None)


class _Router:
    def __init__(self):
        self.provider = _Provider()

    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=[])

    def get_provider(self, name: str):
        return self.provider


class _Resolver:
    class _Resolved:
        def __init__(self, symbol: str):
            self.symbol = symbol
            self.sec_type = "sector"

    def resolve(self, symbol, sec_type):
        return self._Resolved(symbol)


def _req(**kwargs):
    base = {
        "symbols": ["A.BKZS", "B.BKZS", "BAD.BKZS"],
        "sector_type": "concept",
        "sort_by": None,
        "descending": True,
        "top_n": None,
        "provider": None,
    }
    base.update(kwargs)
    return type("Req", (), base)()


def test_sector_quote_partial_failure_with_per_symbol_errors():
    uc = SectorQuoteUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    result = uc.execute(_req())

    assert result["partial_failure"] is True
    assert len(result["items"]) == 2
    assert len(result["errors"]) == 1
    assert result["errors"][0]["symbol"] == "BAD.BKZS"


def test_sector_quote_sort_by_change_percent_and_top_n():
    uc = SectorQuoteUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    result = uc.execute(_req(sort_by="change_percent", top_n=1))

    assert len(result["items"]) == 1
    assert result["items"][0].symbol == "A.BKZS"
    assert result["meta"]["sort_by"] == "change_percent"
    assert result["meta"]["top_n"] == 1


def test_sector_quote_sort_by_turnover_descending():
    uc = SectorQuoteUseCase()
    uc.router = _Router()
    uc.resolver = _Resolver()

    result = uc.execute(_req(sort_by="turnover", top_n=2, descending=True))

    assert [i.symbol for i in result["items"]] == ["B.BKZS", "A.BKZS"]

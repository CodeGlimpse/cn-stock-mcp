from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase
from openclaw_stock_mcp.app.models.quote import Quote


class _ResolverBackedProvider:
    def get_quote(self, symbol: str, sec_type: str):
        return Quote(
            symbol=symbol,
            name="mock",
            sec_type=sec_type,
            exchange=symbol.split(".", 1)[1],
            board="index" if sec_type == "index" else "main",
            price=1.0,
            source="mock",
        )


class _Router:
    def choose_provider(self, **kwargs):
        from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

        return ProviderSelection(primary="zhitu", fallback=[])

    def get_provider(self, name: str):
        return _ResolverBackedProvider()


def test_symbol_resolver_infers_common_cn_indices_as_index():
    resolver = SymbolResolver()

    assert resolver.infer_sec_type("000300.SH") == "index"
    assert resolver.infer_sec_type("000905.SH") == "index"
    assert resolver.infer_sec_type("000852.SH") == "index"
    assert resolver.infer_sec_type("000016.SH") == "index"
    assert resolver.infer_sec_type("399001.SZ") == "index"
    assert resolver.infer_sec_type("899050.BJ") == "index"


def test_symbol_resolver_still_infers_common_funds_and_stocks_correctly():
    resolver = SymbolResolver()

    assert resolver.infer_sec_type("159001.SZ") == "fund"
    assert resolver.infer_sec_type("510300.SH") == "fund"
    assert resolver.infer_sec_type("600519.SH") == "stock"
    assert resolver.infer_sec_type("300750.SZ") == "stock"


def test_stock_quote_allows_common_index_symbol_with_requested_index_sec_type():
    uc = StockQuoteUseCase()
    uc.router = _Router()
    uc.resolver = SymbolResolver()

    req = type(
        "Req",
        (),
        {"symbols": ["000300.SH"], "sec_type": "index", "provider": None, "provider_preference": None},
    )()
    result = uc.execute(req)

    assert result["partial_failure"] is False
    assert result["errors"] == []
    assert result["items"][0].symbol == "000300.SH"
    assert result["meta"]["per_symbol"][0]["sec_type"] == "index"

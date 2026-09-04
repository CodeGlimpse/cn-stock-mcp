from types import SimpleNamespace
from cn_stock_mcp.providers.errors import ProviderError

from cn_stock_mcp.app.models.quote import Quote
from cn_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase
from cn_stock_mcp.server.schemas import StockQuoteRequest


class _MockBatchProvider:
    name = "zhitu"

    def __init__(self, quotes, meta):
        self._quotes = quotes
        self.last_batch_meta = meta

    def get_quotes_with_meta(self, symbols, sec_type=None):
        return self._quotes, self.last_batch_meta


class _MockRouter:
    def __init__(self, provider):
        self.provider = provider

    def choose_provider(self, tool_name, symbol=None, sec_type=None, preferred=None):
        return SimpleNamespace(primary="zhitu", fallback=["akshare"])

    def get_provider(self, name):
        return self.provider


def test_stock_quote_meta_reports_batch_fallback_and_partial_failure():
    provider = _MockBatchProvider(
        quotes=[Quote(symbol="600519.SH", name="贵州茅台", sec_type="stock", price=1600.0, change_percent=1.5, source="zhitu")],
        meta={
            "batch_attempted": True,
            "batch_failed": True,
            "batch_fallback_used": True,
            "batch_fallback_mode": "single_quote",
            "batch_provider": "zhitu",
            "batch_error": {"error_code": "PARTIAL_RESULT", "message": "symbol missing from batch response", "retryable": True},
            "requested_symbols": ["600519.SH", "000001.SZ"],
            "returned_symbols": ["600519.SH"],
            "missing_symbols": ["000001.SZ"],
            "per_symbol": {
                "600519.SH": {
                    "batch_attempted": True,
                    "batch_failed": False,
                    "batch_fallback_used": False,
                    "batch_fallback_mode": None,
                    "batch_provider": "zhitu",
                    "batch_error": None,
                },
                "000001.SZ": {
                    "batch_attempted": True,
                    "batch_failed": True,
                    "batch_fallback_used": True,
                    "batch_fallback_mode": "single_quote",
                    "batch_provider": "zhitu",
                    "batch_error": {"error_code": "PARTIAL_RESULT", "message": "symbol missing from batch response", "retryable": True},
                },
            },
        },
    )
    uc = StockQuoteUseCase()
    uc.router = _MockRouter(provider)

    result = uc.execute(StockQuoteRequest(symbols=["600519.SH", "000001.SZ"], sec_type="stock"))

    assert result["partial_failure"] is True
    assert len(result["items"]) == 1
    assert result["errors"][0]["symbol"] == "000001.SZ"
    assert result["meta"]["batch"] == {
        "attempted": True,
        "failed": True,
        "fallback_used": True,
        "fallback_mode": "single_quote",
        "failed_symbols": ["000001.SZ"],
    }
    per = {x["symbol"]: x for x in result["meta"]["per_symbol"]}
    assert per["600519.SH"]["batch_attempted"] is True
    assert per["600519.SH"]["batch_failed"] is False
    assert per["000001.SZ"]["batch_failed"] is True
    assert per["000001.SZ"]["batch_fallback_used"] is True
    assert per["000001.SZ"]["batch_fallback_mode"] == "single_quote"


def test_stock_quote_meta_reports_clean_batch_success():
    provider = _MockBatchProvider(
        quotes=[
            Quote(symbol="600519.SH", name="贵州茅台", sec_type="stock", price=1600.0, change_percent=1.5, source="zhitu"),
            Quote(symbol="000001.SZ", name="平安银行", sec_type="stock", price=10.0, change_percent=-0.5, source="zhitu"),
        ],
        meta={
            "batch_attempted": True,
            "batch_failed": False,
            "batch_fallback_used": False,
            "batch_fallback_mode": None,
            "batch_provider": "zhitu",
            "batch_error": None,
            "requested_symbols": ["600519.SH", "000001.SZ"],
            "returned_symbols": ["600519.SH", "000001.SZ"],
            "missing_symbols": [],
            "per_symbol": {
                "600519.SH": {"batch_attempted": True, "batch_failed": False, "batch_fallback_used": False, "batch_fallback_mode": None, "batch_provider": "zhitu", "batch_error": None},
                "000001.SZ": {"batch_attempted": True, "batch_failed": False, "batch_fallback_used": False, "batch_fallback_mode": None, "batch_provider": "zhitu", "batch_error": None},
            },
        },
    )
    uc = StockQuoteUseCase()
    uc.router = _MockRouter(provider)

    result = uc.execute(StockQuoteRequest(symbols=["600519.SH", "000001.SZ"], sec_type="stock"))

    assert result["partial_failure"] is False
    assert len(result["items"]) == 2
    assert result["meta"]["batch"]["attempted"] is True
    assert result["meta"]["batch"]["failed"] is False
    assert result["meta"]["batch"]["fallback_used"] is False
    assert result["meta"]["batch"]["failed_symbols"] == []


def test_stock_quote_batch_exception_tries_akshare_fallback_per_symbol():
    class _BatchFailureProvider:
        name = "zhitu"

        def get_quotes_with_meta(self, symbols, sec_type=None):
            raise ProviderError("PROVIDER_TIMEOUT", "batch timed out", retryable=True)

        def get_quote(self, symbol, sec_type):
            raise ProviderError("PROVIDER_TIMEOUT", "single timed out", retryable=True)

    class _FallbackProvider:
        name = "akshare"

        def get_quote(self, symbol, sec_type):
            return Quote(symbol=symbol, name=symbol, sec_type="stock", price=1.0, source="akshare")

    class _FallbackRouter:
        def __init__(self):
            self.providers = {"zhitu": _BatchFailureProvider(), "akshare": _FallbackProvider()}

        def choose_provider(self, **kwargs):
            return SimpleNamespace(primary="zhitu", fallback=["akshare"])

        def get_provider(self, name):
            return self.providers[name]

    uc = StockQuoteUseCase()
    uc.router = _FallbackRouter()
    result = uc.execute(StockQuoteRequest(symbols=["600519.SH", "000001.SZ"], sec_type="stock"))

    assert result["partial_failure"] is False
    assert [item.source for item in result["items"]] == ["akshare", "akshare"]
    assert all(item["used_fallback"] for item in result["meta"]["per_symbol"])


def test_stock_quote_missing_batch_symbol_tries_alternate_provider_after_internal_fallback():
    missing_meta = {
        "batch_attempted": True,
        "batch_failed": True,
        "batch_fallback_used": True,
        "per_symbol": {
            "600519.SH": {"batch_attempted": True, "batch_failed": False},
            "000001.SZ": {
                "batch_attempted": True,
                "batch_failed": True,
                "batch_fallback_used": True,
                "batch_fallback_mode": "single_quote",
                "batch_error": {"error_code": "PARTIAL_RESULT", "message": "missing", "retryable": True},
            },
        },
    }

    class _Primary:
        def get_quotes_with_meta(self, symbols, sec_type=None):
            return [Quote(symbol="600519.SH", sec_type="stock", source="zhitu")], missing_meta

    class _Fallback:
        def get_quote(self, symbol, sec_type):
            return Quote(symbol=symbol, sec_type="stock", source="akshare", price=1.0)

    class _RouterWithFallback:
        def choose_provider(self, **kwargs):
            return SimpleNamespace(primary="zhitu", fallback=["akshare"])

        def get_provider(self, name):
            return _Primary() if name == "zhitu" else _Fallback()

    uc = StockQuoteUseCase()
    uc.router = _RouterWithFallback()
    result = uc.execute(StockQuoteRequest(symbols=["600519.SH", "000001.SZ"], sec_type="stock"))

    assert result["partial_failure"] is False
    assert [item.symbol for item in result["items"]] == ["600519.SH", "000001.SZ"]
    recovered = next(item for item in result["meta"]["per_symbol"] if item["symbol"] == "000001.SZ")
    assert recovered["final_provider"] == "akshare"
    assert recovered["used_fallback"] is True

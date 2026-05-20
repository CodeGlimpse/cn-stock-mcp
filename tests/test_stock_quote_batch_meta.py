from types import SimpleNamespace

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

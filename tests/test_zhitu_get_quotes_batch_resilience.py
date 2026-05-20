from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.providers.zhitu_provider import ZhituProvider
from cn_stock_mcp.providers.adapters.zhitu_market_adapters import adapt_zhitu_quote


class _UnexpectedBatchZhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}
        self.paths = []

    def _get_json(self, path: str, params=None):
        self.paths.append(path)
        if path == "/hs/public/ssjymore":
            return "upstream temporary html or text"
        if path == "/hs/real/ssjy/600519":
            return {"p": 1600.0, "pc": 1.5, "mc": "贵州茅台"}
        if path == "/hs/real/ssjy/000001":
            return {"p": 10.0, "pc": -0.5, "mc": "平安银行"}
        raise AssertionError(f"unexpected path: {path}")

    def _fill_quote_name(self, quote, sec_type, symbol):
        return quote


class _NonDictItemBatchZhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}

    def _get_json(self, path: str, params=None):
        if path == "/hs/public/ssjymore":
            return ["bad", {"dm": "sh600519", "mc": "贵州茅台", "p": 1600.0, "pc": 1.5}]
        raise AssertionError(f"unexpected path: {path}")


def test_zhitu_get_quotes_batch_unexpected_payload_falls_back_to_single():
    provider = _UnexpectedBatchZhitu()

    quotes = provider.get_quotes(["600519.SH", "000001.SZ"], "stock")

    assert len(quotes) == 2
    assert quotes[0].symbol == "600519.SH"
    assert quotes[0].change_percent == 1.5
    assert quotes[1].symbol == "000001.SZ"
    assert quotes[1].change_percent == -0.5
    assert "/hs/public/ssjymore" in provider.paths
    assert "/hs/real/ssjy/600519" in provider.paths
    assert "/hs/real/ssjy/000001" in provider.paths


def test_zhitu_get_quotes_batch_unexpected_payload_meta_marks_fallback():
    provider = _UnexpectedBatchZhitu()

    quotes, meta = provider.get_quotes_with_meta(["600519.SH", "000001.SZ"], "stock")

    assert len(quotes) == 2
    assert meta["batch_attempted"] is True
    assert meta["batch_failed"] is True
    assert meta["batch_fallback_used"] is True
    assert meta["batch_fallback_mode"] == "single_quote"
    assert meta["missing_symbols"] == []
    assert meta["per_symbol"]["600519.SH"]["batch_failed"] is True
    assert meta["per_symbol"]["000001.SZ"]["batch_failed"] is True


def test_zhitu_get_quotes_batch_missing_symbol_meta_marks_partial():
    class _PartialBatchZhitu(ZhituProvider):
        def __init__(self):
            self._instrument_name_cache = {}

        def _get_json(self, path: str, params=None):
            if path == "/hs/public/ssjymore":
                return [{"dm": "sh600519", "mc": "贵州茅台", "p": 1600.0, "pc": 1.5}]
            if path == "/hs/real/ssjy/000001":
                return {"p": 10.0, "pc": -0.5, "mc": "平安银行"}
            raise AssertionError(f"unexpected path: {path}")

        def _fill_quote_name(self, quote, sec_type, symbol):
            return quote

    provider = _PartialBatchZhitu()

    quotes, meta = provider.get_quotes_with_meta(["600519.SH", "000001.SZ"], "stock")

    assert len(quotes) == 2
    assert meta["batch_attempted"] is True
    assert meta["batch_failed"] is True
    assert meta["batch_fallback_used"] is True
    assert meta["per_symbol"]["600519.SH"]["batch_failed"] is False
    assert meta["per_symbol"]["000001.SZ"]["batch_failed"] is True
    assert meta["per_symbol"]["000001.SZ"]["batch_fallback_mode"] == "single_quote"


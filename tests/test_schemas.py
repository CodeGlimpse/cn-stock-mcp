from openclaw_stock_mcp.server.schemas import StockHistoryRequest, TechnicalIndicatorRequest


def test_stock_history_interval_alias_normalization():
    req = StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="d")
    assert req.interval == "1d"

    req2 = StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="15")
    assert req2.interval == "15m"


def test_technical_indicator_alias_normalization():
    req = TechnicalIndicatorRequest(symbol="000001.SH", sec_type="index", interval="m", indicator="MACD")
    assert req.interval == "1M"
    assert req.indicator == "macd"

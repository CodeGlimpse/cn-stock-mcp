import pytest
from pydantic import ValidationError

from openclaw_stock_mcp.server.schemas import StockHistoryRequest, TechnicalIndicatorRequest


def test_stock_history_interval_alias_normalization():
    req = StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="d")
    assert req.interval == "1d"

    req2 = StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="15")
    assert req2.interval == "15m"


def test_stock_history_rejects_1m_interval():
    with pytest.raises(ValidationError) as exc:
        StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="1m")

    assert "1m is not supported" in str(exc.value)


def test_technical_indicator_alias_normalization():
    req = TechnicalIndicatorRequest(symbol="000001.SH", sec_type="index", interval="m", indicator="MACD")
    assert req.interval == "1M"
    assert req.indicator == "macd"


def test_technical_indicator_rejects_1m_interval():
    with pytest.raises(ValidationError) as exc:
        TechnicalIndicatorRequest(symbol="000001.SH", sec_type="index", interval="1m", indicator="macd")

    assert "1m is not supported" in str(exc.value)

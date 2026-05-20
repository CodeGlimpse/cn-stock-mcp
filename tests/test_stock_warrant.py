"""Tests for stock_warrant usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.stock_warrant import StockWarrantUseCase
from cn_stock_mcp.server.schemas import StockWarrantRequest


def _make_etf_rows():
    return [
        {"合约名称": "50ETF购5月2600", "最新价": 0.0825, "涨跌幅": -12.77, "涨跌额": -0.0121, "成交量": 1205, "持仓量": 35200, "行权价": 2.60, "到期日": "2026-05-28"},
        {"合约名称": "50ETF沽5月2600", "最新价": 0.0134, "涨跌幅": 32.67, "涨跌额": 0.0033, "成交量": 890, "持仓量": 28400, "行权价": 2.60, "到期日": "2026-05-28"},
        {"合约名称": "50ETF购6月2700", "最新价": 0.0456, "涨跌幅": -8.42, "涨跌额": -0.0042, "成交量": 3200, "持仓量": 56000, "行权价": 2.70, "到期日": "2026-06-25"},
    ]


def _make_commodity_rows():
    return [
        {"合约名称": "SR607C6200", "最新价": 175, "涨跌幅": -5.41, "涨跌额": -10, "成交量": 56, "持仓量": 1250, "行权价": 6200, "到期日": "2026-07-07"},
        {"合约名称": "SR607P6200", "最新价": 35, "涨跌幅": 16.67, "涨跌额": 5, "成交量": 28, "持仓量": 890, "行权价": 6200, "到期日": "2026-07-07"},
    ]


def _make_index_rows():
    return [
        {"代码": "IO2606C3900", "名称": "沪深300购6月3900", "现价": 245.6, "涨跌": -12.8, "涨跌幅": -4.95, "总成交量": 120, "空盘量": 850, "执行价格": 3900, "最后交易日": "2026-06-19"},
        {"代码": "IO2606P3900", "名称": "沪深300沽6月3900", "现价": 46.2, "涨跌": 5.8, "涨跌幅": 14.36, "总成交量": 85, "空盘量": 620, "执行价格": 3900, "最后交易日": "2026-06-19"},
    ]


def test_stock_warrant_etf():
    uc = StockWarrantUseCase()
    mock_provider = MagicMock()
    mock_provider.get_etf_option.return_value = _make_etf_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockWarrantRequest(include=["etf_option"])
        result = uc.execute(req)
    assert result["etf_option_count"] == 3
    item = result["etf_option"][0]
    assert "50ETF" in item["symbol"]
    assert item["latest_price"] == 0.0825
    assert item["strike"] == 2.60


def test_stock_warrant_commodity():
    uc = StockWarrantUseCase()
    mock_provider = MagicMock()
    mock_provider.get_commodity_option.return_value = _make_commodity_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockWarrantRequest(include=["commodity_option"], commodity_exchange="大商所")
        result = uc.execute(req)
    assert result["commodity_option_count"] == 2
    item = result["commodity_option"][0]
    assert item["symbol"] == "SR607C6200"


def test_stock_warrant_index():
    uc = StockWarrantUseCase()
    mock_provider = MagicMock()
    mock_provider.get_index_option.return_value = _make_index_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockWarrantRequest(include=["index_option"])
        result = uc.execute(req)
    assert result["index_option_count"] == 2
    item = result["index_option"][0]
    assert item["latest_price"] == 245.6


def test_stock_warrant_top_n():
    uc = StockWarrantUseCase()
    mock_provider = MagicMock()
    mock_provider.get_etf_option.return_value = _make_etf_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockWarrantRequest(include=["etf_option"], top_n=2)
        result = uc.execute(req)
    assert result["etf_option_count"] == 2


def test_stock_warrant_uses_cache():
    uc = StockWarrantUseCase()
    raw = _make_etf_rows()
    uc.cache.set("warrant:etf:50ETF期权", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockWarrantRequest(include=["etf_option"])
        result = uc.execute(req)
    mock_provider.get_etf_option.assert_not_called()
    assert result["etf_option_count"] == 3


def test_stock_warrant_summary():
    uc = StockWarrantUseCase()
    mock_provider = MagicMock()
    mock_provider.get_etf_option.return_value = _make_etf_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockWarrantRequest(include=["etf_option"])
        result = uc.execute(req)
    assert "ETF期权" in result["summary"]

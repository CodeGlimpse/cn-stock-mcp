"""Tests for stock_screen usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.stock_screen import StockScreenUseCase
from cn_stock_mcp.server.schemas import StockScreenRequest


def _make_spot_rows():
    return [
        {"代码": "sh600519", "名称": "贵州茅台", "最新价": 1800.0, "涨跌额": 10.0, "涨跌幅": 0.56, "买入": 1800.0, "卖出": 1800.1, "昨收": 1790.0, "今开": 1795.0, "最高": 1810.0, "最低": 1790.0, "成交量": 5000000.0, "成交额": 9000000000.0, "时间戳": "15:00:00"},
        {"代码": "sz000001", "名称": "平安银行", "最新价": 12.5, "涨跌额": -0.3, "涨跌幅": -2.35, "买入": 12.5, "卖出": 12.51, "昨收": 12.8, "今开": 12.8, "最高": 12.85, "最低": 12.4, "成交量": 100000000.0, "成交额": 1250000000.0, "时间戳": "15:00:00"},
        {"代码": "sh688001", "名称": "华兴源创", "最新价": 62.41, "涨跌额": -0.27, "涨跌幅": -0.43, "买入": 62.4, "卖出": 62.41, "昨收": 62.68, "今开": 62.0, "最高": 63.0, "最低": 61.0, "成交量": 21514096.0, "成交额": 1305554000.0, "时间戳": "15:00:00"},
        {"代码": "sz300001", "名称": "特锐德", "最新价": 25.3, "涨跌额": 1.0, "涨跌幅": 4.11, "买入": 25.3, "卖出": 25.31, "昨收": 24.3, "今开": 24.5, "最高": 25.5, "最低": 24.3, "成交量": 30000000.0, "成交额": 750000000.0, "时间戳": "15:00:00"},
        {"代码": "bj920000", "名称": "安徽凤凰", "最新价": 16.2, "涨跌额": -0.18, "涨跌幅": -1.10, "买入": 16.2, "卖出": 16.27, "昨收": 16.38, "今开": 16.22, "最高": 16.44, "最低": 16.06, "成交量": 791997.0, "成交额": 12836981.0, "时间戳": "15:30:01"},
    ]


def test_stock_screen_all():
    uc = StockScreenUseCase()
    mock_provider = MagicMock()
    mock_provider.get_a_share_spot_all.return_value = _make_spot_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(market="all")
        result = uc.execute(req)
    assert result["total_before_filter"] == 5
    assert result["total_after_filter"] == 5


def test_stock_screen_by_market():
    uc = StockScreenUseCase()
    mock_provider = MagicMock()
    mock_provider.get_a_share_spot_all.return_value = _make_spot_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(market="star")
        result = uc.execute(req)
    assert result["total_after_filter"] == 1
    assert result["items"][0]["symbol"] == "688001.SH"


def test_stock_screen_price_filter():
    uc = StockScreenUseCase()
    mock_provider = MagicMock()
    mock_provider.get_a_share_spot_all.return_value = _make_spot_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(min_price=10, max_price=30)
        result = uc.execute(req)
    # Should match: 平安银行(12.5), 特锐德(25.3), 安徽凤凰(16.2)
    assert result["total_after_filter"] == 3


def test_stock_screen_change_pct_filter():
    uc = StockScreenUseCase()
    mock_provider = MagicMock()
    mock_provider.get_a_share_spot_all.return_value = _make_spot_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(min_change_pct=0)
        result = uc.execute(req)
    # Positive: 贵州茅台(0.56), 特锐德(4.11)
    assert result["total_after_filter"] == 2


def test_stock_screen_sort_and_top_n():
    uc = StockScreenUseCase()
    mock_provider = MagicMock()
    mock_provider.get_a_share_spot_all.return_value = _make_spot_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(sort_by="change_pct", descending=True, top_n=2)
        result = uc.execute(req)
    assert len(result["items"]) == 2
    assert result["items"][0]["change_pct"] == 4.11  # 特锐德
    assert result["items"][1]["change_pct"] == 0.56  # 贵州茅台


def test_stock_screen_min_amplitude():
    uc = StockScreenUseCase()
    mock_provider = MagicMock()
    mock_provider.get_a_share_spot_all.return_value = _make_spot_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(min_amplitude=2.0)
        result = uc.execute(req)
    # Amplitude = (high-low)/prev_close*100
    # 茅台: (1810-1790)/1790*100=1.12% → filtered out
    # 平安: (12.85-12.4)/12.8*100=3.52% → pass
    # 华兴: (63-61)/62.68*100=3.19% → pass
    # 特锐德: (25.5-24.3)/24.3*100=4.94% → pass
    # 凤凰: (16.44-16.06)/16.38*100=2.32% → pass
    assert result["total_after_filter"] == 4


def test_stock_screen_summary():
    uc = StockScreenUseCase()
    mock_provider = MagicMock()
    mock_provider.get_a_share_spot_all.return_value = _make_spot_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(market="main", min_change_pct=0)
        result = uc.execute(req)
    assert "筛选完成" in result["summary"]


def test_stock_screen_uses_cache():
    uc = StockScreenUseCase()
    # Pre-fill cache
    raw = _make_spot_rows()
    uc.spot_cache.set("screen:spot_all", raw)
    mock_provider = MagicMock()
    # Provider should NOT be called
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockScreenRequest(market="all")
        result = uc.execute(req)
    mock_provider.get_a_share_spot_all.assert_not_called()
    assert result["total_after_filter"] == 5

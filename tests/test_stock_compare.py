"""Tests for stock_compare usecase with mocked providers."""
from unittest.mock import MagicMock, patch

from openclaw_stock_mcp.app.usecases.stock_compare import StockCompareUseCase
from openclaw_stock_mcp.server.schemas import StockCompareRequest


def _make_sina_rows():
    return [
        {"代码": "sh600519", "名称": "贵州茅台", "最新价": 1800.0, "涨跌额": 10.0, "涨跌幅": 0.56, "买入": 1800.0, "卖出": 1800.1, "昨收": 1790.0, "今开": 1795.0, "最高": 1810.0, "最低": 1790.0, "成交量": 5000000.0, "成交额": 9000000000.0, "时间戳": "15:00:00"},
        {"代码": "sz000858", "名称": "五粮液", "最新价": 140.5, "涨跌额": 2.1, "涨跌幅": 1.52, "买入": 140.5, "卖出": 140.51, "昨收": 138.4, "今开": 139.0, "最高": 141.0, "最低": 138.5, "成交量": 30000000.0, "成交额": 4200000000.0, "时间戳": "15:00:00"},
    ]


def _make_zhitu_quotes():
    from openclaw_stock_mcp.app.models.quote import Quote
    return {
        "600519.SH": Quote(symbol="600519.SH", name="贵州茅台", sec_type="stock", source="zhitu", price=1800.0, change_percent=0.56, pe=32.5, pb=10.1, market_cap=2.26e12, float_market_cap=1.8e12, turnover_rate=0.35, volume=5000000, turnover=9e9),
        "000858.SZ": Quote(symbol="000858.SZ", name="五粮液", sec_type="stock", source="zhitu", price=140.5, change_percent=1.52, pe=22.1, pb=6.3, market_cap=5.5e11, float_market_cap=4.2e11, turnover_rate=0.82, volume=30000000, turnover=4.2e9),
    }


def _make_financial_rows():
    return [
        {"选项": "常用指标", "指标": "营业总收入", "20260331": 5.47e10, "20251231": 1.72e11},
        {"选项": "常用指标", "指标": "归母净利润", "20260331": 2.72e10, "20251231": 8.23e10},
        {"选项": "常用指标", "指标": "净资产收益率", "20260331": 12.5, "20251231": 34.2},
        {"选项": "常用指标", "指标": "毛利率", "20260331": 91.2, "20251231": 91.5},
        {"选项": "常用指标", "指标": "资产负债率", "20260331": 19.3, "20251231": 18.9},
    ]


def test_stock_compare_quote():
    uc = StockCompareUseCase()
    # Pre-fill stock_screen cache
    from openclaw_stock_mcp.app.usecases.stock_screen import StockScreenUseCase
    screen_uc = StockScreenUseCase()
    screen_uc.spot_cache.set("screen:spot_all", _make_sina_rows())

    try:
        req = StockCompareRequest(symbols=["600519.SH", "000858.SZ"], include=["quote"])
        result = uc.execute(req)
    finally:
        # Clear cache to avoid polluting other tests
        screen_uc.spot_cache.set("screen:spot_all", None)
    assert result["total_count"] == 2
    item1 = result["items"][0]
    assert item1["symbol"] == "600519.SH"
    assert item1["latest_price"] == 1800.0
    assert item1["change_pct"] == 0.56
    assert item1["source_quote"] == "akshare_sina"


def test_stock_compare_valuation():
    uc = StockCompareUseCase()
    mock_zhitu = MagicMock()
    mock_zhitu.get_quotes.return_value = _make_zhitu_quotes()
    with patch.object(uc.router, "get_provider", return_value=mock_zhitu):
        req = StockCompareRequest(symbols=["600519.SH", "000858.SZ"], include=["valuation"])
        result = uc.execute(req)
    assert result["total_count"] == 2
    item1 = result["items"][0]
    assert item1["pe"] == 32.5
    assert item1["pb"] == 10.1
    assert item1["market_cap"] == 2.26e12
    assert item1["source_valuation"] == "zhitu"


def test_stock_compare_financial():
    uc = StockCompareUseCase()
    mock_ak = MagicMock()
    mock_ak.get_financial_abstract.return_value = _make_financial_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_ak):
        req = StockCompareRequest(symbols=["600519.SH", "000858.SZ"], include=["financial"])
        result = uc.execute(req)
    assert result["total_count"] == 2
    item = result["items"][0]
    assert item["revenue"] == 5.47e10
    assert item["net_profit"] == 2.72e10
    assert item["roe"] == 12.5
    assert item["gross_margin"] == 91.2
    assert item["debt_ratio"] == 19.3


def test_stock_compare_combined():
    uc = StockCompareUseCase()
    # Fill Sina cache
    from openclaw_stock_mcp.app.usecases.stock_screen import StockScreenUseCase
    screen_uc = StockScreenUseCase()
    screen_uc.spot_cache.set("screen:spot_all", _make_sina_rows())

    mock_zhitu = MagicMock()
    mock_zhitu.get_quotes.return_value = _make_zhitu_quotes()

    def mock_get_provider(name):
        if name == "zhitu":
            return mock_zhitu
        return MagicMock()

    try:
        with patch.object(uc.router, "get_provider", side_effect=mock_get_provider):
            req = StockCompareRequest(symbols=["600519.SH", "000858.SZ"], include=["quote", "valuation"])
            result = uc.execute(req)
    finally:
        screen_uc.spot_cache.set("screen:spot_all", None)
    assert result["total_count"] == 2
    item1 = result["items"][0]
    # Has both quote and valuation data
    assert item1["latest_price"] == 1800.0  # from Sina (or zhitu)
    assert item1["pe"] == 32.5  # from Zhitu


def test_stock_compare_min_2_symbols():
    from pydantic import ValidationError
    try:
        StockCompareRequest(symbols=["600519.SH"])
        assert False
    except ValidationError as e:
        assert "at least 2" in str(e) or "min_length" in str(e)


def test_stock_compare_max_10_symbols():
    from pydantic import ValidationError
    try:
        StockCompareRequest(symbols=[f"{i:06d}.SH" for i in range(11)])
        assert False
    except ValidationError as e:
        assert "at most 10" in str(e) or "max_length" in str(e)


def test_stock_compare_summary():
    uc = StockCompareUseCase()
    mock_zhitu = MagicMock()
    mock_zhitu.get_quotes.return_value = _make_zhitu_quotes()
    with patch.object(uc.router, "get_provider", return_value=mock_zhitu):
        req = StockCompareRequest(symbols=["600519.SH", "000858.SZ"], include=["valuation"])
        result = uc.execute(req)
    assert "对比" in result["summary"]

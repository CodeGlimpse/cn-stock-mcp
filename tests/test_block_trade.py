"""Tests for block_trade usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.block_trade import BlockTradeUseCase
from cn_stock_mcp.server.schemas import BlockTradeRequest


def _make_daily_detail_rows():
    return [
        {
            "序号": 1,
            "交易日期": "2026-05-06",
            "证券代码": "600519",
            "证券简称": "贵州茅台",
            "成交价": 1500.0,
            "成交量": 100.0,
            "成交额": 150000.0,
            "买方营业部": "机构专用",
            "卖方营业部": "中信证券总部",
        }
    ]


def _make_daily_stat_rows():
    return [
        {
            "序号": 1,
            "交易日期": "2026-05-06",
            "证券代码": "600519",
            "证券简称": "贵州茅台",
            "涨跌幅": 0.5,
            "收盘价": 1510.0,
            "成交价": 1500.0,
            "折溢率": -0.0066,
            "成交笔数": 3,
            "成交总量": 100.0,
            "成交总额": 150000.0,
            "成交总额/流通市值": 0.12,
        }
    ]


def _make_industry_rows():
    return [
        {
            "行业": "白酒",
            "上榜次数": 5,
            "成交笔数": 10,
            "总成交额": 500000.0,
            "平均折溢率": -0.03,
            "溢价次数": 1,
            "折价次数": 4,
            "溢价成交额": 50000.0,
            "折价成交额": 450000.0,
        }
    ]


def _make_broker_rank_rows():
    return [
        {
            "序号": 1,
            "营业部名称": "机构专用",
            "上榜后1天-买入次数": 100,
            "上榜后1天-平均涨幅": 0.5,
            "上榜后1天-上涨概率": 55.0,
            "上榜后5天-买入次数": 80,
            "上榜后5天-平均涨幅": 2.0,
            "上榜后5天-上涨概率": 65.0,
            "上榜后10天-买入次数": 50,
            "上榜后10天-平均涨幅": 4.0,
            "上榜后10天-上涨概率": 70.0,
            "上榜后20天-买入次数": 30,
            "上榜后20天-平均涨幅": 6.0,
            "上榜后20天-上涨概率": 72.0,
        }
    ]


def _make_active_stock_rows():
    return [
        {
            "序号": 1,
            "证券代码": "600519",
            "证券简称": "贵州茅台",
            "最新价": 1510.0,
            "涨跌幅": 0.5,
            "最近上榜日": "2026-05-06",
            "上榜次数-总计": 50,
            "上榜次数-溢价": 5,
            "上榜次数-折价": 45,
            "总成交额": 500000.0,
            "折溢率": -0.03,
            "成交总额/流通市值": 0.12,
            "上榜日后平均涨跌幅-1日": 0.2,
            "上榜日后平均涨跌幅-5日": 1.5,
            "上榜日后平均涨跌幅-10日": 3.0,
            "上榜日后平均涨跌幅-20日": 5.0,
        }
    ]


def test_block_trade_daily_detail():
    uc = BlockTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_block_trade_daily.return_value = _make_daily_detail_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = BlockTradeRequest(include=["daily_detail"], trade_date="2026-05-06")
        result = uc.execute(req)
    assert result["daily_detail_count"] == 1
    item = result["daily_detail"][0]
    assert item["symbol"] == "600519.SH"
    assert item["price"] == 1500.0
    assert item["buyer_broker"] == "机构专用"


def test_block_trade_daily_stat():
    uc = BlockTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_block_trade_daily_stat.return_value = _make_daily_stat_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = BlockTradeRequest(include=["daily_stat"], trade_date="2026-05-06")
        result = uc.execute(req)
    assert result["daily_stat_count"] == 1
    item = result["daily_stat"][0]
    assert item["symbol"] == "600519.SH"
    assert item["discount_rate"] == -0.0066
    assert item["trade_count"] == 3


def test_block_trade_industry():
    uc = BlockTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_block_trade_industry.return_value = _make_industry_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = BlockTradeRequest(include=["industry_stat"])
        result = uc.execute(req)
    assert result["industry_stat_count"] == 1
    item = result["industry_stat"][0]
    assert item["industry"] == "白酒"
    assert item["premium_count"] == 1
    assert item["discount_count"] == 4


def test_block_trade_broker_rank():
    uc = BlockTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_block_trade_broker_rank.return_value = _make_broker_rank_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = BlockTradeRequest(include=["broker_rank"])
        result = uc.execute(req)
    assert result["broker_rank_count"] == 1
    item = result["broker_rank"][0]
    assert item["broker_name"] == "机构专用"
    assert item["win_rate_5d"] == 65.0


def test_block_trade_active_stock():
    uc = BlockTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_block_trade_active_stock.return_value = _make_active_stock_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = BlockTradeRequest(include=["active_stock"])
        result = uc.execute(req)
    assert result["active_stock_count"] == 1
    item = result["active_stock"][0]
    assert item["symbol"] == "600519.SH"
    assert item["total_listed_count"] == 50
    assert item["avg_return_5d"] == 1.5


def test_block_trade_top_n():
    uc = BlockTradeUseCase()
    mock_provider = MagicMock()
    rows = _make_daily_detail_rows() * 5
    mock_provider.get_block_trade_daily.return_value = rows
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = BlockTradeRequest(include=["daily_detail"], trade_date="2026-05-06", top_n=3)
        result = uc.execute(req)
    assert result["daily_detail_count"] == 3


def test_block_trade_summary():
    uc = BlockTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_block_trade_daily.return_value = _make_daily_detail_rows()
    mock_provider.get_block_trade_daily_stat.return_value = _make_daily_stat_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = BlockTradeRequest(include=["daily_detail", "daily_stat"], trade_date="2026-05-06")
        result = uc.execute(req)
    assert "大宗交易明细" in result["summary"]

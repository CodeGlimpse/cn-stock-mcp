"""Tests for fund_flow usecase with mocked provider."""
from unittest.mock import MagicMock, patch
import pytest

from openclaw_stock_mcp.app.usecases.fund_flow import FundFlowUseCase
from openclaw_stock_mcp.server.schemas import FundFlowRequest


def _make_market_rows():
    return [
        {"日期": "2026-05-12", "上证-收盘价": 4214.49, "上证-涨跌幅": -0.25, "深证-收盘价": 15824.92, "深证-涨跌幅": -0.47,
         "主力净流入-净额": -1.221e11, "主力净流入-净占比": -3.77,
         "超大单净流入-净额": -6.856e10, "超大单净流入-净占比": -2.11,
         "大单净流入-净额": -5.357e10, "大单净流入-净占比": -1.65,
         "中单净流入-净额": 2.992e10, "中单净流入-净占比": 0.92,
         "小单净流入-净额": 9.221e10, "小单净流入-净占比": 2.84},
        {"日期": "2026-05-13", "上证-收盘价": 4242.57, "上证-涨跌幅": 0.67, "深证-收盘价": 16089.75, "深证-涨跌幅": 1.67,
         "主力净流入-净额": 3.847e9, "主力净流入-净占比": 0.12,
         "超大单净流入-净额": 2.410e10, "超大单净流入-净占比": 0.74,
         "大单净流入-净额": -2.025e10, "大单净流入-净占比": -0.62,
         "中单净流入-净额": -2.055e10, "中单净流入-净占比": -0.63,
         "小单净流入-净额": 1.670e10, "小单净流入-净占比": 0.52},
    ]


def _make_industry_rows():
    return [
        {"序号": 1, "行业": "燃气", "行业指数": 2043.58, "行业-涨跌幅": 0.86, "流入资金": 11.46, "流出资金": 11.19, "净额": 0.27, "公司家数": 27, "领涨股": "贵州燃气", "领涨股-涨跌幅": 9.04, "当前价": 7.60},
        {"序号": 2, "行业": "港口航运", "行业指数": 1293.37, "行业-涨跌幅": 0.79, "流入资金": 36.44, "流出资金": 31.48, "净额": 4.96, "公司家数": 36, "领涨股": "招商南油", "领涨股-涨跌幅": 9.96, "当前价": 5.41},
        {"序号": 3, "行业": "养殖业", "行业指数": 3019.78, "行业-涨跌幅": 0.52, "流入资金": 24.81, "流出资金": 21.76, "净额": 3.05, "公司家数": 36, "领涨股": "天邦食品", "领涨股-涨跌幅": 10.04, "当前价": 3.07},
    ]


def _make_stock_rows():
    return [
        {"日期": "2026-05-12", "收盘价": 1354.55, "涨跌幅": -0.50,
         "主力净流入-净额": -1.123e9, "主力净流入-净占比": -16.31,
         "超大单净流入-净额": -2.418e8, "超大单净流入-净占比": -3.51,
         "大单净流入-净额": -8.811e8, "大单净流入-净占比": -12.80,
         "中单净流入-净额": 1.123e9, "中单净流入-净占比": 16.31,
         "小单净流入-净额": -1.842e5, "小单净流入-净占比": -0.0},
        {"日期": "2026-05-13", "收盘价": 1344.09, "涨跌幅": -0.77,
         "主力净流入-净额": -1.178e9, "主力净流入-净占比": -15.39,
         "超大单净流入-净额": -1.155e9, "超大单净流入-净占比": -15.09,
         "大单净流入-净额": -2.298e7, "大单净流入-净占比": -0.30,
         "中单净流入-净额": 1.178e9, "中单净流入-净占比": 15.39,
         "小单净流入-净额": -2.679e5, "小单净流入-净占比": -0.0},
    ]


def test_fund_flow_market():
    uc = FundFlowUseCase()
    mock_provider = MagicMock()
    mock_provider.get_market_fund_flow.return_value = _make_market_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = FundFlowRequest(include=["market"])
        result = uc.execute(req)
    assert result["market_count"] == 2
    item = result["market"][-1]
    assert item["date"] == "2026-05-13"
    assert item["main_net_inflow"] == pytest.approx(3.847e9, rel=1e-3)


def test_fund_flow_industry():
    uc = FundFlowUseCase()
    mock_provider = MagicMock()
    mock_provider.get_industry_fund_flow.return_value = _make_industry_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = FundFlowRequest(include=["industry"], sort_by="net_inflow", descending=True)
        result = uc.execute(req)
    assert result["industry_count"] == 3
    item = result["industry"][0]
    assert item["name"] == "港口航运"  # net_inflow 4.96 highest


def test_fund_flow_stock():
    uc = FundFlowUseCase()
    mock_provider = MagicMock()
    mock_provider.get_stock_fund_flow.return_value = _make_stock_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = FundFlowRequest(include=["stock"], symbol="600519")
        result = uc.execute(req)
    assert result["stock_count"] == 2
    item = result["stock"][-1]
    assert item["main_net_inflow"] == pytest.approx(-1.178e9, rel=1e-3)


def test_fund_flow_stock_no_symbol():
    uc = FundFlowUseCase()
    with pytest.raises(ValueError, match="symbol is required"):
        req = FundFlowRequest(include=["stock"])
        uc.execute(req)


def test_fund_flow_top_n():
    uc = FundFlowUseCase()
    mock_provider = MagicMock()
    mock_provider.get_industry_fund_flow.return_value = _make_industry_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = FundFlowRequest(include=["industry"], top_n=2)
        result = uc.execute(req)
    assert result["industry_count"] == 2


def test_fund_flow_uses_cache():
    uc = FundFlowUseCase()
    raw = _make_market_rows()
    uc.cache.set("fundflow:market", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = FundFlowRequest(include=["market"])
        result = uc.execute(req)
    mock_provider.get_market_fund_flow.assert_not_called()
    assert result["market_count"] == 2


def test_fund_flow_summary():
    uc = FundFlowUseCase()
    mock_provider = MagicMock()
    mock_provider.get_market_fund_flow.return_value = _make_market_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = FundFlowRequest(include=["market"])
        result = uc.execute(req)
    assert "全市场" in result["summary"]
    assert "净流入" in result["summary"] or "净流出" in result["summary"]

import pytest
from openclaw_stock_mcp.providers.adapters.akshare_capital_flow_adapters import (
    adapt_akshare_market_fund_flow,
    adapt_akshare_individual_fund_flow,
    adapt_akshare_sector_fund_flow,
    build_market_fund_flow_summary,
)
from openclaw_stock_mcp.app.models.capital_flow import (
    CapitalFlowRecord,
    MarketFundFlowSummary,
    SectorFundFlowItem,
)


# ---- adapt_akshare_market_fund_flow ----

def test_adapt_market_fund_flow_basic():
    row = {
        "日期": "2026-05-08",
        "上证-收盘价": 4179.95,
        "上证-涨跌幅": 0.00,
        "深证-收盘价": 15563.80,
        "深证-涨跌幅": -0.50,
        "主力净流入-净额": -5.519013e10,
        "主力净流入-净占比": -1.81,
        "超大单净流入-净额": -2.776193e10,
        "超大单净流入-净占比": -0.91,
        "大单净流入-净额": -2.742820e10,
        "大单净流入-净占比": -0.90,
        "中单净流入-净额": 1.093515e10,
        "中单净流入-净占比": 0.36,
        "小单净流入-净额": 4.425498e10,
        "小单净流入-净占比": 1.45,
    }
    rec = adapt_akshare_market_fund_flow(row)

    assert isinstance(rec, CapitalFlowRecord)
    assert rec.date == "2026-05-08"
    assert rec.close == 4179.95
    assert rec.change_percent == 0.00
    assert rec.main_net_inflow == pytest.approx(-5.519013e10)
    assert rec.main_net_inflow_pct == pytest.approx(-1.81)
    assert rec.super_large_net_inflow == pytest.approx(-2.776193e10)
    assert rec.super_large_net_inflow_pct == pytest.approx(-0.91)
    assert rec.large_net_inflow == pytest.approx(-2.742820e10)
    assert rec.large_net_inflow_pct == pytest.approx(-0.90)
    assert rec.medium_net_inflow == pytest.approx(1.093515e10)
    assert rec.medium_net_inflow_pct == pytest.approx(0.36)
    assert rec.small_net_inflow == pytest.approx(4.425498e10)
    assert rec.small_net_inflow_pct == pytest.approx(1.45)


def test_adapt_market_fund_flow_missing_fields():
    row = {"日期": "2026-05-08"}
    rec = adapt_akshare_market_fund_flow(row)
    assert rec.date == "2026-05-08"
    assert rec.close is None
    assert rec.main_net_inflow is None


# ---- adapt_akshare_individual_fund_flow ----

def test_adapt_individual_fund_flow_basic():
    row = {
        "日期": "2026-05-08",
        "收盘价": 11.30,
        "涨跌幅": -0.62,
        "主力净流入-净额": -13409438.0,
        "主力净流入-净占比": -1.48,
        "超大单净流入-净额": -128761930.0,
        "超大单净流入-净占比": -14.22,
        "大单净流入-净额": 115352492.0,
        "大单净流入-净占比": 12.74,
        "中单净流入-净额": -24692912.0,
        "中单净流入-净占比": -2.73,
        "小单净流入-净额": 38102359.0,
        "小单净流入-净占比": 4.21,
    }
    rec = adapt_akshare_individual_fund_flow(row)

    assert isinstance(rec, CapitalFlowRecord)
    assert rec.date == "2026-05-08"
    assert rec.close == 11.30
    assert rec.change_percent == pytest.approx(-0.62)
    assert rec.main_net_inflow == pytest.approx(-13409438.0)
    assert rec.main_net_inflow_pct == pytest.approx(-1.48)
    assert rec.super_large_net_inflow == pytest.approx(-128761930.0)
    assert rec.super_large_net_inflow_pct == pytest.approx(-14.22)
    assert rec.large_net_inflow == pytest.approx(115352492.0)
    assert rec.large_net_inflow_pct == pytest.approx(12.74)
    assert rec.medium_net_inflow == pytest.approx(-24692912.0)
    assert rec.medium_net_inflow_pct == pytest.approx(-2.73)
    assert rec.small_net_inflow == pytest.approx(38102359.0)
    assert rec.small_net_inflow_pct == pytest.approx(4.21)


def test_adapt_individual_fund_flow_missing_fields():
    row = {"日期": "2026-01-01", "收盘价": 10.0}
    rec = adapt_akshare_individual_fund_flow(row)
    assert rec.close == 10.0
    assert rec.main_net_inflow is None
    assert rec.change_percent is None


# ---- adapt_akshare_sector_fund_flow ----

def test_adapt_sector_fund_flow_basic():
    row = {
        "序号": 1,
        "行业": "军工装备",
        "行业指数": 2686.91,
        "行业-涨跌幅": 3.31,
        "流入资金": 296.00,
        "流出资金": 244.29,
        "净额": 51.71,
        "公司家数": 83,
        "领涨股": "电科蓝天",
        "领涨股-涨跌幅": 19.99,
        "当前价": 85.64,
    }
    item = adapt_akshare_sector_fund_flow(row)

    assert isinstance(item, SectorFundFlowItem)
    assert item.rank == 1
    assert item.sector_name == "军工装备"
    assert item.sector_index == pytest.approx(2686.91)
    assert item.sector_change_percent == pytest.approx(3.31)
    assert item.inflow == pytest.approx(296.00)
    assert item.outflow == pytest.approx(244.29)
    assert item.net_amount == pytest.approx(51.71)
    assert item.company_count == 83
    assert item.leading_stock == "电科蓝天"
    assert item.leading_stock_change_percent == pytest.approx(19.99)
    assert item.leading_stock_price == pytest.approx(85.64)


def test_adapt_sector_fund_flow_missing_fields():
    row = {"行业": "测试行业"}
    item = adapt_akshare_sector_fund_flow(row)
    assert item.sector_name == "测试行业"
    assert item.rank is None
    assert item.net_amount is None


# ---- build_market_fund_flow_summary ----

def test_build_summary_inflow():
    records = [
        CapitalFlowRecord(date="2026-05-06", main_net_inflow=2.0e10, main_net_inflow_pct=0.64),
        CapitalFlowRecord(date="2026-05-08", main_net_inflow=1.5e10, main_net_inflow_pct=0.50,
                          super_large_net_inflow=1e10, large_net_inflow=5e9,
                          medium_net_inflow=-3e9, small_net_inflow=-1.2e10),
    ]
    summary = build_market_fund_flow_summary(records)

    assert isinstance(summary, MarketFundFlowSummary)
    assert summary.main_inflow_direction == "inflow"
    assert summary.total_main_net_inflow == pytest.approx(1.5e10)
    assert summary.avg_main_net_inflow_pct == pytest.approx(0.50)
    assert summary.total_super_large_net_inflow == pytest.approx(1e10)
    assert summary.total_large_net_inflow == pytest.approx(5e9)


def test_build_summary_outflow():
    records = [
        CapitalFlowRecord(date="2026-05-08", main_net_inflow=-5.519013e10, main_net_inflow_pct=-1.81),
    ]
    summary = build_market_fund_flow_summary(records)
    assert summary.main_inflow_direction == "outflow"
    assert summary.total_main_net_inflow == pytest.approx(-5.519013e10)


def test_build_summary_neutral():
    records = [
        CapitalFlowRecord(date="2026-05-08", main_net_inflow=0.0, main_net_inflow_pct=0.0),
    ]
    summary = build_market_fund_flow_summary(records)
    assert summary.main_inflow_direction == "neutral"


def test_build_summary_empty():
    summary = build_market_fund_flow_summary([])
    assert summary.main_inflow_direction is None
    assert summary.total_main_net_inflow is None


# ---- Schema validation ----

def test_capital_flow_request_market_default():
    from openclaw_stock_mcp.server.schemas import CapitalFlowRequest

    req = CapitalFlowRequest()
    assert req.flow_type == "market"
    assert req.symbol is None
    assert req.limit == 60


def test_capital_flow_request_individual_requires_symbol():
    from openclaw_stock_mcp.server.schemas import CapitalFlowRequest

    with pytest.raises(ValueError, match="symbol is required"):
        CapitalFlowRequest(flow_type="individual")


def test_capital_flow_request_individual_with_symbol():
    from openclaw_stock_mcp.server.schemas import CapitalFlowRequest

    req = CapitalFlowRequest(flow_type="individual", symbol="000001.SZ")
    assert req.flow_type == "individual"
    assert req.symbol == "000001.SZ"


def test_capital_flow_request_date_validation():
    from openclaw_stock_mcp.server.schemas import CapitalFlowRequest

    with pytest.raises(ValueError, match="start_date must be"):
        CapitalFlowRequest(start_date="2026-05-10", end_date="2026-05-01")


def test_capital_flow_request_industry():
    from openclaw_stock_mcp.server.schemas import CapitalFlowRequest

    req = CapitalFlowRequest(flow_type="industry", top_n=10)
    assert req.flow_type == "industry"
    assert req.top_n == 10


def test_capital_flow_request_concept():
    from openclaw_stock_mcp.server.schemas import CapitalFlowRequest

    req = CapitalFlowRequest(flow_type="concept", sort_by="inflow", descending=False)
    assert req.flow_type == "concept"
    assert req.sort_by == "inflow"
    assert req.descending is False

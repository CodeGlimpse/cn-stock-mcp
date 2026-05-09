import pytest
from openclaw_stock_mcp.providers.adapters.akshare_northbound_adapters import (
    adapt_em_hist_row,
    build_daily_summary_from_flow_summary,
    adapt_em_hold_item,
    build_northbound_summary_text,
)
from openclaw_stock_mcp.app.models.northbound import (
    NorthboundFlowRecord,
    NorthboundDailySummary,
    NorthboundHoldItem,
)


# ---- adapt_em_hist_row ----

def test_adapt_hist_row_basic():
    row = {
        "日期": "2024-08-16",
        "当日成交净买额": -67.7499,
        "买入成交额": 426.4131,
        "卖出成交额": 494.1630,
        "历史累计净买额": 1.761522,
        "当日资金流入": -53.2235,
        "当日余额": 1093.2235,
        "持股市值": 1.910746e12,
        "领涨股": "深圳华强",
        "领涨股-涨跌幅": 10.02,
        "沪深300": 2879.43,
        "沪深300-涨跌幅": 0.07,
        "领涨股-代码": "000062.SZ",
    }
    rec = adapt_em_hist_row(row)

    assert isinstance(rec, NorthboundFlowRecord)
    assert rec.date == "2024-08-16"
    assert rec.net_buy_amount == pytest.approx(-67.7499)
    assert rec.buy_amount == pytest.approx(426.4131)
    assert rec.sell_amount == pytest.approx(494.1630)
    assert rec.cumulative_net_buy == pytest.approx(1.761522)
    assert rec.daily_inflow == pytest.approx(-53.2235)
    assert rec.balance == pytest.approx(1093.2235)
    assert rec.hold_market_cap == pytest.approx(1.910746e12)
    assert rec.leading_stock == "深圳华强"
    assert rec.leading_stock_change == pytest.approx(10.02)
    assert rec.leading_stock_code == "000062.SZ"
    assert rec.csi300 == pytest.approx(2879.43)
    assert rec.csi300_change == pytest.approx(0.07)


def test_adapt_hist_row_missing_fields():
    row = {"日期": "2024-08-16"}
    rec = adapt_em_hist_row(row)
    assert rec.date == "2024-08-16"
    assert rec.net_buy_amount is None
    assert rec.leading_stock is None


# ---- build_daily_summary_from_flow_summary ----

def test_build_daily_summary_basic():
    rows = [
        {
            "交易日": "2026-05-08",
            "类型": "沪港通",
            "板块": "沪股通",
            "资金方向": "北向",
            "交易状态": "3",
            "成交净买额": -5.23,
            "资金净流入": 0.0,
            "当日资金余额": 0.0,
            "上涨数": 860,
            "持平数": 43,
            "下跌数": 621,
            "相关指数": "上证指数",
            "指数涨跌幅": 0.00,
        },
        {
            "交易日": "2026-05-08",
            "类型": "深港通",
            "板块": "深股通",
            "资金方向": "北向",
            "交易状态": "3",
            "成交净买额": -3.15,
            "资金净流入": 0.0,
            "当日资金余额": 0.0,
            "上涨数": 1045,
            "持平数": 40,
            "下跌数": 626,
            "相关指数": "深证成指",
            "指数涨跌幅": -0.50,
        },
        {
            "交易日": "2026-05-08",
            "类型": "沪港通",
            "板块": "港股通(沪)",
            "资金方向": "南向",
            "交易状态": "3",
            "成交净买额": 101.256,
            "资金净流入": 420.0,
            "当日资金余额": 0.0,
            "上涨数": 257,
            "持平数": 27,
            "下跌数": 316,
            "相关指数": "恒生指数",
            "指数涨跌幅": -0.87,
        },
        {
            "交易日": "2026-05-08",
            "类型": "深港通",
            "板块": "港股通(深)",
            "资金方向": "南向",
            "交易状态": "3",
            "成交净买额": 30.428,
            "资金净流入": 420.0,
            "当日资金余额": 0.0,
            "上涨数": 257,
            "持平数": 27,
            "下跌数": 316,
            "相关指数": "恒生指数",
            "指数涨跌幅": -0.87,
        },
    ]
    summary = build_daily_summary_from_flow_summary(rows)

    assert isinstance(summary, NorthboundDailySummary)
    assert summary.trade_date == "2026-05-08"
    assert summary.sh_north_net_buy == pytest.approx(-5.23)
    assert summary.sz_north_net_buy == pytest.approx(-3.15)
    assert summary.total_north_net_buy == pytest.approx(-8.38)
    assert summary.sh_north_up_count == 860
    assert summary.sh_north_down_count == 621
    assert summary.sz_north_up_count == 1045
    assert summary.sz_north_down_count == 626


def test_build_daily_summary_empty():
    summary = build_daily_summary_from_flow_summary([])
    assert summary.trade_date is None
    assert summary.total_north_net_buy is None


def test_build_daily_summary_north_only():
    """When only northbound rows present (no southbound)."""
    rows = [
        {
            "交易日": "2026-05-08",
            "板块": "沪股通",
            "资金方向": "北向",
            "成交净买额": 10.5,
            "资金净流入": 10.5,
            "上涨数": 500,
            "下跌数": 300,
        },
    ]
    summary = build_daily_summary_from_flow_summary(rows)
    assert summary.sh_north_net_buy == pytest.approx(10.5)
    assert summary.total_north_net_buy == pytest.approx(10.5)


# ---- adapt_em_hold_item ----

def test_adapt_hold_item_basic():
    row = {
        "序号": 1,
        "代码": "600050",
        "名称": "中国联通",
        "今日收盘价": 4.73,
        "今日涨跌幅": 4.42,
        "今日持股-股数": 115290.52,
        "今日持股-市值": 545324.17,
        "今日持股-占流通股比": 3.72,
        "今日持股-占总股本比": 3.63,
        "今日增持估计-股数": 9170.78,
        "今日增持估计-市值": 42969.67,
        "今日增持估计-市值增幅": 8.64,
        "今日增持估计-占流通股比": 3.06,
        "今日增持估计-占总股本比": 2.98,
        "所属板块": "通信服务",
        "日期": "2024-08-16",
    }
    item = adapt_em_hold_item(row)

    assert isinstance(item, NorthboundHoldItem)
    assert item.symbol == "600050.SH"
    assert item.name == "中国联通"
    assert item.price == pytest.approx(4.73)
    assert item.change_percent == pytest.approx(4.42)
    assert item.hold_shares == pytest.approx(115290.52)
    assert item.hold_market_cap == pytest.approx(545324.17)
    assert item.hold_pct_float == pytest.approx(3.72)
    assert item.increase_shares == pytest.approx(9170.78)
    assert item.increase_market_cap == pytest.approx(42969.67)
    assert item.increase_pct == pytest.approx(8.64)
    assert item.sector == "通信服务"
    assert item.date == "2024-08-16"


def test_adapt_hold_item_sz_code():
    row = {"代码": "000001", "名称": "平安银行"}
    item = adapt_em_hold_item(row)
    assert item.symbol == "000001.SZ"


def test_adapt_hold_item_missing_fields():
    row = {"代码": "600519"}
    item = adapt_em_hold_item(row)
    assert item.price is None
    assert item.sector is None


# ---- build_northbound_summary_text ----

def test_summary_text_inflow():
    daily = NorthboundDailySummary(
        trade_date="2026-05-08",
        sh_north_net_buy=15.3,
        sz_north_net_buy=8.7,
        total_north_net_buy=24.0,
        sh_north_up_count=860,
        sh_north_down_count=621,
    )
    history = [NorthboundFlowRecord(date="2026-05-08", hold_market_cap=2.1e12, leading_stock="贵州茅台")]
    text = build_northbound_summary_text(daily, history, [])
    assert "净流入24.00亿" in text
    assert "沪股通15.30亿" in text
    assert "深股通8.70亿" in text
    assert "持股市值" in text


def test_summary_text_outflow():
    daily = NorthboundDailySummary(
        trade_date="2026-05-08",
        sh_north_net_buy=-5.23,
        sz_north_net_buy=-3.15,
        total_north_net_buy=-8.38,
    )
    text = build_northbound_summary_text(daily, [], [])
    assert "净流出" in text


def test_summary_text_with_holdings():
    daily = NorthboundDailySummary(trade_date="2026-05-08", total_north_net_buy=10.0)
    holdings = [
        NorthboundHoldItem(symbol="600519.SH", name="贵州茅台", increase_pct=3.5),
        NorthboundHoldItem(symbol="000858.SZ", name="五粮液", increase_pct=2.1),
        NorthboundHoldItem(symbol="600036.SH", name="招商银行", increase_pct=1.8),
    ]
    text = build_northbound_summary_text(daily, [], holdings)
    assert "增持前列" in text
    assert "贵州茅台" in text


def test_summary_text_empty():
    text = build_northbound_summary_text(None, [], [])
    assert "暂无" in text


# ---- Schema validation ----

def test_northbound_request_defaults():
    from openclaw_stock_mcp.server.schemas import NorthboundRequest

    req = NorthboundRequest()
    assert req.include == ["daily_summary", "history", "holdings"]
    assert req.history_n == 30
    assert req.hold_indicator == "今日排行"
    assert req.hold_top_n == 20


def test_northbound_request_history_only():
    from openclaw_stock_mcp.server.schemas import NorthboundRequest

    req = NorthboundRequest(include=["history"], history_n=60)
    assert req.include == ["history"]
    assert req.history_n == 60


def test_northbound_request_empty_include_fails():
    from openclaw_stock_mcp.server.schemas import NorthboundRequest

    with pytest.raises(ValueError, match="at least one"):
        NorthboundRequest(include=[])


def test_northbound_request_dedup_include():
    from openclaw_stock_mcp.server.schemas import NorthboundRequest

    req = NorthboundRequest(include=["daily_summary", "daily_summary", "holdings"])
    assert req.include == ["daily_summary", "holdings"]

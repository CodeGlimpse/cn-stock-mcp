"""Tests for akshare_etf_snapshot_adapters: adapt, sort, summary."""
from __future__ import annotations

import pytest

from cn_stock_mcp.app.models.etf_snapshot import (
    ETFNAVItem,
    ETFScaleItem,
    ETFSpotItem,
)
from cn_stock_mcp.providers.adapters.akshare_etf_snapshot_adapters import (
    adapt_etf_nav_row,
    adapt_etf_scale_row,
    adapt_etf_spot_row,
    build_etf_snapshot_summary_text,
)


# ── ETFSpot ───────────────────────────────────────────────────────

class TestAdaptETFSpotRow:
    def test_basic_sz(self):
        row = {
            "代码": "159300",
            "名称": "沪深300ETF博时",
            "最新价": 4.125,
            "IOPV实时估值": 4.130,
            "基金折价率": 0.12,
            "涨跌额": 0.025,
            "涨跌幅": 0.61,
            "成交量": 5e6,
            "成交额": 2.06e9,
            "开盘价": 4.10,
            "最高价": 4.14,
            "最低价": 4.09,
            "昨收": 4.10,
            "振幅": 1.22,
            "换手率": 3.5,
            "量比": 1.2,
            "主力净流入-净额": 5e7,
            "主力净流入-净占比": 2.43,
            "超大单净流入-净额": 3e7,
            "大单净流入-净额": 2e7,
            "最新份额": 5e9,
            "流通市值": 2.06e10,
            "总市值": 2.06e10,
            "数据日期": "2025-05-08",
        }
        item = adapt_etf_spot_row(row)
        assert item.symbol == "159300.SZ"
        assert item.name == "沪深300ETF博时"
        assert item.price == pytest.approx(4.125)
        assert item.iopv == pytest.approx(4.130)
        assert item.discount_rate == pytest.approx(0.12)
        assert item.change_percent == pytest.approx(0.61)
        assert item.main_net_inflow == pytest.approx(5e7)
        assert item.trade_date == "2025-05-08"

    def test_sh_symbol(self):
        row = {
            "代码": "510300",
            "名称": "沪深300ETF",
            "最新价": 4.0,
            "IOPV实时估值": 4.01,
            "基金折价率": -0.25,
            "涨跌额": 0.02,
            "涨跌幅": 0.50,
            "成交量": 1e7,
            "成交额": 4e9,
            "开盘价": 3.98,
            "最高价": 4.02,
            "最低价": 3.97,
            "昨收": 3.98,
            "振幅": 1.26,
            "换手率": 5.0,
            "量比": 0.9,
            "主力净流入-净额": -3e7,
            "主力净流入-净占比": -0.75,
            "超大单净流入-净额": -2e7,
            "大单净流入-净额": -1e7,
            "最新份额": 1e10,
            "流通市值": 4e10,
            "总市值": 4e10,
            "数据日期": "2025-05-08",
        }
        item = adapt_etf_spot_row(row)
        assert item.symbol == "510300.SH"
        assert item.discount_rate == pytest.approx(-0.25)

    def test_nan_values(self):
        row = {
            "代码": "510300", "名称": "X",
            "最新价": float("nan"), "IOPV实时估值": float("nan"),
            "基金折价率": float("nan"), "涨跌额": float("nan"),
            "涨跌幅": float("nan"), "成交量": float("nan"),
            "成交额": float("nan"), "开盘价": float("nan"),
            "最高价": float("nan"), "最低价": float("nan"),
            "昨收": float("nan"), "振幅": float("nan"),
            "换手率": float("nan"), "量比": float("nan"),
            "主力净流入-净额": float("nan"), "主力净流入-净占比": float("nan"),
            "超大单净流入-净额": float("nan"), "大单净流入-净额": float("nan"),
            "最新份额": float("nan"), "流通市值": float("nan"),
            "总市值": float("nan"), "数据日期": "",
        }
        item = adapt_etf_spot_row(row)
        assert item.price is None
        assert item.iopv is None
        assert item.discount_rate is None


# ── ETFScale ──────────────────────────────────────────────────────

class TestAdaptETFScaleRow:
    def test_basic(self):
        row = {
            "序号": 1,
            "基金代码": "510010",
            "基金简称": "治理ETF",
            "ETF类型": "单市",
            "统计日期": "2025-01-15",
            "基金份额": 201524400.0,
        }
        item = adapt_etf_scale_row(row)
        assert item.symbol == "510010.SH"
        assert item.name == "治理ETF"
        assert item.etf_type == "单市"
        assert item.shares == pytest.approx(201524400.0)


# ── ETFNAV ────────────────────────────────────────────────────────

class TestAdaptETFNAVRow:
    def test_basic(self):
        row = {
            "净值日期": "2025-05-08",
            "单位净值": 3.9514,
            "累计净值": 1.7139,
            "日增长率": 0.56,
            "申购状态": "场内买入",
            "赎回状态": "场内卖出",
        }
        item = adapt_etf_nav_row(row)
        assert item.date == "2025-05-08"
        assert item.nav == pytest.approx(3.9514)
        assert item.acc_nav == pytest.approx(1.7139)
        assert item.daily_growth == pytest.approx(0.56)
        assert item.purchase_status == "场内买入"


# ── Summary ───────────────────────────────────────────────────────

class TestBuildETFSnapshotSummaryText:
    def test_spot_with_inflow(self):
        items = [
            ETFSpotItem(symbol="510300.SH", name="沪深300ETF", main_net_inflow=5e7),
            ETFSpotItem(symbol="510500.SH", name="中证500ETF", main_net_inflow=-2e7, discount_rate=0.5),
        ]
        text = build_etf_snapshot_summary_text(items, [], [])
        assert "ETF快照2只" in text
        assert "主力净流入最高沪深300ETF" in text
        assert "溢价1只" in text

    def test_nav(self):
        nav = [
            ETFNAVItem(date="2025-05-08", nav=3.9514, daily_growth=0.56),
        ]
        text = build_etf_snapshot_summary_text([], [], nav)
        assert "最新净值3.9514" in text
        assert "日增长0.56%" in text

    def test_empty(self):
        text = build_etf_snapshot_summary_text([], [], [])
        assert "暂无" in text

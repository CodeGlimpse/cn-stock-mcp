"""Tests for akshare_convertible_bond_adapters: adapt, sort, summary."""
from __future__ import annotations

import pytest

from openclaw_stock_mcp.app.models.convertible_bond import (
    CBIndexPoint,
    CBRedeemItem,
    CBSpotItem,
)
from openclaw_stock_mcp.providers.adapters.akshare_convertible_bond_adapters import (
    adapt_cb_index_row,
    adapt_cb_redeem_row,
    adapt_cb_spot_row,
    build_cb_summary_text,
)


# ── CBSpot ────────────────────────────────────────────────────────

class TestAdaptCBSpotRow:
    def test_basic(self):
        row = {
            "代码": "123269",
            "转债名称": "金杨转债",
            "现价": 100.0,
            "涨跌幅": 0.0,
            "正股代码": "301210",
            "正股名称": "金杨精密",
            "正股价": 42.79,
            "正股涨跌": 3.48,
            "正股PB": 2.60,
            "转股价": 39.8,
            "转股价值": 107.51,
            "转股溢价率": -6.99,
            "债券评级": "AA-",
            "回售触发价": 27.86,
            "强赎触发价": 51.74,
            "转债占比": 52.7,
            "到期时间": "2032-04-19",
            "剩余年限": 5.953,
            "剩余规模": 9.800,
            "成交额": 0.0,
            "换手率": 0.0,
            "到期税前收益": 2.21,
            "双低": 93.01,
        }
        item = adapt_cb_spot_row(row)
        assert item.symbol == "123269.SZ"
        assert item.name == "金杨转债"
        assert item.price == pytest.approx(100.0)
        assert item.conv_premium == pytest.approx(-6.99)
        assert item.double_low == pytest.approx(93.01)
        assert item.stock_symbol == "301210.SZ"
        assert item.rating == "AA-"
        assert item.ytm == pytest.approx(2.21)

    def test_sh_symbol(self):
        row = {
            "代码": "110085",
            "转债名称": "X转债",
            "现价": 120.0,
            "涨跌幅": 1.5,
            "正股代码": "600519",
            "正股名称": "贵州茅台",
            "正股价": 1800.0,
            "正股涨跌": 2.0,
            "正股PB": 10.0,
            "转股价": 1500.0,
            "转股价值": 120.0,
            "转股溢价率": 0.0,
            "债券评级": "AAA",
            "回售触发价": 1050.0,
            "强赎触发价": 1950.0,
            "转债占比": 1.0,
            "到期时间": "2030-01-01",
            "剩余年限": 4.5,
            "剩余规模": 50.0,
            "成交额": 1e8,
            "换手率": 5.0,
            "到期税前收益": 1.5,
            "双低": 120.0,
        }
        item = adapt_cb_spot_row(row)
        assert item.symbol == "110085.SH"
        assert item.stock_symbol == "600519.SH"

    def test_nan_values(self):
        row = {
            "代码": "123269", "转债名称": "X", "现价": float("nan"),
            "涨跌幅": float("nan"), "正股代码": "301210", "正股名称": "X",
            "正股价": float("nan"), "正股涨跌": float("nan"),
            "正股PB": float("nan"), "转股价": float("nan"),
            "转股价值": float("nan"), "转股溢价率": float("nan"),
            "债券评级": "", "回售触发价": float("nan"), "强赎触发价": float("nan"),
            "转债占比": float("nan"), "到期时间": "",
            "剩余年限": float("nan"), "剩余规模": float("nan"),
            "成交额": float("nan"), "换手率": float("nan"),
            "到期税前收益": float("nan"), "双低": float("nan"),
        }
        item = adapt_cb_spot_row(row)
        assert item.price is None
        assert item.conv_premium is None
        assert item.double_low is None


# ── CBRedeem ──────────────────────────────────────────────────────

class TestAdaptCBRedeemRow:
    def test_basic(self):
        row = {
            "代码": "118004",
            "名称": "博瑞转债",
            "现价": 190.941,
            "正股代码": "688166",
            "正股名称": "博瑞医药",
            "规模": 4.65,
            "剩余规模": 2.165,
            "转股起始日": "2022-07-11",
            "最后交易日": "2026-05-18",
            "到期日": "2028-01-04",
            "转股价": 34.74,
            "强赎触发比": 130,
            "强赎触发价": 45.162,
            "正股价": 66.64,
            "强赎价": 100.945,
            "强赎天计数": "21/15 | 30",
            "强赎条款": "如果公司股票连续三十个交易日中至少有十五个交易日的收盘价不低于当期转股价格的 130%",
            "强赎状态": "已公告强赎",
        }
        item = adapt_cb_redeem_row(row)
        assert item.symbol == "118004.SH"
        assert item.stock_symbol == "688166.SH"
        assert item.call_status == "已公告强赎"
        assert item.call_day_count == "21/15 | 30"


# ── CBIndex ──────────────────────────────────────────────────────

class TestAdaptCBIndexRow:
    def test_basic(self):
        row = {
            "price_dt": "2025-05-08",
            "price": 2100.5,
            "amount": 500e8,
            "volume": 2000e8,
            "count": 600,
        }
        item = adapt_cb_index_row(row)
        assert item.date == "2025-05-08"
        assert item.price == pytest.approx(2100.5)
        assert item.count == 600


# ── Summary ───────────────────────────────────────────────────────

class TestBuildCBSummaryText:
    def test_spot_with_double_low(self):
        items = [
            CBSpotItem(symbol="123269.SZ", name="金杨转债", double_low=93.01),
            CBSpotItem(symbol="110085.SH", name="X转债", conv_premium=-2.0, double_low=118.0),
        ]
        text = build_cb_summary_text(items, [], [])
        assert "可转债2只" in text
        assert "双低最低金杨转债" in text
        assert "负溢价1只" in text

    def test_redeem(self):
        redeem = [
            CBRedeemItem(symbol="118004.SH", name="博瑞转债", call_status="已公告强赎"),
            CBRedeemItem(symbol="128001.SZ", name="Y转债", call_status="远离强赎"),
        ]
        text = build_cb_summary_text([], redeem, [])
        assert "强赎监控2只" in text
        assert "已公告强赎1只" in text

    def test_index(self):
        index = [
            CBIndexPoint(date="2025-05-08", price=2100.5),
        ]
        text = build_cb_summary_text([], [], index)
        assert "转债指数2100.50" in text

    def test_empty(self):
        text = build_cb_summary_text([], [], [])
        assert "暂无" in text

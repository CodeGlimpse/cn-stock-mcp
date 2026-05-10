"""Tests for akshare_derivatives_data_adapters: adapt, summary."""
from __future__ import annotations

import pytest

from openclaw_stock_mcp.app.models.derivatives_data import (
    FuturesHistItem,
    FuturesSpotItem,
    OptionContractItem,
    QVIXItem,
)
from openclaw_stock_mcp.providers.adapters.akshare_derivatives_data_adapters import (
    adapt_futures_hist_row,
    adapt_futures_spot_row,
    adapt_option_sse_row,
    adapt_option_szse_row,
    adapt_qvix_row,
    build_derivatives_summary_text,
)


# ── FuturesSpot ───────────────────────────────────────────────────

class TestAdaptFuturesSpotRow:
    def test_basic(self):
        row = {
            "symbol": "TA0",
            "exchange": "czce",
            "name": "PTA连续",
            "trade": 6352.0,
            "settlement": 0.0,
            "presettlement": 6386.0,
            "open": 6362.0,
            "high": 6370.0,
            "low": 6308.0,
            "close": 0.0,
            "volume": 268143,
            "position": 1060455,
            "changepercent": -0.005324,
            "tradedate": "2025-05-08",
            "ticktime": "23:00:00",
        }
        item = adapt_futures_spot_row(row)
        assert item.symbol == "TA0"
        assert item.exchange == "czce"
        assert item.name == "PTA连续"
        assert item.price == pytest.approx(6352.0)
        assert item.prev_settlement == pytest.approx(6386.0)
        assert item.volume == pytest.approx(268143)
        assert item.position == pytest.approx(1060455)
        assert item.change_percent == pytest.approx(-0.005324)


# ── FuturesHist ───────────────────────────────────────────────────

class TestAdaptFuturesHistRow:
    def test_basic(self):
        row = {
            "date": "2026-05-08",
            "open": 3272.0,
            "high": 3285.0,
            "low": 3261.0,
            "close": 3263.0,
            "volume": 824912,
            "hold": 2144541,
            "settle": 3275.0,
        }
        item = adapt_futures_hist_row(row)
        assert item.date == "2026-05-08"
        assert item.open == pytest.approx(3272.0)
        assert item.close == pytest.approx(3263.0)
        assert item.position == pytest.approx(2144541)
        assert item.settle == pytest.approx(3275.0)


# ── Option SSE ───────────────────────────────────────────────────

class TestAdaptOptionSSERow:
    def test_basic(self):
        row = {
            "合约编码": "10011381",
            "合约交易代码": "510050C2605M02700",
            "合约简称": "50ETF购5月2700",
            "标的券名称及代码": "50ETF(510050)",
            "类型": "认购",
            "行权价": 2.700,
            "合约单位": 10000,
            "到期日": "20260527",
        }
        item = adapt_option_sse_row(row)
        assert item.code == "10011381"
        assert item.name == "50ETF购5月2700"
        assert item.underlying == "50ETF(510050)"
        assert item.option_type == "认购"
        assert item.strike == pytest.approx(2.700)
        assert item.unit == 10000
        assert item.exchange == "SSE"


# ── Option SZSE ───────────────────────────────────────────────────

class TestAdaptOptionSZSERow:
    def test_basic(self):
        row = {
            "合约编码": "90006441",
            "合约代码": "159901C2606M003100A",
            "合约简称": "深证100ETF购6月3025A",
            "标的证券简称(代码)": "深证100ETF易方达(159901)",
            "合约类型": "认购",
            "行权价": 3.025,
            "合约单位": 10248,
            "到期日": "2026-06-24",
            "涨停价格": 1.2686,
            "跌停价格": 0.4900,
            "前结算价": 0.8793,
            "合约总持仓": 21.0,
        }
        item = adapt_option_szse_row(row)
        assert item.code == "90006441"
        assert item.underlying == "深证100ETF易方达(159901)"
        assert item.exchange == "SZSE"
        assert item.upper_limit == pytest.approx(1.2686)
        assert item.prev_settle == pytest.approx(0.8793)
        assert item.total_position == pytest.approx(21.0)


# ── QVIX ──────────────────────────────────────────────────────────

class TestAdaptQVIXRow:
    def test_basic(self):
        row = {
            "date": "2026-04-30",
            "open": 14.10,
            "high": 15.00,
            "low": 14.00,
            "close": 14.57,
        }
        item = adapt_qvix_row(row)
        assert item.date == "2026-04-30"
        assert item.open == pytest.approx(14.10)
        assert item.close == pytest.approx(14.57)


# ── Summary ───────────────────────────────────────────────────────

class TestBuildDerivativesSummaryText:
    def test_futures_spot(self):
        items = [
            FuturesSpotItem(symbol="TA0", name="PTA连续", change_percent=-0.5),
            FuturesSpotItem(symbol="RB0", name="螺纹钢主力", change_percent=1.2),
        ]
        text = build_derivatives_summary_text(items, [], [], [])
        assert "期货主力2只" in text
        assert "涨1跌1" in text

    def test_futures_hist(self):
        hist = [
            FuturesHistItem(date="2026-05-08", close=3263.0),
        ]
        text = build_derivatives_summary_text([], hist, [], [])
        assert "最新收盘3263.0" in text

    def test_option_list(self):
        opts = [
            OptionContractItem(code="1", option_type="认购"),
            OptionContractItem(code="2", option_type="认沽"),
        ]
        text = build_derivatives_summary_text([], [], opts, [])
        assert "期权合约2只" in text
        assert "购1/沽1" in text

    def test_qvix(self):
        qvix = [
            QVIXItem(date="2026-04-30", close=14.57),
        ]
        text = build_derivatives_summary_text([], [], [], qvix)
        assert "QVIX14.57" in text

    def test_empty(self):
        text = build_derivatives_summary_text([], [], [], [])
        assert "暂无" in text

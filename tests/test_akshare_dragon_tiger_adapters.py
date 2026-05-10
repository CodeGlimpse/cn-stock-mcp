"""Tests for akshare_dragon_tiger_adapters: adapt, sort, summary."""
from __future__ import annotations

import pandas as pd
import pytest

from openclaw_stock_mcp.app.models.dragon_tiger import (
    ActiveBrokerItem,
    BrokerRankItem,
    DailyDetailItem,
    InstitutionItem,
    StockStatItem,
)
from openclaw_stock_mcp.providers.adapters.akshare_dragon_tiger_adapters import (
    adapt_active_broker_row,
    adapt_broker_rank_row,
    adapt_daily_detail_row,
    adapt_institution_row,
    adapt_stock_stat_row,
    build_dragon_tiger_summary_text,
)


# ── DailyDetail ───────────────────────────────────────────────────

class TestAdaptDailyDetailRow:
    def test_basic(self):
        row = {
            "序号": 1,
            "代码": "000062",
            "名称": "深圳华强",
            "上榜日": "2025-05-06",
            "解读": "主力做T，成功率32.58%",
            "收盘价": 28.18,
            "涨跌幅": 9.9922,
            "龙虎榜净买额": 110127833.88,
            "龙虎榜买入额": 227273024.58,
            "龙虎榜卖出额": 117145190.7,
            "龙虎榜成交额": 344418215.28,
            "市场总成交额": 1731125034.0,
            "净买额占总成交比": 6.3616,
            "成交额占总成交比": 19.8956,
            "换手率": 6.174,
            "流通市值": 29446099220.0,
            "上榜原因": "日涨幅偏离值达到7%的前5只证券",
            "上榜后1日": 2.555,
            "上榜后2日": -1.016,
            "上榜后5日": -0.730,
            "上榜后10日": -3.087,
        }
        item = adapt_daily_detail_row(row)
        assert item.symbol == "000062.SZ"
        assert item.name == "深圳华强"
        assert item.trade_date == "2025-05-06"
        assert item.close == pytest.approx(28.18)
        assert item.change_percent == pytest.approx(9.9922)
        assert item.net_buy_amount == pytest.approx(110127833.88)
        assert item.reason == "日涨幅偏离值达到7%的前5只证券"
        assert item.interpretation == "主力做T，成功率32.58%"
        assert item.after_1d == pytest.approx(2.555)
        assert item.after_10d == pytest.approx(-3.087)

    def test_sh_symbol(self):
        row = {"代码": "600519", "名称": "贵州茅台", "上榜日": "2025-05-06",
               "收盘价": 1800.0, "涨跌幅": 5.0, "龙虎榜净买额": 1e8,
               "龙虎榜买入额": 2e8, "龙虎榜卖出额": 1e8, "龙虎榜成交额": 3e8,
               "市场总成交额": 5e9, "净买额占总成交比": 2.0, "成交额占总成交比": 6.0,
               "换手率": 1.5, "流通市值": 2e12, "上榜原因": "test",
               "上榜后1日": None, "上榜后2日": None, "上榜后5日": None, "上榜后10日": None,
               "解读": ""}
        item = adapt_daily_detail_row(row)
        assert item.symbol == "600519.SH"

    def test_nan_values(self):
        row = {
            "代码": "000001", "名称": "X", "上榜日": "",
            "收盘价": float("nan"), "涨跌幅": float("nan"),
            "龙虎榜净买额": float("nan"), "龙虎榜买入额": float("nan"),
            "龙虎榜卖出额": float("nan"), "龙虎榜成交额": float("nan"),
            "市场总成交额": float("nan"), "净买额占总成交比": float("nan"),
            "成交额占总成交比": float("nan"), "换手率": float("nan"),
            "流通市值": float("nan"), "上榜原因": "",
            "上榜后1日": float("nan"), "上榜后2日": float("nan"),
            "上榜后5日": float("nan"), "上榜后10日": float("nan"),
            "解读": "",
        }
        item = adapt_daily_detail_row(row)
        assert item.close is None
        assert item.net_buy_amount is None
        assert item.after_1d is None


# ── Institution ───────────────────────────────────────────────────

class TestAdaptInstitutionRow:
    def test_basic(self):
        row = {
            "序号": 1, "代码": "002094", "名称": "青岛金王",
            "收盘价": 7.61, "涨跌幅": 9.9711,
            "买方机构数": 4, "卖方机构数": 0,
            "机构买入总额": 169893700.0, "机构卖出总额": 14103668.05,
            "机构买入净额": 155790031.95, "市场总成交额": 1006124647.0,
            "机构净买额占总成交额比": 15.484, "换手率": 19.5999,
            "流通市值": 5254000000.0,
            "上榜原因": "日涨幅偏离值达到7%的前5只证券",
            "上榜日期": "2025-05-06",
        }
        item = adapt_institution_row(row)
        assert item.symbol == "002094.SZ"
        assert item.buy_inst_count == 4
        assert item.sell_inst_count == 0
        assert item.inst_buy_total == pytest.approx(169893700.0)
        assert item.inst_net_buy == pytest.approx(155790031.95)
        assert item.trade_date == "2025-05-06"


# ── ActiveBroker ──────────────────────────────────────────────────

class TestAdaptActiveBrokerRow:
    def test_basic(self):
        row = {
            "序号": 1,
            "营业部名称": "中信证券股份有限公司上海分公司",
            "上榜日": "2025-05-06",
            "买入个股数": 11, "卖出个股数": 5,
            "买入总金额": 301755900.0, "卖出总金额": 123942200.0,
            "总买卖净额": 177813700.0,
            "买入股票": "曙光股份 华电辽能 龙溪股份",
            "营业部代码": "10135341",
        }
        item = adapt_active_broker_row(row)
        assert item.broker_name == "中信证券股份有限公司上海分公司"
        assert item.buy_count == 11
        assert item.buy_stocks == "曙光股份 华电辽能 龙溪股份"
        assert item.broker_code == "10135341"


# ── BrokerRank ────────────────────────────────────────────────────

class TestAdaptBrokerRankRow:
    def test_basic(self):
        row = {
            "序号": 1,
            "营业部名称": "东方财富拉萨团结路",
            "上榜后1天-买入次数": 50,
            "上榜后1天-平均涨幅": 1.23,
            "上榜后1天-上涨概率": 55.0,
            "上榜后2天-买入次数": 48,
            "上榜后2天-平均涨幅": 0.87,
            "上榜后2天-上涨概率": 52.0,
            "上榜后5天-买入次数": 45,
            "上榜后5天-平均涨幅": 2.15,
            "上榜后5天-上涨概率": 58.0,
            "上榜后10天-买入次数": 40,
            "上榜后10天-平均涨幅": 3.40,
            "上榜后10天-上涨概率": 60.0,
        }
        item = adapt_broker_rank_row(row)
        assert item.broker_name == "东方财富拉萨团结路"
        assert item.after_1d_count == 50
        assert item.after_1d_avg_change == pytest.approx(1.23)
        assert item.after_1d_up_prob == pytest.approx(55.0)
        assert item.after_10d_up_prob == pytest.approx(60.0)


# ── StockStat ─────────────────────────────────────────────────────

class TestAdaptStockStatRow:
    def test_basic(self):
        row = {
            "序号": 1, "代码": "300999", "名称": "金龙鱼",
            "最近上榜日": "2025-04-30",
            "收盘价": 42.5, "涨跌幅": 3.21,
            "上榜次数": 5,
            "龙虎榜成交金额": 5e8,
            "龙虎榜净买额": 1.5e8,
            "上榜后1日": 1.2, "上榜后2日": -0.5,
            "上榜后5日": 2.3, "上榜后10日": -1.1,
        }
        item = adapt_stock_stat_row(row)
        assert item.symbol == "300999.SZ"
        assert item.listed_count == 5
        assert item.after_1d_avg == pytest.approx(1.2)


# ── Summary ───────────────────────────────────────────────────────

class TestBuildDragonTigerSummaryText:
    def test_daily_detail_with_net_buy(self):
        items = [
            DailyDetailItem(symbol="000062.SZ", name="深圳华强", net_buy_amount=1.1e8),
            DailyDetailItem(symbol="600519.SH", name="贵州茅台", net_buy_amount=-2e8),
        ]
        text = build_dragon_tiger_summary_text(items, [], [], [], [])
        assert "上榜2只" in text
        assert "净买入最高深圳华强" in text
        assert "净卖出最高贵州茅台" in text

    def test_institution(self):
        inst = [
            InstitutionItem(symbol="002094.SZ", name="青岛金王", inst_net_buy=1.5e8),
        ]
        text = build_dragon_tiger_summary_text([], inst, [], [], [])
        assert "机构参与1只" in text
        assert "机构净买入青岛金王" in text

    def test_empty(self):
        text = build_dragon_tiger_summary_text([], [], [], [], [])
        assert "暂无" in text

    def test_broker_rank(self):
        rank = [
            BrokerRankItem(broker_name="东方财富拉萨", after_1d_up_prob=55.0),
        ]
        text = build_dragon_tiger_summary_text([], [], [], rank, [])
        assert "胜率最高" in text

    def test_stock_stat(self):
        stat = [
            StockStatItem(symbol="300999.SZ", name="金龙鱼", listed_count=8),
        ]
        text = build_dragon_tiger_summary_text([], [], [], [], stat)
        assert "最频繁上榜金龙鱼" in text

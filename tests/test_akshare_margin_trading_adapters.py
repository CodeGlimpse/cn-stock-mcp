"""Tests for akshare_margin_trading_adapters: adapt, sort, summary."""
from __future__ import annotations

import pytest

from cn_stock_mcp.app.models.margin_trading import (
    MarginDetailItem,
    MarginSummaryItem,
)
from cn_stock_mcp.providers.adapters.akshare_margin_trading_adapters import (
    adapt_margin_sse_detail_row,
    adapt_margin_sse_summary_row,
    adapt_margin_szse_detail_row,
    adapt_margin_szse_summary_row,
    build_margin_summary_text,
)


# ── SSE Summary ──────────────────────────────────────────────────

class TestAdaptMarginSSESummaryRow:
    def test_basic(self):
        row = {
            "信用交易日期": "20250508",
            "融资余额": 911157862069,
            "融资买入额": 51393706214,
            "融券余量": 1927674798,
            "融券余量金额": 7986207629,
            "融券卖出量": 67795171,
            "融资融券余额": 919144069698,
        }
        item = adapt_margin_sse_summary_row(row)
        assert item.trade_date == "2025-05-08"
        assert item.financing_balance == pytest.approx(911157862069)
        assert item.financing_buy == pytest.approx(51393706214)
        assert item.securities_volume == pytest.approx(1927674798)
        assert item.total_balance == pytest.approx(919144069698)
        assert item.exchange == "SSE"

    def test_date_format(self):
        row = {"信用交易日期": "20250506", "融资余额": 0, "融资买入额": 0,
               "融券余量": 0, "融券余量金额": 0, "融券卖出量": 0, "融资融券余额": 0}
        item = adapt_margin_sse_summary_row(row)
        assert item.trade_date == "2025-05-06"


# ── SZSE Summary ──────────────────────────────────────────────────

class TestAdaptMarginSZSESummaryRow:
    def test_basic(self):
        row = {
            "融资买入额": 641.89,
            "融资余额": 8807.38,
            "融券卖出量": 0.27,
            "融券余量": 6.68,
            "融券余额": 36.22,
            "融资融券余额": 8843.61,
        }
        item = adapt_margin_szse_summary_row(row)
        assert item.financing_balance == pytest.approx(8807.38)
        assert item.total_balance == pytest.approx(8843.61)
        assert item.exchange == "SZSE"


# ── SSE Detail ────────────────────────────────────────────────────

class TestAdaptMarginSSEDetailRow:
    def test_basic(self):
        row = {
            "信用交易日期": "20250508",
            "标的证券代码": "510050",
            "标的证券简称": "50ETF",
            "融资余额": 3070721166,
            "融资买入额": 219558160,
            "融资偿还额": 213157229,
            "融券余量": 14647020,
            "融券卖出量": 4703500,
            "融券偿还量": 3519500,
        }
        item = adapt_margin_sse_detail_row(row)
        assert item.symbol == "510050.SH"
        assert item.name == "50ETF"
        assert item.financing_balance == pytest.approx(3070721166)
        assert item.financing_repay == pytest.approx(213157229)
        assert item.securities_repay == pytest.approx(3519500)
        assert item.exchange == "SSE"


# ── SZSE Detail ───────────────────────────────────────────────────

class TestAdaptMarginSZSEDetailRow:
    def test_basic(self):
        row = {
            "证券代码": "000001",
            "证券简称": "平安银行",
            "融资买入额": 139740114,
            "融资余额": 4664112415,
            "融券卖出量": 77300,
            "融券余量": 387800,
            "融券余额": 4296824,
            "融资融券余额": 4668409239,
        }
        item = adapt_margin_szse_detail_row(row)
        assert item.symbol == "000001.SZ"
        assert item.name == "平安银行"
        assert item.financing_balance == pytest.approx(4664112415)
        assert item.securities_amount == pytest.approx(4296824)
        assert item.total_balance == pytest.approx(4668409239)
        assert item.exchange == "SZSE"


# ── Summary ───────────────────────────────────────────────────────

class TestBuildMarginSummaryText:
    def test_summary_with_balance(self):
        summary = [
            MarginSummaryItem(
                trade_date="2025-05-08",
                financing_balance=911157862069,
                total_balance=919144069698,
                exchange="SSE",
            ),
        ]
        text = build_margin_summary_text(summary, [])
        assert "融资余额9112亿" in text
        assert "两融余额9191亿" in text

    def test_detail_with_top_buy(self):
        detail = [
            MarginDetailItem(symbol="600519.SH", name="贵州茅台", financing_buy=5e8),
            MarginDetailItem(symbol="000001.SZ", name="平安银行", financing_buy=1.4e8),
        ]
        text = build_margin_summary_text([], detail)
        assert "融资买入最多贵州茅台" in text

    def test_szse_small_values(self):
        summary = [
            MarginSummaryItem(financing_balance=8807.38, total_balance=8843.61, exchange="SZSE"),
        ]
        text = build_margin_summary_text(summary, [])
        assert "融资余额8807亿" in text

    def test_empty(self):
        text = build_margin_summary_text([], [])
        assert "暂无" in text


# ── UseCase: partial_failure and errors ───────────────────────────

class TestMarginTradingUseCasePartialFailure:
    def test_partial_failure_when_sse_summary_fails(self):
        from unittest.mock import MagicMock
        from cn_stock_mcp.app.usecases.margin_trading import MarginTradingUseCase

        uc = MarginTradingUseCase()
        provider = MagicMock()
        provider.get_margin_sse_summary.side_effect = Exception("SSE down")
        provider.get_margin_szse_summary.return_value = []
        uc.router.get_provider = lambda name: provider

        req = type("Req", (), {
            "include": ["summary"],
            "trade_date": "2026-05-09",
            "start_date": None,
            "end_date": None,
            "exchange": "both",
            "sort_by": "financing_buy",
            "descending": True,
            "top_n": None,
        })()

        result = uc.execute(req)
        assert result["partial_failure"] is True
        assert len(result["errors"]) == 1
        assert result["errors"][0]["exchange"] == "SSE"
        assert result["errors"][0]["section"] == "summary"

    def test_no_errors_when_all_succeed(self):
        from unittest.mock import MagicMock
        from cn_stock_mcp.app.usecases.margin_trading import MarginTradingUseCase

        uc = MarginTradingUseCase()
        provider = MagicMock()
        provider.get_margin_sse_summary.return_value = []
        provider.get_margin_szse_summary.return_value = []
        uc.router.get_provider = lambda name: provider

        req = type("Req", (), {
            "include": ["summary"],
            "trade_date": "2026-05-09",
            "start_date": None,
            "end_date": None,
            "exchange": "both",
            "sort_by": "financing_buy",
            "descending": True,
            "top_n": None,
        })()

        result = uc.execute(req)
        assert result["partial_failure"] is False
        assert result["errors"] == []

    def test_partial_failure_when_detail_exchange_fails(self):
        from unittest.mock import MagicMock
        from cn_stock_mcp.app.usecases.margin_trading import MarginTradingUseCase

        uc = MarginTradingUseCase()
        provider = MagicMock()
        provider.get_margin_sse_summary.return_value = []
        provider.get_margin_szse_summary.return_value = []
        provider.get_margin_sse_detail.side_effect = Exception("SSE detail down")
        provider.get_margin_szse_detail.return_value = []
        uc.router.get_provider = lambda name: provider

        req = type("Req", (), {
            "include": ["summary", "detail"],
            "trade_date": "2026-05-09",
            "start_date": None,
            "end_date": None,
            "exchange": "both",
            "sort_by": "financing_buy",
            "descending": True,
            "top_n": 10,
        })()

        result = uc.execute(req)
        assert result["partial_failure"] is True
        assert any(e["section"] == "detail" for e in result["errors"])

import pytest

from cn_stock_mcp.app.models.valuation_rank import (
    MarketValuationSnapshot,
    StockValuationItem,
    ValuationRankSummary,
)
from cn_stock_mcp.providers.adapters.akshare_valuation_rank_adapters import (
    build_market_valuation_snapshot,
    rank_stock_valuation_items,
    build_valuation_summary,
    build_valuation_summary_text,
)


def test_build_market_valuation_snapshot_basic():
    pe_row = {
        "date": "2026-05-08",
        "middlePETTM": 45.07,
        "averagePETTM": 66.33,
        "middlePELYR": 45.99,
        "averagePELYR": 69.37,
        "quantileInAllHistoryMiddlePeTtm": 0.73609,
        "quantileInRecent10YearsMiddlePeTtm": 0.85431,
    }
    pb_row = {
        "date": "2026-05-08",
        "middlePB": 3.21,
        "equalWeightAveragePB": 4.73,
        "quantileInAllHistoryMiddlePB": 0.65269,
        "quantileInRecent10YearsMiddlePB": 0.82107,
    }
    dy_row = {"日期": "2026-05-08", "股息率": 2.57}
    hl_row = {"date": "2026-05-08", "high20": 1488, "low20": 215, "high60": 588, "low60": 111, "close": 4179.95}

    snap = build_market_valuation_snapshot(pe_row, pb_row, dy_row, hl_row)
    assert isinstance(snap, MarketValuationSnapshot)
    assert snap.date == "2026-05-08"
    assert snap.pe_ttm_median == pytest.approx(45.07)
    assert snap.pb_median == pytest.approx(3.21)
    assert snap.dividend_yield == pytest.approx(2.57)
    assert snap.high20_count == 1488


def test_rank_stock_valuation_items_and_labels():
    items = [
        StockValuationItem(symbol="000001.SZ", pe=8.0, pb=0.9),
        StockValuationItem(symbol="600519.SH", pe=30.0, pb=9.0),
        StockValuationItem(symbol="000333.SZ", pe=15.0, pb=3.0),
        StockValuationItem(symbol="601318.SH", pe=6.0, pb=0.8),
    ]

    ranked = rank_stock_valuation_items(items, sort_by="pe", descending=False)
    assert ranked[0].symbol == "601318.SH"
    assert ranked[-1].symbol == "600519.SH"

    labels = {it.symbol: it.valuation_label for it in ranked}
    assert labels["601318.SH"] in {"low", "neutral"}
    assert labels["600519.SH"] in {"high", "neutral"}

    # pb<1 should tag below_book_pb
    target = next(it for it in ranked if it.symbol == "601318.SH")
    assert "below_book_pb" in target.reason_tags


def test_rank_stock_valuation_items_market_cap_sort_desc():
    items = [
        StockValuationItem(symbol="A", market_cap=100),
        StockValuationItem(symbol="B", market_cap=300),
        StockValuationItem(symbol="C", market_cap=200),
    ]
    ranked = rank_stock_valuation_items(items, sort_by="market_cap", descending=True)
    assert [x.symbol for x in ranked] == ["B", "C", "A"]


def test_build_valuation_summary_and_text():
    snapshot = MarketValuationSnapshot(
        pe_ttm_median=45.07,
        pb_median=3.21,
        pe_ttm_quantile_10y=0.85,
        pb_quantile_10y=0.82,
        dividend_yield=2.57,
    )
    items = [
        StockValuationItem(symbol="A", valuation_label="low", pe=8, pb=1),
        StockValuationItem(symbol="B", valuation_label="neutral", pe=15, pb=2),
        StockValuationItem(symbol="C", valuation_label="high", pe=40, pb=8),
    ]

    summary = build_valuation_summary(items, snapshot)
    assert isinstance(summary, ValuationRankSummary)
    assert summary.stock_count == 3
    assert summary.low_valuation_count == 1
    assert summary.neutral_valuation_count == 1
    assert summary.high_valuation_count == 1
    assert summary.market_temperature in {"hot", "overheated"}

    text = build_valuation_summary_text(summary, snapshot)
    assert "市场估值温度" in text
    assert "全A中位PE" in text
    assert "低估/中性/高估=1/1/1" in text


def test_valuation_rank_request_schema():
    from cn_stock_mcp.server.schemas import ValuationRankRequest

    req = ValuationRankRequest(symbols=["000001.SZ", "000001.SZ", "600519.SH"], top_n=2)
    assert req.symbols == ["000001.SZ", "600519.SH"]
    assert req.top_n == 2

    with pytest.raises(ValueError):
        ValuationRankRequest(symbols=["", "  "])

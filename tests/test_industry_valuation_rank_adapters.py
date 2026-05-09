import pytest

from openclaw_stock_mcp.app.models.industry_valuation_rank import IndustryValuationItem
from openclaw_stock_mcp.providers.adapters.industry_valuation_rank_adapters import (
    build_sector_item,
    rank_items,
    build_summary,
    build_summary_text,
)


class _Q:
    def __init__(self, pe=None, pb=None):
        self.pe = pe
        self.pb = pb


def test_build_sector_item_basic():
    symbols = ["000001.SZ", "600519.SH", "000333.SZ"]
    quotes = [_Q(pe=8, pb=0.9), _Q(pe=35, pb=8), _Q(pe=14, pb=3)]
    item = build_sector_item("1000金融", symbols, quotes)

    assert item.sector_name == "1000金融"
    assert item.member_count == 3
    assert item.quote_coverage_count == 3
    assert item.pe_median == pytest.approx(14)
    assert item.pb_median == pytest.approx(3)
    assert item.pb_below_one_ratio == pytest.approx(1 / 3)


def test_rank_items_and_labels():
    items = [
        IndustryValuationItem(sector_name="A", pe_median=8, pb_median=1),
        IndustryValuationItem(sector_name="B", pe_median=15, pb_median=2),
        IndustryValuationItem(sector_name="C", pe_median=30, pb_median=5),
    ]
    ranked = rank_items(items, sort_by="pe_median", descending=False)
    assert [x.sector_name for x in ranked] == ["A", "B", "C"]
    assert ranked[0].pe_rank == 1
    assert ranked[-1].pe_rank == 3
    assert ranked[0].valuation_label in {"low", "neutral"}


def test_build_summary_and_text():
    items = [
        IndustryValuationItem(sector_name="A", valuation_label="low"),
        IndustryValuationItem(sector_name="B", valuation_label="neutral"),
        IndustryValuationItem(sector_name="C", valuation_label="high"),
    ]
    s = build_summary(items)
    assert s.sector_count == 3
    assert s.low_valuation_count == 1
    assert s.neutral_valuation_count == 1
    assert s.high_valuation_count == 1
    t = build_summary_text(s)
    assert "低估/中性/高估=1/1/1" in t


def test_request_schema():
    from openclaw_stock_mcp.server.schemas import IndustryValuationRankRequest

    req = IndustryValuationRankRequest(sector_names=["1000金融", "1000金融", "1000医药"], top_n=2)
    assert req.sector_names == ["1000金融", "1000医药"]
    assert req.top_n == 2

    with pytest.raises(ValueError):
        IndustryValuationRankRequest(sector_names=["", "   "])

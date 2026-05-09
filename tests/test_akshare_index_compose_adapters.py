import pytest

from openclaw_stock_mcp.app.models.index_compose import IndexConstituentItem
from openclaw_stock_mcp.providers.adapters.akshare_index_compose_adapters import (
    adapt_index_compose_rows,
    build_index_compose_summary,
    build_index_compose_summary_text,
)


def test_adapt_index_compose_rows_with_weight():
    rows = [
        {
            "日期": "2026-04-30",
            "指数代码": "000300",
            "指数名称": "沪深300",
            "成分券代码": "000001",
            "成分券名称": "平安银行",
            "交易所": "深圳证券交易所",
            "权重": 0.425,
        },
        {
            "日期": "2026-04-30",
            "指数代码": "000300",
            "指数名称": "沪深300",
            "成分券代码": "600519",
            "成分券名称": "贵州茅台",
            "交易所": "上海证券交易所",
            "权重": 4.2,
        },
    ]
    items = adapt_index_compose_rows(rows, include_weight=True)
    assert len(items) == 2
    assert isinstance(items[0], IndexConstituentItem)
    assert items[0].symbol == "000001.SZ"
    assert items[1].symbol == "600519.SH"
    assert items[0].weight == pytest.approx(0.425)


def test_adapt_index_compose_rows_without_weight():
    rows = [{"成分券代码": "000001", "成分券名称": "平安银行"}]
    items = adapt_index_compose_rows(rows, include_weight=False)
    assert items[0].weight is None


def test_build_index_compose_summary():
    items = [
        IndexConstituentItem(symbol="A", name="A", weight=10, date="2026-05-01", index_code="000300", index_name="沪深300"),
        IndexConstituentItem(symbol="B", name="B", weight=20, date="2026-05-01", index_code="000300", index_name="沪深300"),
        IndexConstituentItem(symbol="C", name="C", weight=5, date="2026-05-01", index_code="000300", index_name="沪深300"),
    ]
    s = build_index_compose_summary("000300", items)
    assert s.constituent_count == 3
    assert s.total_weight == pytest.approx(35)
    assert s.top5_weight == pytest.approx(35)
    assert s.max_weight == pytest.approx(20)
    assert s.min_weight == pytest.approx(5)


def test_build_index_compose_summary_text():
    items = [
        IndexConstituentItem(symbol="A", name="A", weight=10, date="2026-05-01", index_code="000300", index_name="沪深300"),
        IndexConstituentItem(symbol="B", name="B", weight=20, date="2026-05-01", index_code="000300", index_name="沪深300"),
    ]
    s = build_index_compose_summary("000300", items)
    text = build_index_compose_summary_text(s)
    assert "000300" in text
    assert "沪深300" in text
    assert "成分股2只" in text


def test_index_compose_request_schema():
    from openclaw_stock_mcp.server.schemas import IndexComposeRequest

    req = IndexComposeRequest(index_code="000300.SH", top_n=20)
    assert req.index_code == "000300.SH"
    assert req.top_n == 20

    with pytest.raises(ValueError):
        IndexComposeRequest(index_code="  ")

import pytest
from openclaw_stock_mcp.providers.adapters.akshare_financial_adapters import (
    build_financial_snapshot_from_abstract,
    build_financial_history_from_abstract,
    adapt_akshare_financial_detail_row,
    build_financial_summary_text,
)
from openclaw_stock_mcp.app.models.financial import (
    FinancialSnapshot,
    FinancialHistoryPoint,
    FinancialDetailItem,
)


# ---- Sample data mimicking stock_financial_abstract_new_ths ----

def _make_abstract_rows(report_date: str = "2026-03-31", quarter_name: str = "2026一季度") -> list[dict]:
    """Generate sample abstract rows for testing."""
    base_metrics = {
        "operating_income_total": 352.77e8,
        "parent_holder_net_profit": 145.23e8,
        "index_deduct_holder_net_profit": 144.88e8,
        "basic_eps": 0.67,
        "calc_per_net_assets": 22.15,
        "per_capital_reserve": 1.46,
        "per_undistributed_profits": 13.52,
        "index_per_operating_cash_flow_net": 1.95,
        "index_weighted_avg_roe": 0.0305,
        "index_full_diluted_roe": 0.0298,
        "sale_gross_margin": 0.4532,
        "sale_net_interest_ratio": 0.1201,
        "assets_debt_ratio": 0.9175,
        "equity_ratio": 0.28,
        "current_ratio": 1.02,
        "quick_ratio": 1.02,
        "conservative_quick_ratio": 1.02,
        "inventory_turnover_days": 0,
        "inventory_turnover_ratio": 0,
        "receive_accounts_turnover_days": 0,
        "business_cycle": 0,
    }
    yoy_metrics = {
        "calculate_parent_holder_net_profit_yoy_growth_ratio": -0.0618,
        "deduct_net_profit_yoy_growth_ratio": 3.1688,
        "calculate_operating_income_total_yoy_growth_ratio": -0.0352,
    }
    rows = []
    for metric_name, value in base_metrics.items():
        rows.append({
            "report_date": report_date,
            "report_name": "2026一季报",
            "report_period": "2026-1",
            "quarter_name": quarter_name,
            "metric_name": metric_name,
            "value": value,
            "single": value,
            "yoy": None,
            "mom": None,
            "single_yoy": None,
        })
    for metric_name, value in yoy_metrics.items():
        rows.append({
            "report_date": report_date,
            "report_name": "2026一季报",
            "report_period": "2026-1",
            "quarter_name": quarter_name,
            "metric_name": metric_name,
            "value": value,
            "single": value,
            "yoy": None,
            "mom": None,
            "single_yoy": None,
        })
    return rows


def _make_multi_period_rows() -> list[dict]:
    """Generate sample abstract rows across two periods."""
    rows = _make_abstract_rows("2026-03-31", "2026一季度")
    rows2 = _make_abstract_rows("2025-12-31", "2025年报")
    # Override some values for the second period
    for row in rows2:
        if row["metric_name"] == "operating_income_total":
            row["value"] = 1314.42e8
        elif row["metric_name"] == "parent_holder_net_profit":
            row["value"] = 426.33e8
        elif row["metric_name"] == "index_weighted_avg_roe":
            row["value"] = 0.0938
    return rows + rows2


# ---- build_financial_snapshot_from_abstract ----

def test_snapshot_basic():
    rows = _make_abstract_rows()
    snap = build_financial_snapshot_from_abstract("000001.SZ", rows)

    assert isinstance(snap, FinancialSnapshot)
    assert snap.symbol == "000001.SZ"
    assert snap.report_date == "2026-03-31"
    assert snap.quarter_name == "2026一季度"
    assert snap.operating_revenue == pytest.approx(352.77e8)
    assert snap.net_profit == pytest.approx(145.23e8)
    assert snap.deduct_net_profit == pytest.approx(144.88e8)
    assert snap.basic_eps == pytest.approx(0.67)
    assert snap.per_net_assets == pytest.approx(22.15)
    assert snap.roe_weighted == pytest.approx(0.0305)
    assert snap.sale_net_margin == pytest.approx(0.1201)
    assert snap.assets_debt_ratio == pytest.approx(0.9175)
    assert snap.net_profit_yoy == pytest.approx(-0.0618)
    assert snap.deduct_net_profit_yoy == pytest.approx(3.1688)
    assert snap.revenue_yoy == pytest.approx(-0.0352)


def test_snapshot_specific_report_date():
    rows = _make_multi_period_rows()
    snap = build_financial_snapshot_from_abstract("000001.SZ", rows, report_date="2025-12-31")

    assert snap.report_date == "2025-12-31"
    assert snap.operating_revenue == pytest.approx(1314.42e8)
    assert snap.net_profit == pytest.approx(426.33e8)


def test_snapshot_uses_latest_when_no_report_date():
    rows = _make_multi_period_rows()
    snap = build_financial_snapshot_from_abstract("000001.SZ", rows)

    # Should use the latest date
    assert snap.report_date == "2026-03-31"


def test_snapshot_empty_rows():
    snap = build_financial_snapshot_from_abstract("000001.SZ", [])
    assert snap.symbol == "000001.SZ"
    assert snap.report_date is None
    assert snap.operating_revenue is None


# ---- build_financial_history_from_abstract ----

def test_history_basic():
    rows = _make_multi_period_rows()
    history = build_financial_history_from_abstract(rows, recent_n=8)

    assert len(history) == 2
    assert all(isinstance(h, FinancialHistoryPoint) for h in history)
    # Sorted descending by date
    assert history[0].report_date == "2026-03-31"
    assert history[1].report_date == "2025-12-31"
    assert history[0].operating_revenue == pytest.approx(352.77e8)
    assert history[1].operating_revenue == pytest.approx(1314.42e8)


def test_history_limits_to_recent_n():
    rows = _make_multi_period_rows()
    history = build_financial_history_from_abstract(rows, recent_n=1)
    assert len(history) == 1
    assert history[0].report_date == "2026-03-31"


def test_history_empty():
    history = build_financial_history_from_abstract([], recent_n=8)
    assert history == []


# ---- adapt_akshare_financial_detail_row ----

def test_adapt_detail_row():
    row = {
        "report_date": "2026-03-31",
        "report_name": "2026一季报",
        "report_period": "2026-1",
        "quarter_name": "2026一季度",
        "metric_name": "total_current_assets",
        "value": 5.2e12,
        "single": 5.2e12,
        "yoy": 0.05,
        "mom": -0.02,
        "single_yoy": 0.04,
    }
    item = adapt_akshare_financial_detail_row(row)

    assert isinstance(item, FinancialDetailItem)
    assert item.report_date == "2026-03-31"
    assert item.report_name == "2026一季报"
    assert item.quarter_name == "2026一季度"
    assert item.metric_name == "total_current_assets"
    assert item.value == pytest.approx(5.2e12)
    assert item.yoy == pytest.approx(0.05)
    assert item.mom == pytest.approx(-0.02)


def test_adapt_detail_row_missing_fields():
    row = {"report_date": "2026-03-31", "report_name": "", "quarter_name": "", "metric_name": "test", "value": None}
    item = adapt_akshare_financial_detail_row(row)
    assert item.value is None
    assert item.yoy is None


def test_adapt_detail_row_false_value():
    row = {"report_date": "2026-03-31", "metric_name": "test", "value": False}
    item = adapt_akshare_financial_detail_row(row)
    assert item.value is None


# ---- build_financial_summary_text ----

def test_summary_text_full():
    snap = FinancialSnapshot(
        symbol="000001.SZ",
        report_date="2026-03-31",
        quarter_name="2026一季度",
        operating_revenue=352.77e8,
        revenue_yoy=-0.0352,
        net_profit=145.23e8,
        net_profit_yoy=-0.0618,
        roe_weighted=0.0305,
        sale_net_margin=0.1201,
        assets_debt_ratio=0.9175,
        basic_eps=0.67,
    )
    text = build_financial_summary_text(snap, "000001.SZ")
    assert "000001.SZ" in text
    assert "2026一季度" in text
    assert "营收" in text
    assert "净利" in text
    assert "ROE" in text
    assert "EPS" in text


def test_summary_text_empty():
    text = build_financial_summary_text(None, "000001.SZ")
    assert "000001.SZ" in text
    assert "暂无" in text


def test_summary_text_no_report_date():
    snap = FinancialSnapshot(symbol="000001.SZ")
    text = build_financial_summary_text(snap, "000001.SZ")
    assert "暂无" in text


# ---- Schema validation ----

def test_stock_financial_request_defaults():
    from openclaw_stock_mcp.server.schemas import StockFinancialRequest

    req = StockFinancialRequest(symbol="000001.SZ")
    assert req.symbol == "000001.SZ"
    assert req.include == ["snapshot", "history"]
    assert req.statement == "income"
    assert req.history_n == 8


def test_stock_financial_request_details_only():
    from openclaw_stock_mcp.server.schemas import StockFinancialRequest

    req = StockFinancialRequest(symbol="000001.SZ", include=["details"], statement="balance")
    assert req.include == ["details"]
    assert req.statement == "balance"


def test_stock_financial_request_empty_include_fails():
    from openclaw_stock_mcp.server.schemas import StockFinancialRequest

    with pytest.raises(ValueError, match="at least one"):
        StockFinancialRequest(symbol="000001.SZ", include=[])


def test_stock_financial_request_invalid_report_date():
    from openclaw_stock_mcp.server.schemas import StockFinancialRequest

    with pytest.raises(ValueError):
        StockFinancialRequest(symbol="000001.SZ", report_date="not-a-date")


def test_stock_financial_request_dedup_include():
    from openclaw_stock_mcp.server.schemas import StockFinancialRequest

    req = StockFinancialRequest(symbol="000001.SZ", include=["snapshot", "snapshot", "history"])
    assert req.include == ["snapshot", "history"]

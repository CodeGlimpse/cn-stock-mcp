import pytest

from cn_stock_mcp.app.models.financial import FinancialSnapshot
from cn_stock_mcp.providers.adapters.earnings_quality_adapters import (
    build_metrics,
    score_earnings_quality,
)


def test_build_metrics_basic():
    snap = FinancialSnapshot(
        symbol="000001.SZ",
        report_date="2026-03-31",
        quarter_name="2026一季度",
        net_profit=100,
        deduct_net_profit=90,
        net_profit_yoy=0.10,
        deduct_net_profit_yoy=0.08,
        basic_eps=1.0,
        per_operating_cash_flow=1.2,
        roe_weighted=0.12,
        assets_debt_ratio=0.55,
    )
    m = build_metrics(snap, "000001.SZ")
    assert m.deduct_profit_ratio == pytest.approx(0.9)
    assert m.profit_growth_gap == pytest.approx(0.02)
    assert m.cash_eps_ratio == pytest.approx(1.2)


def test_score_earnings_quality_excellent():
    snap = FinancialSnapshot(
        symbol="A",
        net_profit=100,
        deduct_net_profit=98,
        net_profit_yoy=0.20,
        deduct_net_profit_yoy=0.19,
        basic_eps=1.0,
        per_operating_cash_flow=1.4,
        roe_weighted=0.18,
        assets_debt_ratio=0.40,
    )
    m = build_metrics(snap, "A")
    score, label, tags, _ = score_earnings_quality(m)
    assert score is not None and score >= 80
    assert label in {"excellent", "good"}
    assert "strong_cash_conversion" in tags


def test_score_earnings_quality_poor():
    snap = FinancialSnapshot(
        symbol="B",
        net_profit=100,
        deduct_net_profit=40,
        net_profit_yoy=0.30,
        deduct_net_profit_yoy=-0.10,
        basic_eps=1.0,
        per_operating_cash_flow=0.2,
        roe_weighted=-0.05,
        assets_debt_ratio=0.90,
    )
    m = build_metrics(snap, "B")
    score, label, tags, _ = score_earnings_quality(m)
    assert score is not None and score <= 45
    assert label in {"weak", "poor", "fair"}
    assert "low_deduct_ratio" in tags
    assert "weak_cash_conversion" in tags


def test_score_missing_profit_data():
    snap = FinancialSnapshot(symbol="C")
    m = build_metrics(snap, "C")
    score, label, tags, diag = score_earnings_quality(m)
    assert score is None
    assert label == "unknown"
    assert "missing_profit_data" in tags
    assert "reason" in diag


def test_earnings_quality_request_schema():
    from cn_stock_mcp.server.schemas import EarningsQualityRequest

    req = EarningsQualityRequest(symbol="000001.SZ")
    assert req.symbol == "000001.SZ"

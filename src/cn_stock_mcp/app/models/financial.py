from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FinancialMetric(BaseModel):
    """A single financial metric with period and YoY/MoM context."""

    report_date: str
    quarter_name: str
    value: float | None = None
    single: float | None = None
    yoy: float | None = None
    mom: float | None = None
    single_yoy: float | None = None


class FinancialSnapshot(BaseModel):
    """Core financial snapshot for a stock, derived from abstract metrics."""

    symbol: str
    report_date: str | None = None
    quarter_name: str | None = None

    # Profitability
    operating_revenue: float | None = None
    net_profit: float | None = None
    deduct_net_profit: float | None = None
    net_profit_yoy: float | None = None
    deduct_net_profit_yoy: float | None = None
    revenue_yoy: float | None = None

    # Per-share
    basic_eps: float | None = None
    per_net_assets: float | None = None
    per_capital_reserve: float | None = None
    per_undistributed_profits: float | None = None
    per_operating_cash_flow: float | None = None

    # Ratios
    roe_weighted: float | None = None
    roe_diluted: float | None = None
    sale_gross_margin: float | None = None
    sale_net_margin: float | None = None
    assets_debt_ratio: float | None = None
    equity_ratio: float | None = None
    current_ratio: float | None = None
    quick_ratio: float | None = None
    conservative_quick_ratio: float | None = None

    # Turnover
    inventory_turnover_days: float | None = None
    inventory_turnover_ratio: float | None = None
    receive_accounts_turnover_days: float | None = None
    business_cycle: float | None = None

    source: str = "akshare"


class FinancialDetailItem(BaseModel):
    """A single row from detailed financial statement (long format)."""

    report_date: str
    report_name: str
    quarter_name: str
    metric_name: str
    value: float | None = None
    single: float | None = None
    yoy: float | None = None
    mom: float | None = None
    single_yoy: float | None = None


class FinancialHistoryPoint(BaseModel):
    """One quarter's snapshot of key metrics for trend analysis."""

    report_date: str
    quarter_name: str
    operating_revenue: float | None = None
    net_profit: float | None = None
    net_profit_yoy: float | None = None
    revenue_yoy: float | None = None
    basic_eps: float | None = None
    roe_weighted: float | None = None
    sale_net_margin: float | None = None
    assets_debt_ratio: float | None = None


class StockFinancialResult(BaseModel):
    """Full result for stock_financial tool."""

    symbol: str
    snapshot: FinancialSnapshot | None = None
    history: list[FinancialHistoryPoint] = Field(default_factory=list)
    details: list[FinancialDetailItem] = Field(default_factory=list)
    detail_statement: str | None = None  # "income" / "balance" / "cashflow"
    source: str = "akshare"

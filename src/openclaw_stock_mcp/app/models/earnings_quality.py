from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EarningsQualityMetrics(BaseModel):
    symbol: str
    report_date: str | None = None
    quarter_name: str | None = None

    net_profit: float | None = None
    deduct_net_profit: float | None = None
    net_profit_yoy: float | None = None
    deduct_net_profit_yoy: float | None = None

    operating_revenue: float | None = None
    revenue_yoy: float | None = None

    basic_eps: float | None = None
    per_operating_cash_flow: float | None = None
    cash_eps_ratio: float | None = None

    roe_weighted: float | None = None
    sale_net_margin: float | None = None
    assets_debt_ratio: float | None = None

    deduct_profit_ratio: float | None = None
    profit_growth_gap: float | None = None


class EarningsQualityResult(BaseModel):
    symbol: str
    report_date: str | None = None
    quarter_name: str | None = None
    score: float | None = None
    label: str | None = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    reason_tags: list[str] = Field(default_factory=list)
    metrics: EarningsQualityMetrics | None = None
    summary: str | None = None
    source: str = "akshare"

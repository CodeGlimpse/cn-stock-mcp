from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CapitalFlowRecord(BaseModel):
    """Single-date capital flow data point."""

    date: str
    close: float | None = None
    change_percent: float | None = None
    main_net_inflow: float | None = None
    main_net_inflow_pct: float | None = None
    super_large_net_inflow: float | None = None
    super_large_net_inflow_pct: float | None = None
    large_net_inflow: float | None = None
    large_net_inflow_pct: float | None = None
    medium_net_inflow: float | None = None
    medium_net_inflow_pct: float | None = None
    small_net_inflow: float | None = None
    small_net_inflow_pct: float | None = None


class SectorFundFlowItem(BaseModel):
    """Sector-level fund flow ranking item."""

    rank: int | None = None
    sector_name: str
    sector_index: float | None = None
    sector_change_percent: float | None = None
    inflow: float | None = None
    outflow: float | None = None
    net_amount: float | None = None
    company_count: int | None = None
    leading_stock: str | None = None
    leading_stock_change_percent: float | None = None
    leading_stock_price: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class MarketFundFlowSummary(BaseModel):
    """Aggregated summary for market-level fund flow."""

    total_main_net_inflow: float | None = None
    avg_main_net_inflow_pct: float | None = None
    total_super_large_net_inflow: float | None = None
    total_large_net_inflow: float | None = None
    total_medium_net_inflow: float | None = None
    total_small_net_inflow: float | None = None
    main_inflow_direction: str | None = None  # "inflow" / "outflow" / "neutral"

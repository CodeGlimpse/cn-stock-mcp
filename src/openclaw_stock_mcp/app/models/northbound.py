from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NorthboundFlowRecord(BaseModel):
    """A single date's northbound flow data point."""

    date: str
    net_buy_amount: float | None = None  # 当日成交净买额（亿元）
    buy_amount: float | None = None      # 买入成交额（亿元）
    sell_amount: float | None = None     # 卖出成交额（亿元）
    cumulative_net_buy: float | None = None  # 历史累计净买额（亿元）
    daily_inflow: float | None = None    # 当日资金流入（亿元）
    balance: float | None = None        # 当日余额（亿元）
    hold_market_cap: float | None = None  # 持股市值（亿元）
    leading_stock: str | None = None
    leading_stock_change: float | None = None
    leading_stock_code: str | None = None
    csi300: float | None = None
    csi300_change: float | None = None


class NorthboundDailySummary(BaseModel):
    """Current-day northbound flow summary (from fund_flow_summary_em)."""

    trade_date: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)
    sh_north_net_buy: float | None = None  # 沪股通净买额
    sz_north_net_buy: float | None = None  # 深股通净买额
    total_north_net_buy: float | None = None
    sh_north_inflow: float | None = None
    sz_north_inflow: float | None = None
    sh_north_up_count: int | None = None
    sh_north_down_count: int | None = None
    sz_north_up_count: int | None = None
    sz_north_down_count: int | None = None


class NorthboundHoldItem(BaseModel):
    """A stock held by northbound capital."""

    symbol: str
    name: str
    price: float | None = None
    change_percent: float | None = None
    hold_shares: float | None = None       # 持股数量（万股）
    hold_market_cap: float | None = None   # 持股市值（万元）
    hold_pct_float: float | None = None    # 占流通股比%
    hold_pct_total: float | None = None    # 占总股本比%
    increase_shares: float | None = None   # 增持股数（万股）
    increase_market_cap: float | None = None  # 增持市值（万元）
    increase_pct: float | None = None      # 增持市值增幅%
    sector: str | None = None
    date: str | None = None


class NorthboundResult(BaseModel):
    """Full result for northbound tool."""

    daily_summary: NorthboundDailySummary | None = None
    history: list[NorthboundFlowRecord] = Field(default_factory=list)
    holdings: list[NorthboundHoldItem] = Field(default_factory=list)
    source: str = "akshare"

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ETFSpotItem(BaseModel):
    """A single ETF's real-time snapshot from fund_etf_spot_em."""

    symbol: str
    name: str
    price: float | None = None                # 最新价
    iopv: float | None = None                  # IOPV实时估值
    discount_rate: float | None = None         # 基金折价率%
    change_amount: float | None = None         # 涨跌额
    change_percent: float | None = None        # 涨跌幅%
    volume: float | None = None                # 成交量
    turnover: float | None = None              # 成交额
    open: float | None = None
    high: float | None = None
    low: float | None = None
    prev_close: float | None = None
    amplitude: float | None = None             # 振幅%
    turnover_rate: float | None = None         # 换手率%
    volume_ratio: float | None = None          # 量比
    main_net_inflow: float | None = None       # 主力净流入-净额
    main_net_inflow_ratio: float | None = None # 主力净流入-净占比%
    super_large_net_inflow: float | None = None  # 超大单净流入-净额
    large_net_inflow: float | None = None        # 大单净流入-净额
    latest_shares: float | None = None         # 最新份额
    circulating_market_cap: float | None = None  # 流通市值
    total_market_cap: float | None = None      # 总市值
    trade_date: str | None = None


class ETFScaleItem(BaseModel):
    """ETF share/scale data from fund_etf_scale_sse."""

    symbol: str
    name: str
    etf_type: str | None = None               # 单市/跨市 等
    date: str | None = None
    shares: float | None = None               # 基金份额


class ETFNAVItem(BaseModel):
    """ETF net asset value from fund_etf_fund_info_em."""

    date: str
    nav: float | None = None                  # 单位净值
    acc_nav: float | None = None              # 累计净值
    daily_growth: float | None = None         # 日增长率%
    purchase_status: str | None = None
    redeem_status: str | None = None


class ETFSnapshotResult(BaseModel):
    """Full result for etf_snapshot tool."""

    spot: list[ETFSpotItem] = Field(default_factory=list)
    spot_count: int = 0
    scale: list[ETFScaleItem] = Field(default_factory=list)
    scale_count: int = 0
    nav: list[ETFNAVItem] = Field(default_factory=list)
    nav_count: int = 0
    summary: str = ""
    source: str = "akshare"

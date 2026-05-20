from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CBSpotItem(BaseModel):
    """A single convertible bond snapshot from bond_cb_jsl."""

    symbol: str
    name: str
    price: float | None = None                 # 现价
    change_percent: float | None = None        # 涨跌幅%
    stock_symbol: str | None = None            # 正股代码
    stock_name: str | None = None              # 正股名称
    stock_price: float | None = None           # 正股价
    stock_change: float | None = None          # 正股涨跌%
    stock_pb: float | None = None              # 正股PB
    conv_price: float | None = None            # 转股价
    conv_value: float | None = None            # 转股价值
    conv_premium: float | None = None          # 转股溢价率%
    rating: str | None = None                  # 债券评级
    put_trigger_price: float | None = None     # 回售触发价
    call_trigger_price: float | None = None    # 强赎触发价
    cb_ratio: float | None = None              # 转债占比%
    maturity_date: str | None = None           # 到期时间
    remaining_years: float | None = None       # 剩余年限
    remaining_size: float | None = None        # 剩余规模（亿元）
    turnover: float | None = None              # 成交额
    turnover_rate: float | None = None         # 换手率%
    ytm: float | None = None                   # 到期税前收益%
    double_low: float | None = None            # 双低值


class CBRedeemItem(BaseModel):
    """A convertible bond's call/put status from bond_cb_redeem_jsl."""

    symbol: str
    name: str
    price: float | None = None
    stock_symbol: str | None = None
    stock_name: str | None = None
    total_size: float | None = None            # 规模（亿元）
    remaining_size: float | None = None        # 剩余规模（亿元）
    conv_start_date: str | None = None         # 转股起始日
    last_trade_date: str | None = None         # 最后交易日
    maturity_date: str | None = None           # 到期日
    conv_price: float | None = None            # 转股价
    call_trigger_ratio: float | None = None    # 强赎触发比%
    call_trigger_price: float | None = None    # 强赎触发价
    stock_price: float | None = None           # 正股价
    call_price: float | None = None            # 强赎价
    call_day_count: str | None = None          # 强赎天计数
    call_clause: str | None = None             # 强赎条款
    call_status: str | None = None             # 强赎状态


class CBIndexPoint(BaseModel):
    """A data point in the convertible bond index."""

    date: str
    price: float | None = None
    amount: float | None = None
    volume: float | None = None
    count: int | None = None


class ConvertibleBondResult(BaseModel):
    """Full result for convertible_bond tool."""

    spot: list[CBSpotItem] = Field(default_factory=list)
    spot_count: int = 0
    redeem: list[CBRedeemItem] = Field(default_factory=list)
    redeem_count: int = 0
    index: list[CBIndexPoint] = Field(default_factory=list)
    index_count: int = 0
    summary: str = ""
    source: str = "akshare"

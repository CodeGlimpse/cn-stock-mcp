from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LimitUpItem(BaseModel):
    """A single limit-up stock with full metadata."""

    symbol: str
    name: str
    price: float | None = None
    change_percent: float | None = None
    turnover: float | None = None
    turnover_rate: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None
    limit_fund: float | None = None
    first_limit_time: str | None = None
    last_limit_time: str | None = None
    board_burst_count: int | None = None
    consecutive_boards: int | None = None
    limit_stat: str | None = None
    sector: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class BrokenLimitItem(BaseModel):
    """A stock that hit limit-up but broke (炸板)."""

    symbol: str
    name: str
    price: float | None = None
    change_percent: float | None = None
    limit_price: float | None = None
    turnover: float | None = None
    turnover_rate: float | None = None
    amplitude: float | None = None
    first_limit_time: str | None = None
    board_burst_count: int | None = None
    limit_stat: str | None = None
    sector: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class PreviousDayLimitItem(BaseModel):
    """A stock that was limit-up yesterday — tracking today's performance."""

    symbol: str
    name: str
    price: float | None = None
    change_percent: float | None = None
    limit_price: float | None = None
    turnover: float | None = None
    turnover_rate: float | None = None
    speed: float | None = None
    amplitude: float | None = None
    yesterday_limit_time: str | None = None
    yesterday_consecutive_boards: int | None = None
    limit_stat: str | None = None
    sector: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class LimitStatSummary(BaseModel):
    """Aggregated limit statistics for a trading day."""

    trade_date: str
    limit_up_count: int = 0
    broken_limit_count: int = 0
    limit_down_count: int = 0
    seal_rate: float | None = None  # 封板率 = limit_up / (limit_up + broken_limit)
    avg_consecutive_boards: float | None = None
    max_consecutive_boards: int = 0
    board_distribution: dict[int, int] = Field(default_factory=dict)  # {连板数: 个数}
    yesterday_limit_count: int = 0
    yesterday_continue_limit_count: int = 0  # 昨日涨停今日继续涨停
    yesterday_continue_rate: float | None = None  # 昨涨停今继续率
    limit_up_by_sector: dict[str, int] = Field(default_factory=dict)  # {行业: 涨停个数}
    broken_limit_by_sector: dict[str, int] = Field(default_factory=dict)

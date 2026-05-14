from __future__ import annotations

from pydantic import BaseModel


class LimitUpItem(BaseModel):
    code: str | None
    name: str | None
    change_pct: float | None
    latest_price: float | None
    turnover: float | None
    float_market_cap: float | None
    total_market_cap: float | None
    turnover_rate: float | None
    seal_amount: float | None
    first_seal_time: str | None
    last_seal_time: str | None
    broken_count: int | None
    limit_stat: str | None
    consecutive_limit: int | None
    industry: str | None
    source: str = "akshare"


class LimitDownItem(BaseModel):
    code: str | None
    name: str | None
    change_pct: float | None
    latest_price: float | None
    turnover: float | None
    float_market_cap: float | None
    total_market_cap: float | None
    pe_dynamic: float | None
    turnover_rate: float | None
    seal_amount: float | None
    last_seal_time: str | None
    board_turnover: float | None
    consecutive_limit: int | None
    open_count: int | None
    industry: str | None
    source: str = "akshare"


class StrongItem(BaseModel):
    code: str | None
    name: str | None
    change_pct: float | None
    latest_price: float | None
    limit_price: float | None
    turnover: float | None
    float_market_cap: float | None
    total_market_cap: float | None
    turnover_rate: float | None
    speed: float | None
    is_new_high: str | None
    volume_ratio: float | None
    limit_stat: str | None
    reason: str | None
    industry: str | None
    source: str = "akshare"


class PreviousItem(BaseModel):
    code: str | None
    name: str | None
    change_pct: float | None
    latest_price: float | None
    limit_price: float | None
    turnover: float | None
    float_market_cap: float | None
    total_market_cap: float | None
    turnover_rate: float | None
    speed: float | None
    amplitude: float | None
    yesterday_seal_time: str | None
    yesterday_consecutive: int | None
    limit_stat: str | None
    industry: str | None
    source: str = "akshare"


class SubNewItem(BaseModel):
    code: str | None
    name: str | None
    change_pct: float | None
    latest_price: float | None
    limit_price: float | None
    turnover: float | None
    float_market_cap: float | None
    total_market_cap: float | None
    turnover_rate: float | None
    open_days: int | None
    open_date: str | None
    list_date: str | None
    is_new_high: str | None
    limit_stat: str | None
    industry: str | None
    source: str = "akshare"


class BrokenItem(BaseModel):
    code: str | None
    name: str | None
    change_pct: float | None
    latest_price: float | None
    limit_price: float | None
    turnover: float | None
    float_market_cap: float | None
    total_market_cap: float | None
    turnover_rate: float | None
    speed: float | None
    first_seal_time: str | None
    broken_count: int | None
    limit_stat: str | None
    amplitude: float | None
    industry: str | None
    source: str = "akshare"


class LimitUpPoolResult(BaseModel):
    limit_up: list[LimitUpItem] = []
    limit_up_count: int = 0
    limit_down: list[LimitDownItem] = []
    limit_down_count: int = 0
    strong: list[StrongItem] = []
    strong_count: int = 0
    previous: list[PreviousItem] = []
    previous_count: int = 0
    sub_new: list[SubNewItem] = []
    sub_new_count: int = 0
    broken: list[BrokenItem] = []
    broken_count: int = 0
    summary: str = ""

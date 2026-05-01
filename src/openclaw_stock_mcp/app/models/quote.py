from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Quote(BaseModel):
    symbol: str
    name: str | None = None
    market: Literal["CN"] = "CN"
    exchange: Literal["SH", "SZ", "BJ", "BK"] | None = None
    board: str | None = None
    sec_type: Literal["stock", "index", "fund", "sector"]
    price: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    prev_close: float | None = None
    change: float | None = None
    change_percent: float | None = None
    amplitude: float | None = None
    volume: float | None = None
    turnover: float | None = None
    turnover_rate: float | None = None
    pe: float | None = None
    pb: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None
    currency: str = "CNY"
    trading_status: str | None = None
    timestamp: str | None = None
    source: str

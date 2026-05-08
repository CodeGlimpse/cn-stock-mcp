from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class SectorQuote(BaseModel):
    symbol: str
    name: str | None = None
    market: Literal["CN"] = "CN"
    sector_type: Literal["primary", "concept"] | None = None
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
    currency: str = "CNY"
    timestamp: str | None = None
    source: str

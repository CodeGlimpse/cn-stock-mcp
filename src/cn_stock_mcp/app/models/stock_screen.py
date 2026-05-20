from __future__ import annotations

from pydantic import BaseModel, Field


class StockScreenItem(BaseModel):
    symbol: str
    name: str
    latest_price: float | None
    change_pct: float | None
    change_amt: float | None
    open: float | None
    high: float | None
    low: float | None
    prev_close: float | None
    volume: float | None
    turnover: float | None
    amplitude: float | None = None
    source: str = "akshare"


class StockScreenResult(BaseModel):
    filter_desc: str = ""
    total_before_filter: int = 0
    total_after_filter: int = 0
    items: list[StockScreenItem] = []
    summary: str = ""

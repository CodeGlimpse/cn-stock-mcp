from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MarketPoolItem(BaseModel):
    symbol: str
    name: str
    price: float | None = None
    change_percent: float | None = None
    turnover: float | None = None
    turnover_rate: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

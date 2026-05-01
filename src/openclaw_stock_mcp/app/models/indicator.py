from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class IndicatorPoint(BaseModel):
    time: str
    values: dict[str, float | None] = Field(default_factory=dict)


class IndicatorSeries(BaseModel):
    symbol: str
    name: str | None = None
    market: Literal["CN"] = "CN"
    sec_type: Literal["stock", "index", "fund"]
    interval: str
    indicator: Literal["macd", "ma", "boll", "kdj"]
    items: list[IndicatorPoint] = Field(default_factory=list)
    source: str

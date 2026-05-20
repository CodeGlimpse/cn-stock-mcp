from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Instrument(BaseModel):
    symbol: str
    name: str | None = None
    market: Literal["CN"] = "CN"
    exchange: Literal["SH", "SZ", "BJ", "BK"] | None = None
    board: str | None = None
    sec_type: Literal["stock", "index", "fund", "sector"]
    raw_symbol: str | None = None
    source: str | None = None
    confidence: float | None = None

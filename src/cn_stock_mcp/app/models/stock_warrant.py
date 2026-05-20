from __future__ import annotations

from pydantic import BaseModel


class OptionItem(BaseModel):
    symbol: str | None
    name: str | None
    latest_price: float | None
    change_pct: float | None
    change_amt: float | None
    volume: float | None
    open_interest: float | None
    strike: float | None
    expiry: str | None
    option_type: str | None
    source: str = "akshare"


class StockWarrantResult(BaseModel):
    etf_option: list[OptionItem] = []
    etf_option_count: int = 0
    commodity_option: list[OptionItem] = []
    commodity_option_count: int = 0
    index_option: list[OptionItem] = []
    index_option_count: int = 0
    summary: str = ""

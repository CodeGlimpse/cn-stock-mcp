from __future__ import annotations

from pydantic import BaseModel


class DisclosureItem(BaseModel):
    """财报披露日历条目"""
    symbol: str
    name: str
    first_schedule: str | None
    change_1: str | None
    change_2: str | None
    change_3: str | None
    actual_date: str | None
    source: str = "akshare"


class DisclosureResult(BaseModel):
    items: list[DisclosureItem] = []
    total_count: int = 0
    period: str = ""
    market: str = ""
    summary: str = ""

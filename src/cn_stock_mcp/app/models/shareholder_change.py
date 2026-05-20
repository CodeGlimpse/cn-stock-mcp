from __future__ import annotations

from pydantic import BaseModel


class ShareholderTop10Item(BaseModel):
    """十大股东（占总股本）"""
    rank: int | None
    shareholder_name: str | None
    share_type: str | None
    hold_count: float | None
    hold_ratio: float | None
    change: str | None
    change_ratio: float | None
    source: str = "akshare"


class ShareholderChangeItem(BaseModel):
    """股东持股变动汇总"""
    shareholder_name: str | None
    shareholder_type: str | None
    total_hold: int | None
    new_hold: int | None
    increase_hold: int | None
    unchanged_hold: int | None
    decrease_hold: int | None
    float_cap: float | None
    held_stocks: str | None
    source: str = "akshare"


class ShareholderChangeResult(BaseModel):
    top10: list[ShareholderTop10Item] = []
    top10_count: int = 0
    change: list[ShareholderChangeItem] = []
    change_count: int = 0
    symbol: str = ""
    quarter: str = ""
    summary: str = ""

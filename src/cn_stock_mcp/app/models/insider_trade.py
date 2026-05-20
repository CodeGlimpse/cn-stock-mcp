from __future__ import annotations

from pydantic import BaseModel


class InsiderTop10Item(BaseModel):
    """十大流通股东持股"""
    rank: int | None
    shareholder_name: str | None
    shareholder_type: str | None
    share_type: str | None
    hold_count: float | None
    hold_ratio: float | None
    change: str | None
    change_ratio: float | None
    source: str = "akshare"


class InsiderChangeItem(BaseModel):
    """高管/股东增减持明细"""
    announce_date: str | None
    shareholder_name: str | None
    change_count: str | None
    avg_price: str | None
    remaining_shares: str | None
    change_period: str | None
    change_method: str | None
    source: str = "akshare"


class InsiderTradeResult(BaseModel):
    top10: list[InsiderTop10Item] = []
    top10_count: int = 0
    change: list[InsiderChangeItem] = []
    change_count: int = 0
    symbol: str = ""
    quarter: str = ""
    summary: str = ""

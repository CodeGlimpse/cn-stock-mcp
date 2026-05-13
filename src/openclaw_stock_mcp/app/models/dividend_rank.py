from __future__ import annotations

from pydantic import BaseModel


class DividendRankItem(BaseModel):
    """全市场历史分红排名"""
    symbol: str
    name: str
    list_date: str | None
    total_dividend: float | None
    avg_annual_dividend: float | None
    dividend_count: int | None
    total_financing: float | None
    financing_count: int | None
    source: str = "akshare"


class DividendPlanItem(BaseModel):
    """按报告期分红配送方案"""
    symbol: str
    name: str
    bonus_share_ratio: float | None
    conversion_ratio: float | None
    cash_dividend_ratio: float | None
    dividend_yield: float | None
    eps: float | None
    bvps: float | None
    reserve_per_share: float | None
    undistributed_per_share: float | None
    net_profit_yoy: float | None
    total_shares: float | None
    announce_date: str | None
    record_date: str | None
    ex_date: str | None
    progress: str | None
    source: str = "akshare"


class DividendDetailItem(BaseModel):
    """单股历史分红明细"""
    announce_date: str | None
    bonus_share: float | None
    conversion: float | None
    cash_dividend: float | None
    progress: str | None
    ex_date: str | None
    record_date: str | None
    source: str = "akshare"


class DividendRankResult(BaseModel):
    rank: list[DividendRankItem] = []
    rank_count: int = 0
    plan: list[DividendPlanItem] = []
    plan_count: int = 0
    detail: list[DividendDetailItem] = []
    detail_count: int = 0
    summary: str = ""

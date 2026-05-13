from __future__ import annotations

from pydantic import BaseModel


class ShiborItem(BaseModel):
    date: str
    overnight: float | None
    overnight_change: float | None
    week_1: float | None
    week_1_change: float | None
    week_2: float | None
    week_2_change: float | None
    month_1: float | None
    month_1_change: float | None
    month_3: float | None
    month_3_change: float | None
    month_6: float | None
    month_6_change: float | None
    month_9: float | None
    month_9_change: float | None
    year_1: float | None
    year_1_change: float | None
    source: str = "akshare"


class InterbankRateItem(BaseModel):
    date: str
    rate: float | None
    change: float | None
    source: str = "akshare"


class RepoRateItem(BaseModel):
    date: str
    FR001: float | None
    FR007: float | None
    FR014: float | None
    FDR001: float | None
    FDR007: float | None
    FDR014: float | None
    source: str = "akshare"


class MoneyRateResult(BaseModel):
    shibor: list[ShiborItem] = []
    shibor_count: int = 0
    interbank: list[InterbankRateItem] = []
    interbank_count: int = 0
    repo: list[RepoRateItem] = []
    repo_count: int = 0
    summary: str = ""

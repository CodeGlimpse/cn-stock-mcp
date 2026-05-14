from __future__ import annotations

from pydantic import BaseModel


class IndustryListItem(BaseModel):
    name: str
    code: str | None
    change_pct: float | None
    volume: float | None
    turnover: float | None
    net_inflow: float | None
    up_count: int | None
    down_count: int | None
    avg_price: float | None
    leader: str | None
    leader_price: float | None
    leader_change_pct: float | None
    source: str = "akshare"


class ConceptListItem(BaseModel):
    name: str
    code: str | None
    date: str | None
    driver_event: str | None
    leader: str | None
    member_count: int | None
    source: str = "akshare"


class IndustryChainResult(BaseModel):
    industry_list: list[IndustryListItem] = []
    industry_count: int = 0
    concept_list: list[ConceptListItem] = []
    concept_count: int = 0
    summary: str = ""

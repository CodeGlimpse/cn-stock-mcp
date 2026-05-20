from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IndexConstituentItem(BaseModel):
    symbol: str
    name: str
    exchange: str | None = None
    weight: float | None = None
    date: str | None = None
    index_code: str | None = None
    index_name: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class IndexComposeSummary(BaseModel):
    index_code: str
    index_name: str | None = None
    as_of_date: str | None = None
    constituent_count: int = 0
    total_weight: float | None = None
    top10_weight: float | None = None
    top5_weight: float | None = None
    max_weight: float | None = None
    min_weight: float | None = None


class IndexComposeResult(BaseModel):
    summary: IndexComposeSummary
    items: list[IndexConstituentItem] = Field(default_factory=list)
    source: str = "akshare"

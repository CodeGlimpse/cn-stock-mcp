from __future__ import annotations

from pydantic import BaseModel, Field


class IndexEnhanceMemberItem(BaseModel):
    symbol: str
    name: str | None = None
    weight: float | None = None
    price: float | None = None
    change_percent: float | None = None
    weighted_contribution: float | None = None
    excess_vs_index: float | None = None
    source: str | None = None


class IndexEnhanceSummary(BaseModel):
    index_code: str
    index_name: str | None = None
    benchmark_return: float | None = None
    enhanced_return: float | None = None
    excess_return: float | None = None
    member_count: int = 0
    total_weight: float | None = None
    outperform_count: int = 0
    underperform_count: int = 0
    method: str = "top_weight_weighted_quote"


class IndexEnhanceResult(BaseModel):
    summary: IndexEnhanceSummary
    members: list[IndexEnhanceMemberItem] = Field(default_factory=list)
    summary_text: str = ""
    source: str = "mixed"

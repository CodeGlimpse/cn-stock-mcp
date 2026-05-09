from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IndustryValuationItem(BaseModel):
    sector_name: str
    sector_type: str = "primary"
    member_count: int = 0
    quote_coverage_count: int = 0
    pe_median: float | None = None
    pb_median: float | None = None
    pe_mean: float | None = None
    pb_mean: float | None = None
    pe_positive_ratio: float | None = None
    pb_below_one_ratio: float | None = None
    pe_rank: int | None = None
    pb_rank: int | None = None
    valuation_percentile: float | None = None
    valuation_label: str | None = None
    reason_tags: list[str] = Field(default_factory=list)
    sample_symbols: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class IndustryValuationSummary(BaseModel):
    sector_count: int = 0
    priced_sector_count: int = 0
    low_valuation_count: int = 0
    neutral_valuation_count: int = 0
    high_valuation_count: int = 0


class IndustryValuationRankResult(BaseModel):
    sector_type: str = "primary"
    items: list[IndustryValuationItem] = Field(default_factory=list)
    summary: IndustryValuationSummary | None = None
    source: str = "mixed"

from __future__ import annotations

from pydantic import BaseModel, Field


class IndexEnhanceMemberItem(BaseModel):
    symbol: str
    name: str | None = None
    industry: str | None = None
    weight: float | None = None
    price: float | None = None
    change_percent: float | None = None
    weighted_contribution: float | None = None
    excess_vs_index: float | None = None
    source: str | None = None


class IndexEnhanceIndustryExposureItem(BaseModel):
    industry: str
    member_count: int = 0
    weight_sum: float | None = None
    avg_change_percent: float | None = None
    contribution_sum: float | None = None
    excess_contribution_sum: float | None = None


class IndexEnhanceWeightExposure(BaseModel):
    total_weight: float | None = None
    top1_weight_percent: float | None = None
    top3_weight_percent: float | None = None
    top5_weight_percent: float | None = None
    top10_weight_percent: float | None = None
    top_members: list[IndexEnhanceMemberItem] = Field(default_factory=list)


class IndexEnhanceIndustryCoverage(BaseModel):
    known_count: int = 0
    unknown_count: int = 0
    coverage_ratio: float | None = None


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
    weight_exposure: IndexEnhanceWeightExposure | None = None
    industry_exposure: list[IndexEnhanceIndustryExposureItem] = Field(default_factory=list)
    industry_coverage: IndexEnhanceIndustryCoverage | None = None
    summary_text: str = ""
    source: str = "mixed"

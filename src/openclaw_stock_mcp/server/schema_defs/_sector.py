from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ._helpers import (
    dedupe_include,
    dedupe_str_list,
    normalize_pool_type,
    validate_date_range,
)
from ._types import AdjustType, ProviderName, SectorLookupMode, SectorType


class SectorReviewRequest(BaseModel):
    sector_name: str = Field(min_length=1)
    sector_type: SectorType = "primary"
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: Literal["zhitu"] | None = "zhitu"
    sort_by: Literal["relative_strength", "return", "max_drawdown", "volume_ratio"] = "relative_strength"
    descending: bool = True
    top_n: int = Field(default=5, ge=1, le=20)
    limit: int = Field(default=100, ge=1, le=500)
    min_relative_strength: float | None = None
    min_return: float | None = None
    max_drawdown_limit: float | None = None
    min_volume_ratio: float | None = None

    @model_validator(mode="after")
    def validate_request(self):
        self.trade_date, self.start_date, self.end_date = validate_date_range(
            self.trade_date, self.start_date, self.end_date
        )
        return self


class SectorRotationReviewRequest(BaseModel):
    sector_names: list[str] = Field(min_length=2, max_length=15)
    sector_type: SectorType = "primary"
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: Literal["zhitu"] | None = "zhitu"
    sort_by: Literal["avg_relative_strength", "avg_return", "positive_ratio", "stronger_ratio", "sentiment_score", "rotation_score"] = "avg_relative_strength"
    descending: bool = True
    top_n: int = Field(default=5, ge=1, le=15)
    limit: int = Field(default=100, ge=1, le=500)
    member_top_n: int = Field(default=3, ge=1, le=10)
    skip_member_detail: bool = Field(default=False, description="When True, skip per-member stock_review expansion and return only sector-level aggregate (sector_lookup + quote-level breadth). Much faster for sector comparison only.")
    min_relative_strength: float | None = None
    min_return: float | None = None
    max_drawdown_limit: float | None = None
    min_volume_ratio: float | None = None

    @model_validator(mode="after")
    def validate_request(self):
        if self.trade_date and (self.start_date or self.end_date):
            raise ValueError("trade_date cannot be combined with start_date/end_date")
        if self.start_date or self.end_date:
            if not self.start_date or not self.end_date:
                raise ValueError("start_date and end_date must be provided together")
            from datetime import date as dt_date
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
        elif self.trade_date:
            from datetime import date as dt_date
            dt_date.fromisoformat(self.trade_date)
        else:
            from datetime import date as dt_date
            self.trade_date = dt_date.today().isoformat()

        normalized: list[str] = []
        seen: set[str] = set()
        for name in self.sector_names:
            value = (name or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            normalized.append(value)
        if len(normalized) < 2:
            raise ValueError("sector_names must contain at least 2 distinct non-empty sector names")
        self.sector_names = normalized
        return self


class SectorLookupRequest(BaseModel):
    mode: SectorLookupMode = ...  # type: ignore[assignment]
    sector_type: SectorType | None = None
    sector_name: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    provider: Literal["zhitu"] | None = "zhitu"

    @model_validator(mode="after")
    def validate_request(self):
        from ._types import SectorLookupMode
        if self.mode == "list" and self.sector_type is None:
            self.sector_type = "concept"
        if self.mode == "children" and self.sector_type is None:
            self.sector_type = "primary"
        if self.mode in {"members", "children"} and not self.sector_name:
            raise ValueError("sector_name is required when mode=members/children")
        return self


class SectorQuoteRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, max_length=50)
    sector_type: Literal["primary", "concept"] | None = None
    sort_by: Literal["change_percent", "turnover"] | None = None
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=50)
    min_turnover: float | None = Field(default=None, ge=0)
    min_change_percent: float | None = None
    exclude_null_fields: bool = False
    return_mode: Literal["full", "ranked_only"] = "full"
    provider: Literal["zhitu"] | None = "zhitu"


class SectorLeadersRequest(BaseModel):
    sector_name: str = Field(min_length=1)
    sector_type: Literal["primary", "concept"] = "primary"
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: Literal["zhitu"] | None = "zhitu"
    sort_by: Literal["relative_strength", "return", "volume_ratio", "max_drawdown"] = "relative_strength"
    descending: bool = True
    top_n: int = Field(default=3, ge=1, le=20)
    limit: int = Field(default=100, ge=1, le=500)
    return_mode: Literal["full", "ranked_only"] = "full"
    min_relative_strength: float | None = None
    min_return: float | None = None
    max_drawdown_limit: float | None = None
    min_volume_ratio: float | None = None

    @model_validator(mode="after")
    def validate_request(self):
        self.trade_date, self.start_date, self.end_date = validate_date_range(
            self.trade_date, self.start_date, self.end_date
        )
        return self


class IndustryValuationRankRequest(BaseModel):
    sector_names: list[str] = Field(min_length=1, max_length=30)
    sector_type: SectorType = "primary"
    sort_by: Literal["pe_median", "pb_median", "valuation_percentile", "quote_coverage_count"] = "pe_median"
    descending: bool = False
    top_n: int | None = Field(default=None, ge=1, le=30)
    member_limit: int = Field(default=200, ge=10, le=500)
    provider: Literal["zhitu", "akshare"] | None = "zhitu"

    @model_validator(mode="after")
    def validate_request(self):
        normalized = dedupe_str_list(self.sector_names)
        if not normalized:
            raise ValueError("sector_names must contain at least 1 non-empty name")
        self.sector_names = normalized
        return self


# Rebuild models that reference types imported under `from __future__ import annotations`
# (Pydantic v2 needs explicit rebuild when forward refs can't be resolved at class-creation time)
SectorLookupRequest.model_rebuild(_types_namespace={"SectorLookupMode": SectorLookupMode})

__all__ = [
    "SectorReviewRequest", "SectorRotationReviewRequest", "SectorLookupRequest",
    "SectorQuoteRequest", "SectorLeadersRequest", "SectorValuationRankRequest",
    "IndustryChainRequest",
]


class IndustryChainRequest(BaseModel):
    include: list[Literal["industry_list", "concept_list"]] = Field(
        default=["industry_list"]
    )
    sort_by: Literal["change_pct", "net_inflow", "turnover", "volume", "up_count"] = "change_pct"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=200)
    provider: Literal["akshare"] | None = "akshare"

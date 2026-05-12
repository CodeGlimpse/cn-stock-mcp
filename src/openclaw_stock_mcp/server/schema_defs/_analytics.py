from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ._helpers import (
    dedupe_include,
    dedupe_str_list,
    normalize_interval,
    normalize_pool_type,
    validate_date_range,
)
from ._types import AdjustType, IndicatorType, ProviderName, SectorType


class StockCandidateScanRequest(BaseModel):
    symbols: list[str] | None = Field(default=None, max_length=100)
    sector_names: list[str] | None = Field(default=None, max_length=10)
    sector_type: SectorType = "primary"
    pool_type: str | None = None
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: ProviderName | None = "mixed"
    sort_by: Literal["candidate_score", "relative_strength", "return", "volume_ratio", "max_drawdown"] = "candidate_score"
    descending: bool = True
    top_n: int = Field(default=20, ge=1, le=100)
    limit: int = Field(default=20, ge=1, le=100)
    min_candidate_score: float | None = None
    min_relative_strength: float | None = None
    min_return: float | None = None
    max_drawdown_limit: float | None = None
    min_volume_ratio: float | None = None
    min_up_streak: int | None = Field(default=None, ge=0, le=50)
    max_down_streak: int | None = Field(default=None, ge=0, le=50)
    require_source_tags: list[str] | None = Field(default=None, max_length=20)
    exclude_risk_flags: list[str] | None = Field(default=None, max_length=20)
    must_have_reason_tags: list[str] | None = Field(default=None, max_length=30)
    exclude_reason_tags: list[str] | None = Field(default=None, max_length=30)

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

        self.symbols = dedupe_str_list(self.symbols)
        self.sector_names = dedupe_str_list(self.sector_names)

        if self.pool_type is not None:
            self.pool_type = normalize_pool_type(self.pool_type)

        if not self.symbols and not self.sector_names and not self.pool_type:
            raise ValueError("at least one of symbols/sector_names/pool_type must be provided")

        self.require_source_tags = dedupe_str_list(self.require_source_tags)
        self.exclude_risk_flags = dedupe_str_list(self.exclude_risk_flags)
        self.must_have_reason_tags = dedupe_str_list(self.must_have_reason_tags)
        self.exclude_reason_tags = dedupe_str_list(self.exclude_reason_tags)
        return self


class WatchlistReviewRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, max_length=100)
    watchlist_name: str | None = None
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: Literal["akshare"] | None = "akshare"
    sort_by: Literal["watchlist_score", "relative_strength", "return", "max_drawdown", "volume_ratio"] = "watchlist_score"
    descending: bool = True
    top_n: int = Field(default=20, ge=1, le=100)
    min_watchlist_score: float | None = None
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
        for symbol in self.symbols:
            value = (symbol or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            normalized.append(value)
        if not normalized:
            raise ValueError("symbols must contain at least 1 non-empty symbol")
        self.symbols = normalized
        if self.watchlist_name is not None:
            self.watchlist_name = self.watchlist_name.strip() or None
        return self


class MultiTimeframeReviewRequest(BaseModel):
    symbol: str
    intervals: list[str] = Field(min_length=2, max_length=8)
    indicators: list[IndicatorType] | None = None
    sec_type: Literal["stock", "index", "fund"] = "stock"
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    limit: int = Field(default=120, ge=20, le=500)
    provider: ProviderName | None = "mixed"

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

        normalized: list[str] = []
        seen: set[str] = set()
        for interval in self.intervals:
            mapped = normalize_interval(interval)
            if mapped in seen:
                continue
            seen.add(mapped)
            normalized.append(mapped)
        if len(normalized) < 2:
            raise ValueError("intervals must contain at least 2 distinct valid intervals")
        self.intervals = normalized
        self.indicators = self.indicators or ["macd", "ma", "kdj"]
        return self


class HotThemeTrackerRequest(BaseModel):
    sector_names: list[str] | None = Field(default=None, max_length=20)
    sector_type: SectorType = "primary"
    watch_name: str | None = None
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: Literal["zhitu"] | None = "zhitu"
    sort_by: Literal["avg_relative_strength", "avg_return", "positive_ratio", "stronger_ratio", "sentiment_score", "rotation_score"] = "avg_relative_strength"
    descending: bool = True
    top_n: int = Field(default=5, ge=1, le=20)
    sector_limit: int = Field(default=10, ge=2, le=30)
    member_limit: int = Field(default=20, ge=1, le=200)
    member_top_n: int = Field(default=3, ge=1, le=10)
    pool_top_n: int = Field(default=5, ge=1, le=20)
    include_pool_snapshot: bool = True
    min_relative_strength: float | None = None
    min_return: float | None = None
    max_drawdown_limit: float | None = None
    min_volume_ratio: float | None = None

    @model_validator(mode="after")
    def validate_request(self):
        self.trade_date, self.start_date, self.end_date = validate_date_range(
            self.trade_date, self.start_date, self.end_date
        )
        self.sector_names = dedupe_str_list(self.sector_names)
        if self.sector_names is not None and len(self.sector_names) < 2:
            raise ValueError("sector_names must contain at least 2 distinct non-empty sector names")
        if self.watch_name is not None:
            self.watch_name = self.watch_name.strip() or None
        return self


class EventCalendarRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, max_length=100)
    event_types: list[Literal["dividend", "unlock", "profit"]] | None = None
    start_date: str | None = None
    end_date: str | None = None
    next_event_only: bool = False
    event_priority: list[Literal["dividend", "unlock", "profit"]] | None = None
    provider: Literal["zhitu"] | None = "zhitu"

    @model_validator(mode="after")
    def validate_request(self):
        from ._helpers import validate_date_order
        validate_date_order(self.start_date, self.end_date)
        if self.event_types is not None:
            self.event_types = dedupe_include(self.event_types)  # type: ignore[assignment]
        if self.event_priority is not None:
            self.event_priority = dedupe_include(self.event_priority)  # type: ignore[assignment]
        return self


class IndexComposeRequest(BaseModel):
    index_code: str = Field(min_length=1)
    top_n: int | None = Field(default=None, ge=1, le=1000)
    include_weight: bool = True
    sort_by: Literal["weight", "symbol"] = "weight"
    descending: bool = True
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        self.index_code = (self.index_code or "").strip()
        if not self.index_code:
            raise ValueError("index_code is required")
        return self


__all__ = [
    "StockCandidateScanRequest", "WatchlistReviewRequest",
    "MultiTimeframeReviewRequest", "HotThemeTrackerRequest",
    "EventCalendarRequest", "IndexComposeRequest",
]

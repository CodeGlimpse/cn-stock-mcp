from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MarketValuationSnapshot(BaseModel):
    date: str | None = None
    pe_ttm_median: float | None = None
    pe_ttm_avg: float | None = None
    pe_lyr_median: float | None = None
    pe_lyr_avg: float | None = None
    pb_median: float | None = None
    pb_equal_weight_avg: float | None = None
    pe_ttm_quantile_all: float | None = None
    pe_ttm_quantile_10y: float | None = None
    pb_quantile_all: float | None = None
    pb_quantile_10y: float | None = None
    dividend_yield: float | None = None
    high20_count: int | None = None
    low20_count: int | None = None
    high60_count: int | None = None
    low60_count: int | None = None
    close: float | None = None


class StockValuationItem(BaseModel):
    symbol: str
    name: str | None = None
    pe: float | None = None
    pb: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None
    rank_pe: int | None = None
    rank_pb: int | None = None
    valuation_label: str | None = None
    reason_tags: list[str] = Field(default_factory=list)
    source: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ValuationRankSummary(BaseModel):
    stock_count: int = 0
    pe_available_count: int = 0
    pb_available_count: int = 0
    low_valuation_count: int = 0
    neutral_valuation_count: int = 0
    high_valuation_count: int = 0
    market_temperature: str | None = None
    market_temperature_score: float | None = None


class ValuationRankResult(BaseModel):
    market: MarketValuationSnapshot | None = None
    items: list[StockValuationItem] = Field(default_factory=list)
    summary: ValuationRankSummary | None = None
    source: str = "mixed"

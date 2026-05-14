from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ._helpers import dedupe_str_list, normalize_interval, validate_date_range
from ._types import AdjustType, ProviderName, SecType


class StockSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    sec_types: list[SecType] | None = None
    market: Literal["CN"] = "CN"
    limit: int = Field(default=10, ge=1, le=50)
    provider: Literal["akshare", "zhitu"] | None = None


class StockQuoteRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, max_length=50)
    sec_type: Literal["stock", "index", "fund"] | None = None
    fields: list[str] | None = None
    provider: Literal["akshare", "zhitu"] | None = None
    provider_preference: list[Literal["akshare", "zhitu"]] | None = None


class StockHistoryRequest(BaseModel):
    symbol: str
    interval: str
    sec_type: Literal["stock", "index", "fund"] | None = None
    start_date: str | None = None
    end_date: str | None = None
    limit: int = Field(default=200, ge=1, le=1000)
    adjust: AdjustType = "none"
    provider: Literal["akshare", "zhitu"] | None = None
    provider_preference: list[Literal["akshare", "zhitu"]] | None = None

    @model_validator(mode="after")
    def normalize_interval(self):
        self.interval = normalize_interval(self.interval)
        return self


class StockReviewRequest(BaseModel):
    symbol: str
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        self.trade_date, self.start_date, self.end_date = validate_date_range(
            self.trade_date, self.start_date, self.end_date
        )
        return self


class StockReviewBatchRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, max_length=50)
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    adjust: AdjustType = "none"
    provider: Literal["akshare"] | None = "akshare"
    sort_by: Literal["relative_strength", "return", "max_drawdown", "volume_ratio"] = "relative_strength"
    descending: bool = True
    top_n: int = Field(default=20, ge=1, le=50)
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


class StockOrderbookRequest(BaseModel):
    symbol: str
    sec_type: Literal["stock"] = "stock"
    provider: Literal["zhitu"] | None = "zhitu"


class StockProfileRequest(BaseModel):
    symbol: str = Field(min_length=1)
    include: list[Literal["profile", "dividends", "unlocks", "profits", "valuation"]] | None = None
    provider: Literal["zhitu"] | None = "zhitu"


class StockFinancialRequest(BaseModel):
    symbol: str = Field(min_length=1)
    include: list[Literal["snapshot", "history", "details"]] = Field(default=["snapshot", "history"])
    statement: Literal["income", "balance", "cashflow"] = "income"
    report_date: str | None = None
    history_n: int = Field(default=8, ge=1, le=30)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        from ._helpers import dedupe_include
        if self.report_date:
            from datetime import date as dt_date
            dt_date.fromisoformat(self.report_date)
        if not self.include:
            raise ValueError("include must contain at least one of: snapshot, history, details")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


class ValuationRankRequest(BaseModel):
    symbols: list[str] = Field(min_length=1, max_length=200)
    sec_type: Literal["stock"] = "stock"
    sort_by: Literal["pe", "pb", "market_cap"] = "pe"
    descending: bool = False
    top_n: int | None = Field(default=None, ge=1, le=200)
    provider: Literal["zhitu", "akshare"] | None = "zhitu"

    @model_validator(mode="after")
    def validate_request(self):
        normalized = dedupe_str_list(self.symbols)
        if not normalized:
            raise ValueError("symbols must contain at least 1 non-empty symbol")
        self.symbols = normalized
        return self


class EarningsQualityRequest(BaseModel):
    symbol: str = Field(min_length=1)
    provider: Literal["akshare"] | None = "akshare"


__all__ = [
    "StockSearchRequest", "StockQuoteRequest", "StockHistoryRequest",
    "StockReviewRequest", "StockReviewBatchRequest", "StockOrderbookRequest",
    "StockProfileRequest", "StockFinancialRequest", "ValuationRankRequest",
    "EarningsQualityRequest", "InsiderTradeRequest", "DividendRankRequest",
    "ShareholderChangeRequest",
    "StockRepurchaseRequest",
]


class InsiderTradeRequest(BaseModel):
    include: list[Literal["top10", "change"]] = Field(
        default=["top10", "change"]
    )
    symbol: str
    sec_type: str = "stock"
    quarter: Literal["auto", "20261", "20254", "20253", "20252", "20251", "20244", "20243", "20242", "20241"] = "auto"
    top_n: int | None = Field(default=None, ge=1, le=50)
    provider: Literal["akshare"] | None = "akshare"


class DividendRankRequest(BaseModel):
    include: list[Literal["rank", "plan", "detail"]] = Field(
        default=["rank", "plan"]
    )
    report_date: Literal["latest", "20241231", "20231231", "20221231", "20211231", "20201231"] = "latest"
    symbol: str | None = None
    sec_type: str = "stock"
    sort_by: Literal["avg_annual_dividend", "total_dividend", "dividend_count", "dividend_yield", "cash_dividend_ratio", "eps"] = "avg_annual_dividend"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if "detail" in self.include and not self.symbol:
            raise ValueError("symbol is required when include contains 'detail'")
        return self


class ShareholderChangeRequest(BaseModel):
    include: list[Literal["top10", "change"]] = Field(
        default=["top10", "change"]
    )
    symbol: str | None = None
    sec_type: str = "stock"
    quarter: Literal["auto", "20261", "20254", "20253", "20252", "20251", "20244", "20243", "20242", "20241"] = "auto"
    shareholder_type: Literal["基金", "社保", "QFII", "券商", "保险", "信托", "个人", "其它", None] = None
    sort_by: Literal["total_hold", "new_hold", "increase_hold", "decrease_hold", "float_cap"] = "total_hold"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if "top10" in self.include and not self.symbol:
            raise ValueError("symbol is required when include contains 'top10'")
        return self


class StockRepurchaseRequest(BaseModel):
    status: Literal["all", "董事会预案", "股东大会通过", "实施中", "完成实施"] = "all"
    symbol: str | None = None
    sec_type: str = "stock"
    sort_by: Literal["done_amount", "plan_amount_max", "plan_ratio_max", "latest_price", "start_date"] = "done_amount"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

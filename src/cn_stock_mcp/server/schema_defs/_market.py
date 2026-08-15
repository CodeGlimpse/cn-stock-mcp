from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ._helpers import dedupe_include, validate_date_order, validate_date_range
from ._types import AdjustType, ProviderName


class TradingCalendarRequest(BaseModel):
    market: Literal["CN"] = "CN"
    date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    recent_limit: int = Field(default=5, ge=1, le=60)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        self.date, self.start_date, self.end_date = validate_date_range(
            self.date, self.start_date, self.end_date
        )
        return self


class MarketOverviewRequest(BaseModel):
    market: Literal["CN"] = "CN"
    include: list[str] | None = None
    provider: ProviderName | None = "mixed"


class MarketBriefRequest(BaseModel):
    brief_type: Literal["pre_open", "intraday", "close"] = "close"
    market: Literal["CN"] = "CN"
    trade_date: str | None = None
    include_pools: bool = True
    top_n: int = Field(default=5, ge=1, le=50)
    provider: ProviderName | None = "mixed"


class TechnicalIndicatorRequest(BaseModel):
    symbol: str
    interval: str
    indicator: str
    sec_type: Literal["stock", "index", "fund"] = "index"
    start_date: str | None = None
    end_date: str | None = None
    limit: int = Field(default=200, ge=1, le=2000)
    provider: Literal["zhitu", "akshare"] | None = None

    @model_validator(mode="after")
    def normalize_request(self):
        from ._helpers import normalize_indicator, normalize_interval
        self.interval = normalize_interval(self.interval)
        self.indicator = normalize_indicator(self.indicator)
        return self


class MarketPoolRequest(BaseModel):
    pool_type: str
    trade_date: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    provider: Literal["zhitu"] | None = "zhitu"

    @model_validator(mode="after")
    def normalize_pool_type(self):
        from ._helpers import normalize_pool_type
        self.pool_type = normalize_pool_type(self.pool_type)
        return self


class CapitalFlowRequest(BaseModel):
    flow_type: Literal["market", "individual", "industry", "concept"] = "market"
    symbol: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    limit: int = Field(default=60, ge=1, le=500)
    sort_by: Literal["net_amount", "inflow", "outflow", "sector_change_percent", "company_count"] = "net_amount"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=200)
    allow_stale: bool = Field(default=False, description="Allow a clearly marked cached result when the upstream is unavailable")
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if self.flow_type == "individual" and not self.symbol:
            raise ValueError("symbol is required when flow_type=individual")
        validate_date_order(self.start_date, self.end_date)
        return self


class LimitStatRequest(BaseModel):
    trade_date: str | None = None
    include: list[Literal["summary", "limit_up", "broken_limit", "previous_day", "limit_down"]] = Field(
        default=["summary", "limit_up", "broken_limit", "previous_day"]
    )
    min_consecutive_boards: int | None = Field(default=None, ge=1, le=50)
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if self.trade_date:
            from datetime import date as dt_date
            dt_date.fromisoformat(self.trade_date)
        if not self.include:
            raise ValueError("include must contain at least one of: summary, limit_up, broken_limit, previous_day, limit_down")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


class NorthboundRequest(BaseModel):
    include: list[Literal["daily_summary", "history"]] = Field(default=["daily_summary", "history"])
    history_n: int = Field(default=30, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if not self.include:
            raise ValueError("include must contain at least one of: daily_summary, history")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


class MarginTradingRequest(BaseModel):
    include: list[Literal["summary", "detail"]] = Field(default=["summary", "detail"])
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    exchange: Literal["SSE", "SZSE", "both"] = Field(default="both", description="交易所选择")
    sort_by: Literal["financing_buy", "financing_balance", "securities_sell", "securities_volume"] = "financing_buy"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        self.trade_date, self.start_date, self.end_date = validate_date_range(
            self.trade_date, self.start_date, self.end_date
        )
        if not self.include:
            raise ValueError("include must contain at least one of: summary, detail")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


__all__ = [
    "TradingCalendarRequest", "MarketOverviewRequest", "MarketBriefRequest",
    "TechnicalIndicatorRequest", "MarketPoolRequest", "CapitalFlowRequest",
    "LimitStatRequest", "NorthboundRequest", "MarginTradingRequest",
    "StockScreenRequest",
    "DisclosureCalendarRequest",
    "FundFlowRequest",
    "LimitUpPoolRequest",
]


class StockScreenRequest(BaseModel):
    market: Literal["all", "sh", "sz", "bj", "main", "star", "gem"] = "all"
    min_price: float | None = Field(default=None, description="Minimum latest price (inclusive)")
    max_price: float | None = Field(default=None, description="Maximum latest price (inclusive)")
    min_change_pct: float | None = Field(default=None, description="Minimum change percent (inclusive)")
    max_change_pct: float | None = Field(default=None, description="Maximum change percent (inclusive)")
    min_volume: float | None = Field(default=None, description="Minimum volume (inclusive)")
    min_turnover: float | None = Field(default=None, description="Minimum turnover (CNY, inclusive)")
    min_amplitude: float | None = Field(default=None, description="Minimum amplitude percent (inclusive)")
    sort_by: Literal["change_pct", "turnover", "volume", "latest_price", "amplitude"] = "change_pct"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"


class DisclosureCalendarRequest(BaseModel):
    market: Literal["沪深京", "深市", "沪市", "京市"] = "沪深京"
    period: str = Field(default="auto", description="报告期：YYYY年报/YYYY一季/YYYY半年/YYYY三季，如 '2024年报'/'2025一季'，或 'auto'")
    symbol: str | None = None
    sec_type: str = "stock"
    status: Literal["all", "disclosed", "pending", "changed"] = "all"
    sort_by: Literal["first_schedule", "actual_date"] = "first_schedule"
    descending: bool = False
    top_n: int | None = Field(default=None, ge=1, le=1000)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_period(self):
        if self.period == "auto":
            from datetime import date
            today = date.today()
            year = today.year
            month = today.month
            if month <= 4:
                self.period = f"{year - 1}年报"
            elif month <= 5:
                self.period = f"{year}一季"
            elif month <= 8:
                self.period = f"{year}半年"
            elif month <= 10:
                self.period = f"{year}三季"
            else:
                self.period = f"{year}年报"
        return self


class FundFlowRequest(BaseModel):
    include: list[Literal["market", "industry", "stock"]] = Field(
        default=["market", "industry"]
    )
    period: Literal["即时", "3日", "5日", "10日"] = "即时"
    symbol: str | None = Field(default=None, description="Stock code required when include='stock', e.g. 600519")
    sort_by: Literal["net_inflow", "inflow", "change_pct"] = "net_inflow"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=200)
    provider: Literal["akshare"] | None = "akshare"


class LimitUpPoolRequest(BaseModel):
    include: list[Literal["limit_up", "limit_down", "strong", "previous", "sub_new", "broken"]] = Field(
        default=["limit_up", "limit_down", "strong"]
    )
    trade_date: str | None = Field(default=None, description="YYYYMMDD, defaults to today")
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

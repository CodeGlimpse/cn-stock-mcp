from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

SecType = Literal["stock", "index", "fund", "sector"]
ProviderName = Literal["akshare", "zhitu", "mixed"]
Interval = Literal["1m", "5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]
AdjustType = Literal["none", "qfq", "hfq"]
IndicatorType = Literal["macd", "ma", "boll", "kdj"]
PoolType = Literal["limit_up", "limit_down", "strong"]
SectorLookupMode = Literal["list", "members", "children"]
SectorType = Literal["concept", "primary"]


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
        raw = (self.interval or "").strip()
        alias = {
            "5": "5m",
            "15": "15m",
            "30": "30m",
            "60": "60m",
            "d": "1d",
            "w": "1w",
            "m": "1M",
            "y": "1y",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "60m": "60m",
            "1d": "1d",
            "1w": "1w",
            "1m": "1M",
            "1y": "1y",
        }
        normalized = alias.get(raw.lower())
        if not normalized:
            raise ValueError("interval must be one of: 5/15/30/60/d/w/m/y or 5m/15m/30m/60m/1d/1w/1M/1y")
        self.interval = normalized
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
        interval_raw = (self.interval or "").strip()
        interval_alias = {
            "5": "5m",
            "15": "15m",
            "30": "30m",
            "60": "60m",
            "d": "1d",
            "w": "1w",
            "m": "1M",
            "y": "1y",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "60m": "60m",
            "1d": "1d",
            "1w": "1w",
            "1m": "1M",
            "1y": "1y",
        }
        interval_normalized = interval_alias.get(interval_raw.lower())
        if not interval_normalized:
            raise ValueError("interval must be one of: 5/15/30/60/d/w/m/y or 5m/15m/30m/60m/1d/1w/1M/1y")

        indicator_raw = (self.indicator or "").strip().lower()
        indicator_alias = {
            "macd": "macd",
            "ma": "ma",
            "boll": "boll",
            "kdj": "kdj",
        }
        indicator_normalized = indicator_alias.get(indicator_raw)
        if not indicator_normalized:
            raise ValueError("indicator must be one of: macd/ma/boll/kdj")

        self.interval = interval_normalized
        self.indicator = indicator_normalized
        return self


class MarketPoolRequest(BaseModel):
    pool_type: str
    trade_date: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    provider: Literal["zhitu"] | None = "zhitu"

    @model_validator(mode="after")
    def normalize_pool_type(self):
        raw = (self.pool_type or "").strip().lower()
        alias = {
            "limit_up": "limit_up",
            "ztgc": "limit_up",
            "up": "limit_up",
            "涨停": "limit_up",
            "limit_down": "limit_down",
            "dtgc": "limit_down",
            "down": "limit_down",
            "跌停": "limit_down",
            "strong": "strong",
            "qsgc": "strong",
            "强势": "strong",
        }
        normalized = alias.get(raw)
        if not normalized:
            raise ValueError(
                "pool_type must be one of: limit_up/limit_down/strong "
                "(aliases: ztgc/dtgc/qsgc, up/down, 涨停/跌停/强势)"
            )
        self.pool_type = normalized
        return self


class StockOrderbookRequest(BaseModel):
    symbol: str
    sec_type: Literal["stock"] = "stock"
    provider: Literal["zhitu"] | None = "zhitu"


class SectorLookupRequest(BaseModel):
    mode: SectorLookupMode
    sector_type: SectorType | None = None
    sector_name: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    provider: Literal["zhitu"] | None = "zhitu"

    @model_validator(mode="after")
    def validate_request(self):
        if self.mode == "list" and self.sector_type is None:
            self.sector_type = "concept"

        if self.mode == "children" and self.sector_type is None:
            self.sector_type = "primary"

        if self.mode in {"members", "children"} and not self.sector_name:
            raise ValueError("sector_name is required when mode=members/children")

        return self

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SecType = Literal["stock", "index", "fund", "sector"]
ProviderName = Literal["akshare", "zhitu", "mixed"]
Interval = Literal["1m", "5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]
AdjustType = Literal["none", "qfq", "hfq"]
IndicatorType = Literal["macd", "ma", "boll", "kdj"]
PoolType = Literal["limit_up", "limit_down", "strong"]


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
    interval: Interval
    sec_type: Literal["stock", "index", "fund"] | None = None
    start_date: str | None = None
    end_date: str | None = None
    limit: int = Field(default=200, ge=1, le=1000)
    adjust: AdjustType = "none"
    provider: Literal["akshare", "zhitu"] | None = None
    provider_preference: list[Literal["akshare", "zhitu"]] | None = None


class MarketOverviewRequest(BaseModel):
    market: Literal["CN"] = "CN"
    include: list[str] | None = None
    provider: ProviderName | None = "mixed"


class TechnicalIndicatorRequest(BaseModel):
    symbol: str
    interval: Literal["5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]
    indicator: IndicatorType
    sec_type: Literal["stock", "index", "fund"] = "index"
    start_date: str | None = None
    end_date: str | None = None
    limit: int = Field(default=200, ge=1, le=2000)
    provider: Literal["zhitu", "akshare"] | None = None


class MarketPoolRequest(BaseModel):
    pool_type: PoolType
    trade_date: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    provider: Literal["zhitu"] | None = "zhitu"


class StockOrderbookRequest(BaseModel):
    symbol: str
    sec_type: Literal["stock"] = "stock"
    provider: Literal["zhitu"] | None = "zhitu"


class SectorLookupRequest(BaseModel):
    mode: Literal["list", "members"]
    sector_type: Literal["concept", "primary"] | None = None
    sector_name: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    provider: Literal["zhitu"] | None = "zhitu"

from __future__ import annotations

from datetime import date as dt_date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

SecType = Literal["stock", "index", "fund", "sector"]
ProviderName = Literal["akshare", "zhitu", "mixed"]
Interval = Literal["5m", "15m", "30m", "60m", "1d", "1w", "1M", "1y"]
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
            "1m": None,
            "1y": "1y",
        }
        normalized = alias.get(raw.lower())
        if normalized is None:
            raise ValueError(
                "interval must be one of: 5/15/30/60/d/w/m/y or 5m/15m/30m/60m/1d/1w/1M/1y; 1m is not supported in current version"
            )
        self.interval = normalized
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
        if self.trade_date and (self.start_date or self.end_date):
            raise ValueError("trade_date cannot be combined with start_date/end_date")

        if self.start_date or self.end_date:
            if not self.start_date or not self.end_date:
                raise ValueError("start_date and end_date must be provided together")
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
            return self

        if self.trade_date:
            dt_date.fromisoformat(self.trade_date)
            return self

        self.trade_date = dt_date.today().isoformat()
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
        if self.trade_date and (self.start_date or self.end_date):
            raise ValueError("trade_date cannot be combined with start_date/end_date")

        if self.start_date or self.end_date:
            if not self.start_date or not self.end_date:
                raise ValueError("start_date and end_date must be provided together")
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
            return self

        if self.trade_date:
            dt_date.fromisoformat(self.trade_date)
            return self

        self.trade_date = dt_date.today().isoformat()
        return self


class TradingCalendarRequest(BaseModel):
    market: Literal["CN"] = "CN"
    date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    recent_limit: int = Field(default=5, ge=1, le=60)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if self.date and (self.start_date or self.end_date):
            raise ValueError("date cannot be combined with start_date/end_date")

        if self.start_date or self.end_date:
            if not self.start_date or not self.end_date:
                raise ValueError("start_date and end_date must be provided together")
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
            return self

        if self.date:
            dt_date.fromisoformat(self.date)
            return self

        self.date = dt_date.today().isoformat()
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
            "1m": None,
            "1y": "1y",
        }
        interval_normalized = interval_alias.get(interval_raw.lower())
        if interval_normalized is None:
            raise ValueError(
                "interval must be one of: 5/15/30/60/d/w/m/y or 5m/15m/30m/60m/1d/1w/1M/1y; 1m is not supported in current version"
            )

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


class SectorReviewRequest(BaseModel):
    sector_name: str = Field(min_length=1)
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
        if self.trade_date and (self.start_date or self.end_date):
            raise ValueError("trade_date cannot be combined with start_date/end_date")

        if self.start_date or self.end_date:
            if not self.start_date or not self.end_date:
                raise ValueError("start_date and end_date must be provided together")
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
            return self

        if self.trade_date:
            dt_date.fromisoformat(self.trade_date)
            return self

        self.trade_date = dt_date.today().isoformat()
        return self


class SectorRotationReviewRequest(BaseModel):
    sector_names: list[str] = Field(min_length=2, max_length=15)
    sector_type: Literal["primary"] = "primary"
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
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
        elif self.trade_date:
            dt_date.fromisoformat(self.trade_date)
        else:
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


class StockCandidateScanRequest(BaseModel):
    symbols: list[str] | None = Field(default=None, max_length=100)
    sector_names: list[str] | None = Field(default=None, max_length=10)
    sector_type: Literal["primary"] = "primary"
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

    @model_validator(mode="after")
    def validate_request(self):
        if self.trade_date and (self.start_date or self.end_date):
            raise ValueError("trade_date cannot be combined with start_date/end_date")

        if self.start_date or self.end_date:
            if not self.start_date or not self.end_date:
                raise ValueError("start_date and end_date must be provided together")
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
        elif self.trade_date:
            dt_date.fromisoformat(self.trade_date)
        else:
            self.trade_date = dt_date.today().isoformat()

        normalized_symbols: list[str] = []
        seen_symbols: set[str] = set()
        for symbol in self.symbols or []:
            value = (symbol or "").strip()
            if not value or value in seen_symbols:
                continue
            seen_symbols.add(value)
            normalized_symbols.append(value)
        self.symbols = normalized_symbols or None

        normalized_sectors: list[str] = []
        seen_sectors: set[str] = set()
        for name in self.sector_names or []:
            value = (name or "").strip()
            if not value or value in seen_sectors:
                continue
            seen_sectors.add(value)
            normalized_sectors.append(value)
        self.sector_names = normalized_sectors or None

        if self.pool_type is not None:
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
            normalized_pool = alias.get(raw)
            if not normalized_pool:
                raise ValueError(
                    "pool_type must be one of: limit_up/limit_down/strong "
                    "(aliases: ztgc/dtgc/qsgc, up/down, 涨停/跌停/强势)"
                )
            self.pool_type = normalized_pool

        if not self.symbols and not self.sector_names and not self.pool_type:
            raise ValueError("at least one of symbols/sector_names/pool_type must be provided")

        def _norm_list(values: list[str] | None) -> list[str] | None:
            normalized: list[str] = []
            seen: set[str] = set()
            for raw in values or []:
                value = (raw or "").strip()
                if not value or value in seen:
                    continue
                seen.add(value)
                normalized.append(value)
            return normalized or None

        self.require_source_tags = _norm_list(self.require_source_tags)
        self.exclude_risk_flags = _norm_list(self.exclude_risk_flags)

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
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
        elif self.trade_date:
            dt_date.fromisoformat(self.trade_date)
        else:
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
            start = dt_date.fromisoformat(self.start_date)
            end = dt_date.fromisoformat(self.end_date)
            if start > end:
                raise ValueError("start_date must be <= end_date")
        elif self.trade_date:
            dt_date.fromisoformat(self.trade_date)

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
            "1m": None,
            "1y": "1y",
        }
        normalized: list[str] = []
        seen: set[str] = set()
        for interval in self.intervals:
            raw = (interval or "").strip()
            mapped = interval_alias.get(raw.lower())
            if mapped is None:
                raise ValueError(
                    "intervals must contain only: 5/15/30/60/d/w/m/y or 5m/15m/30m/60m/1d/1w/1M/1y; 1m is not supported in current version"
                )
            if mapped in seen:
                continue
            seen.add(mapped)
            normalized.append(mapped)

        if len(normalized) < 2:
            raise ValueError("intervals must contain at least 2 distinct valid intervals")

        self.intervals = normalized
        self.indicators = self.indicators or ["macd", "ma", "kdj"]
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

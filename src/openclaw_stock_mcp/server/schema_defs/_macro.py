from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ._helpers import dedupe_include, validate_date_order, validate_date_range


class MacroIndicatorRequest(BaseModel):
    indicator: str = Field(min_length=1)
    region: Literal["cn", "usa", "euro", "global"] = "cn"
    include: list[Literal["latest", "history", "calendar", "overview"]] = Field(default=["latest"])
    history_n: int = Field(default=12, ge=1, le=500)
    start_date: str | None = None
    end_date: str | None = None
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        validate_date_order(self.start_date, self.end_date)
        if not self.include:
            raise ValueError("include must contain at least one of: latest, history, calendar, overview")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


class DragonTigerRequest(BaseModel):
    include: list[Literal["daily_detail", "institution", "active_broker", "broker_rank", "stock_stat"]] = Field(
        default=["daily_detail", "institution"]
    )
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    period: Literal["近一月", "近三月", "近六月", "近一年"] = "近一月"
    sort_by: Literal["net_buy_amount", "turnover_amount", "buy_amount", "inst_net_buy", "listed_count"] = "net_buy_amount"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        self.trade_date, self.start_date, self.end_date = validate_date_range(
            self.trade_date, self.start_date, self.end_date
        )
        if not self.include:
            raise ValueError("include must contain at least one of: daily_detail, institution, active_broker, broker_rank, stock_stat")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


class ETFSnapshotRequest(BaseModel):
    include: list[Literal["spot", "scale", "nav"]] = Field(default=["spot"])
    symbol: str | None = Field(default=None, min_length=1)
    sort_by: Literal["turnover", "change_percent", "discount_rate", "main_net_inflow", "volume", "total_market_cap"] = "turnover"
    descending: bool = True
    top_n: int = Field(default=20, ge=1, le=200)
    min_discount: float | None = Field(default=None, description="折价率下限筛选（负数=折价）")
    max_discount: float | None = Field(default=None, description="溢价率上限筛选（正数=溢价）")
    history_n: int = Field(default=30, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if "nav" in self.include and not self.symbol:
            raise ValueError("symbol is required when include contains 'nav'")
        if not self.include:
            raise ValueError("include must contain at least one of: spot, scale, nav")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        if self.symbol:
            raw = self.symbol.strip()
            self._raw_code = raw.split(".")[0] if "." in raw else raw
        return self


class ConvertibleBondRequest(BaseModel):
    include: list[Literal["spot", "redeem", "index"]] = Field(default=["spot"])
    sort_by: Literal["double_low", "conv_premium", "ytm", "change_percent", "turnover", "remaining_years"] = "double_low"
    descending: bool = False
    top_n: int | None = Field(default=None, ge=1, le=500)
    min_double_low: float | None = Field(default=None, description="双低下限")
    max_double_low: float | None = Field(default=None, description="双低上限")
    max_conv_premium: float | None = Field(default=None, description="溢价率上限筛选")
    min_ytm: float | None = Field(default=None, description="到期收益率下限筛选")
    call_status_filter: Literal["all", "called", "near_call", "safe"] | None = Field(default=None, description="强赎状态筛选")
    history_n: int = Field(default=60, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if not self.include:
            raise ValueError("include must contain at least one of: spot, redeem, index")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


class DerivativesDataRequest(BaseModel):
    include: list[Literal["futures_spot", "futures_hist", "option_list", "qvix"]] = Field(
        default=["futures_spot", "qvix"]
    )
    futures_symbol: str = Field(default="RB0", description="期货合约代码，如 RB0=螺纹钢主力, I0=铁矿石主力, AU0=黄金主力")
    option_exchange: Literal["SSE", "SZSE", "both"] = Field(default="both", description="期权交易所选择")
    qvix_underlying: Literal["50etf", "300etf", "500etf", "100etf", "50index", "300index", "1000index", "kcb", "cyb"] = Field(default="50etf")
    history_n: int = Field(default=60, ge=1, le=500)
    option_type_filter: Literal["all", "call", "put"] = Field(default="all", description="认购/认沽筛选")
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        if not self.include:
            raise ValueError("include must contain at least one of: futures_spot, futures_hist, option_list, qvix")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


class BlockTradeRequest(BaseModel):
    include: list[Literal["daily_detail", "daily_stat", "industry_stat", "broker_rank", "active_stock"]] = Field(
        default=["daily_detail", "daily_stat"]
    )
    trade_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    period: Literal["近一月", "近三月", "近六月", "近一年"] = "近一月"
    industry_period: Literal["近3日", "近5日", "近10日", "近30日"] = "近3日"
    sort_by: Literal["turnover", "discount_rate", "turnover_to_float_cap", "listed_count", "avg_return_5d"] = "turnover"
    descending: bool = True
    top_n: int | None = Field(default=None, ge=1, le=500)
    provider: Literal["akshare"] | None = "akshare"

    @model_validator(mode="after")
    def validate_request(self):
        self.trade_date, self.start_date, self.end_date = validate_date_range(
            self.trade_date, self.start_date, self.end_date
        )
        if not self.include:
            raise ValueError("include must contain at least one of: daily_detail, daily_stat, industry_stat, broker_rank, active_stock")
        self.include = dedupe_include(self.include)  # type: ignore[assignment]
        return self


__all__ = [
    "MacroIndicatorRequest", "DragonTigerRequest", "ETFSnapshotRequest",
    "ConvertibleBondRequest", "DerivativesDataRequest", "BlockTradeRequest",
]

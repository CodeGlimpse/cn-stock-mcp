from __future__ import annotations

from pydantic import BaseModel, Field


class SeatDetailItem(BaseModel):
    rank: int | None = None
    broker_name: str | None = None
    buy_amount: float | None = None
    buy_ratio: float | None = None
    sell_amount: float | None = None
    sell_ratio: float | None = None
    net_amount: float | None = None
    reason_type: str | None = None
    side: str | None = None
    source: str = "akshare"


class ActiveBrokerItem(BaseModel):
    rank: int | None = None
    broker_name: str | None = None
    trade_date: str | None = None
    buy_stock_count: int | None = None
    sell_stock_count: int | None = None
    buy_amount: float | None = None
    sell_amount: float | None = None
    net_amount: float | None = None
    bought_stocks: str | None = None
    broker_code: str | None = None
    source: str = "akshare"


class InstitutionDetailItem(BaseModel):
    code: str | None = None
    name: str | None = None
    trade_date: str | None = None
    inst_buy_amount: float | None = None
    inst_sell_amount: float | None = None
    inst_net_amount: float | None = None
    reason_type: str | None = None
    source: str = "akshare"


class InstitutionTraceItem(BaseModel):
    code: str | None = None
    name: str | None = None
    total_buy_amount: float | None = None
    buy_count: int | None = None
    total_sell_amount: float | None = None
    sell_count: int | None = None
    net_amount: float | None = None
    source: str = "akshare"


class SecRevealResult(BaseModel):
    stock_seat_buy: list[SeatDetailItem] = Field(default_factory=list)
    stock_seat_buy_count: int = 0
    stock_seat_sell: list[SeatDetailItem] = Field(default_factory=list)
    stock_seat_sell_count: int = 0
    active_broker: list[ActiveBrokerItem] = Field(default_factory=list)
    active_broker_count: int = 0
    institution_detail: list[InstitutionDetailItem] = Field(default_factory=list)
    institution_detail_count: int = 0
    institution_trace: list[InstitutionTraceItem] = Field(default_factory=list)
    institution_trace_count: int = 0
    summary: str = ""

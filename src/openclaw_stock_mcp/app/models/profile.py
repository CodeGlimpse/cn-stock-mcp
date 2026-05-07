from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class StockProfile(BaseModel):
    symbol: str
    name: str | None = None
    ename: str | None = None
    market: str | None = None
    list_date: str | None = None
    issue_price: str | None = None
    registered_capital: str | None = None
    industry: str | None = None
    organization_type: str | None = None
    business_scope: str | None = None
    description: str | None = None
    concepts: list[str] = []
    address: str | None = None
    office_address: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    secretary: str | None = None
    source: str


class DividendRecord(BaseModel):
    announce_date: str | None = None
    bonus_per_10: float | None = None
    transfer_per_10: float | None = None
    dividend_per_10: float | None = None
    progress: str | None = None
    ex_dividend_date: str | None = None
    record_date: str | None = None


class UnlockRecord(BaseModel):
    unlock_date: str | None = None
    unlock_amount: float | None = None
    unlock_value: float | None = None
    batch: int | None = None
    announce_date: str | None = None


class QuarterProfit(BaseModel):
    period: str | None = None
    revenue: float | None = None
    net_profit: float | None = None
    eps: float | None = None


class StockProfileDetail(BaseModel):
    profile: StockProfile
    dividends: list[DividendRecord] = []
    unlocks: list[UnlockRecord] = []
    quarter_profits: list[QuarterProfit] = []
    dividend_summary: dict | None = None
    unlock_risk: dict | None = None
    source: str

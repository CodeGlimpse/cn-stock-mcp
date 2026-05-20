from __future__ import annotations

from pydantic import BaseModel


class MarketFundFlowItem(BaseModel):
    date: str | None
    sh_close: float | None
    sh_change_pct: float | None
    sz_close: float | None
    sz_change_pct: float | None
    main_net_inflow: float | None
    main_net_pct: float | None
    huge_net_inflow: float | None
    huge_net_pct: float | None
    big_net_inflow: float | None
    big_net_pct: float | None
    mid_net_inflow: float | None
    mid_net_pct: float | None
    small_net_inflow: float | None
    small_net_pct: float | None
    source: str = "akshare"


class IndustryFundFlowItem(BaseModel):
    name: str | None
    index: float | None
    change_pct: float | None
    inflow: float | None
    outflow: float | None
    net_inflow: float | None
    company_count: int | None
    leader: str | None
    leader_change_pct: float | None
    leader_price: float | None
    source: str = "akshare"


class StockFundFlowItem(BaseModel):
    date: str | None
    close: float | None
    change_pct: float | None
    main_net_inflow: float | None
    main_net_pct: float | None
    huge_net_inflow: float | None
    huge_net_pct: float | None
    big_net_inflow: float | None
    big_net_pct: float | None
    mid_net_inflow: float | None
    mid_net_pct: float | None
    small_net_inflow: float | None
    small_net_pct: float | None
    source: str = "akshare"


class FundFlowResult(BaseModel):
    market: list[MarketFundFlowItem] = []
    market_count: int = 0
    industry: list[IndustryFundFlowItem] = []
    industry_count: int = 0
    stock: list[StockFundFlowItem] = []
    stock_count: int = 0
    summary: str = ""

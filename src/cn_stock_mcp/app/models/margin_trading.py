from __future__ import annotations

from pydantic import BaseModel, Field


class MarginSummaryItem(BaseModel):
    """Market-level margin trading summary for a single date."""

    trade_date: str | None = None
    financing_balance: float | None = None      # 融资余额（元）
    financing_buy: float | None = None          # 融资买入额（元）
    financing_repay: float | None = None        # 融资偿还额（元，SSE only）
    securities_volume: float | None = None       # 融券余量（股）
    securities_amount: float | None = None       # 融券余量金额（元）
    securities_sell: float | None = None        # 融券卖出量（股）
    total_balance: float | None = None          # 融资融券余额（元）
    exchange: str | None = None                  # SSE/SZSE


class MarginDetailItem(BaseModel):
    """Stock-level margin trading detail for a single date."""

    symbol: str
    name: str | None = None
    financing_balance: float | None = None      # 融资余额（元）
    financing_buy: float | None = None          # 融资买入额（元）
    financing_repay: float | None = None        # 融资偿还额（元，SSE only）
    securities_volume: float | None = None       # 融券余量（股）
    securities_sell: float | None = None        # 融券卖出量（股）
    securities_repay: float | None = None       # 融券偿还量（股，SSE only）
    securities_amount: float | None = None       # 融券余额（元，SZSE only）
    total_balance: float | None = None          # 融资融券余额（元，SZSE only）
    exchange: str | None = None


class MarginTradingResult(BaseModel):
    """Full result for margin_trading tool."""

    summary: list[MarginSummaryItem] = Field(default_factory=list)
    summary_count: int = 0
    detail: list[MarginDetailItem] = Field(default_factory=list)
    detail_count: int = 0
    summary_text: str = ""
    source: str = "akshare"

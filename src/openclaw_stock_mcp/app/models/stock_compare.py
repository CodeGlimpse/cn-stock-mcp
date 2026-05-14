from __future__ import annotations

from pydantic import BaseModel


class StockCompareItem(BaseModel):
    """多股横向对比条目"""
    symbol: str
    name: str
    # quote fields (Sina)
    latest_price: float | None = None
    change_pct: float | None = None
    volume: float | None = None
    turnover: float | None = None
    amplitude: float | None = None
    # valuation fields (Zhitu)
    pe: float | None = None
    pb: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None
    turnover_rate: float | None = None
    # financial fields (AKShare)
    revenue: float | None = None
    net_profit: float | None = None
    roe: float | None = None
    gross_margin: float | None = None
    debt_ratio: float | None = None
    # dividend fields
    dividend_yield: float | None = None
    eps: float | None = None
    # meta
    source_quote: str = ""
    source_valuation: str = ""
    source_financial: str = ""


class StockCompareResult(BaseModel):
    items: list[StockCompareItem] = []
    total_count: int = 0
    symbols_compared: list[str] = []
    summary: str = ""

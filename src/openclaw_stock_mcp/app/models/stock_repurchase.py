from __future__ import annotations

from pydantic import BaseModel


class RepurchaseItem(BaseModel):
    """回购明细条目"""
    symbol: str
    name: str
    latest_price: float | None
    plan_price_range: str | None
    plan_qty_min: float | None
    plan_qty_max: float | None
    plan_ratio_min: float | None
    plan_ratio_max: float | None
    plan_amount_min: float | None
    plan_amount_max: float | None
    start_date: str | None
    progress: str | None
    done_price_min: float | None
    done_price_max: float | None
    done_qty: float | None
    done_amount: float | None
    latest_announce_date: str | None
    source: str = "akshare"


class RepurchaseResult(BaseModel):
    items: list[RepurchaseItem] = []
    total_count: int = 0
    summary: str = ""

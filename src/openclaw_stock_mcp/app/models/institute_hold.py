from __future__ import annotations

from pydantic import BaseModel


class InstituteHoldSummaryItem(BaseModel):
    """全市场个股机构持仓汇总"""
    symbol: str
    name: str
    institute_count: int | None
    institute_count_change: int | None
    hold_ratio: float | None
    hold_ratio_change: float | None
    float_ratio: float | None
    float_ratio_change: float | None
    source: str = "akshare"


class InstituteHoldDetailItem(BaseModel):
    """单股机构持仓明细"""
    institute_type: str | None
    institute_code: str | None
    institute_name: str | None
    institute_full_name: str | None
    hold_count: float | None
    latest_hold_count: float | None
    hold_ratio: float | None
    latest_hold_ratio: float | None
    float_ratio: float | None
    latest_float_ratio: float | None
    hold_ratio_change: float | None
    float_ratio_change: float | None
    source: str = "akshare"


class InstituteHoldResult(BaseModel):
    summary: list[InstituteHoldSummaryItem] = []
    summary_count: int = 0
    detail: list[InstituteHoldDetailItem] = []
    detail_count: int = 0
    quarter: str = ""
    effective_quarter: str = ""
    summary_text: str = ""

from __future__ import annotations

from openclaw_stock_mcp.app.models.shareholder_change import (
    ShareholderChangeItem,
    ShareholderTop10Item,
)


def _to_float(value):
    if value is None or value == "" or value == "不变" or value == "NaN":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    if value is None or value == "" or value == "NaN":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clean_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s and s != "NaN" and s != "NaT" else None


def adapt_top10_row(row: dict) -> ShareholderTop10Item:
    return ShareholderTop10Item(
        rank=_to_int(row.get("名次")),
        shareholder_name=_clean_str(row.get("股东名称")),
        share_type=_clean_str(row.get("股份类型")),
        hold_count=_to_float(row.get("持股数")),
        hold_ratio=_to_float(row.get("占总股本持股比例")),
        change=_clean_str(row.get("增减")),
        change_ratio=_to_float(row.get("变动比率")),
    )


def adapt_change_row(row: dict) -> ShareholderChangeItem:
    return ShareholderChangeItem(
        shareholder_name=_clean_str(row.get("股东名称")),
        shareholder_type=_clean_str(row.get("股东类型")),
        total_hold=_to_int(row.get("期末持股只数统计-总持有")),
        new_hold=_to_int(row.get("期末持股只数统计-新进")),
        increase_hold=_to_int(row.get("期末持股只数统计-增加")),
        unchanged_hold=_to_int(row.get("期末持股只数统计-不变")),
        decrease_hold=_to_int(row.get("期末持股只数统计-减少")),
        float_cap=_to_float(row.get("流通市值统计")),
        held_stocks=_clean_str(row.get("持有个股")),
    )


def build_shareholder_summary(top10: list, change: list, symbol: str, quarter: str) -> str:
    parts = []
    if top10:
        increasing = [t for t in top10 if t.change_ratio is not None and t.change_ratio > 0]
        decreasing = [t for t in top10 if t.change_ratio is not None and t.change_ratio < 0]
        parts.append(f"十大股东：增持 {len(increasing)} 减持 {len(decreasing)}")
    if change:
        net_buy = [c for c in change if c.new_hold is not None and c.new_hold > 0]
        parts.append(f"股东变动 {len(change)} 家（新进 {len(net_buy)} 家）")
    if not parts:
        return f"{symbol}（{quarter}）：无股东变动数据"
    return f"（{quarter}）" + "；".join(parts)

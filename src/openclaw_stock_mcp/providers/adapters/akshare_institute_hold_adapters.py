from __future__ import annotations

from openclaw_stock_mcp.app.models.institute_hold import (
    InstituteHoldDetailItem,
    InstituteHoldSummaryItem,
)
from openclaw_stock_mcp.infra.time_utils import normalize_symbol


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def adapt_institute_hold_summary_row(row: dict) -> InstituteHoldSummaryItem:
    raw_code = str(row.get("证券代码", "")).strip()
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return InstituteHoldSummaryItem(
        symbol=symbol,
        name=str(row.get("证券简称", "")).strip(),
        institute_count=_to_int(row.get("机构数")),
        institute_count_change=_to_int(row.get("机构数变化")),
        hold_ratio=_to_float(row.get("持股比例")),
        hold_ratio_change=_to_float(row.get("持股比例增幅")),
        float_ratio=_to_float(row.get("占流通股比例")),
        float_ratio_change=_to_float(row.get("占流通股比例增幅")),
    )


def adapt_institute_hold_detail_row(row: dict) -> InstituteHoldDetailItem:
    return InstituteHoldDetailItem(
        institute_type=str(row.get("持股机构类型", "")).strip() or None,
        institute_code=str(row.get("持股机构代码", "")).strip() or None,
        institute_name=str(row.get("持股机构简称", "")).strip() or None,
        institute_full_name=str(row.get("持股机构全称", "")).strip() or None,
        hold_count=_to_float(row.get("持股数")),
        latest_hold_count=_to_float(row.get("最新持股数")),
        hold_ratio=_to_float(row.get("持股比例")),
        latest_hold_ratio=_to_float(row.get("最新持股比例")),
        float_ratio=_to_float(row.get("占流通股比例")),
        latest_float_ratio=_to_float(row.get("最新占流通股比例")),
        hold_ratio_change=_to_float(row.get("持股比例增幅")),
        float_ratio_change=_to_float(row.get("占流通股比例增幅")),
    )


def build_institute_hold_summary_text(
    summary: list, detail: list, effective_quarter: str,
) -> str:
    parts = []
    if summary:
        increasing = [s for s in summary if s.hold_ratio_change is not None and s.hold_ratio_change > 0]
        parts.append(f"机构持仓汇总 {len(summary)} 只")
        if increasing:
            parts.append(f"增持 {len(increasing)} 只")
    if detail:
        types = set(d.institute_type for d in detail if d.institute_type)
        parts.append(f"持股机构 {len(detail)} 家（{', '.join(types)}）")
    if not parts:
        return f"无机构持仓数据（{effective_quarter}）"
    return f"（{effective_quarter}）" + "；".join(parts)

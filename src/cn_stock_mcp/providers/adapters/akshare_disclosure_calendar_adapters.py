from __future__ import annotations

from cn_stock_mcp.app.models.disclosure_calendar import DisclosureItem


def _clean_str(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s or s == "NaN" or s == "NaT":
        return None
    return s


def adapt_disclosure_row(row: dict) -> DisclosureItem:
    raw_code = str(row.get("股票代码", "")).strip()
    from cn_stock_mcp.infra.time_utils import normalize_symbol
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return DisclosureItem(
        symbol=symbol,
        name=_clean_str(row.get("股票简称")),
        first_schedule=_clean_str(row.get("首次预约")),
        change_1=_clean_str(row.get("初次变更")),
        change_2=_clean_str(row.get("二次变更")),
        change_3=_clean_str(row.get("三次变更")),
        actual_date=_clean_str(row.get("实际披露")),
    )


def build_disclosure_summary(items: list, period: str, market: str) -> str:
    if not items:
        return f"无披露日历数据（{period}）"
    disclosed = [i for i in items if i.actual_date is not None]
    scheduled = [i for i in items if i.first_schedule is not None and i.actual_date is None]
    changed = [i for i in items if i.change_1 is not None]
    parts = [f"{period} 披露日历 {len(items)} 只"]
    if disclosed:
        parts.append(f"已披露 {len(disclosed)}")
    if scheduled:
        parts.append(f"待披露 {len(scheduled)}")
    if changed:
        parts.append(f"变更日期 {len(changed)}")
    return "；".join(parts)

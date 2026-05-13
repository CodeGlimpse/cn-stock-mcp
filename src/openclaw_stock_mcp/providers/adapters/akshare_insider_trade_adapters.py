from __future__ import annotations

from openclaw_stock_mcp.app.models.insider_trade import InsiderChangeItem, InsiderTop10Item


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
    return s if s and s != "NaN" else None


def adapt_top10_row(row: dict) -> InsiderTop10Item:
    return InsiderTop10Item(
        rank=_to_int(row.get("名次")),
        shareholder_name=_clean_str(row.get("股东名称")),
        shareholder_type=_clean_str(row.get("股东性质")),
        share_type=_clean_str(row.get("股份类型")),
        hold_count=_to_float(row.get("持股数")),
        hold_ratio=_to_float(row.get("占总流通股本持股比例")),
        change=_clean_str(row.get("增减")),
        change_ratio=_to_float(row.get("变动比率")),
    )


def adapt_change_row(row: dict) -> InsiderChangeItem:
    return InsiderChangeItem(
        announce_date=_clean_str(row.get("公告日期")),
        shareholder_name=_clean_str(row.get("变动股东")),
        change_count=_clean_str(row.get("变动数量")),
        avg_price=_clean_str(row.get("交易均价")),
        remaining_shares=_clean_str(row.get("剩余股份总数")),
        change_period=_clean_str(row.get("变动期间")),
        change_method=_clean_str(row.get("变动途径")),
    )


def build_insider_summary(top10: list, change: list, symbol: str, quarter: str) -> str:
    parts = [f"{symbol}"]
    if top10:
        increasing = [t for t in top10 if t.change_ratio is not None and t.change_ratio > 0]
        decreasing = [t for t in top10 if t.change_ratio is not None and t.change_ratio < 0]
        unchanged = [t for t in top10 if t.change is not None and "不变" in str(t.change)]
        parts.append(f"十大股东：增持 {len(increasing)} 减持 {len(decreasing)} 不变 {len(unchanged)}")
    if change:
        buy = [c for c in change if c.change_count and "增持" in str(c.change_count)]
        sell = [c for c in change if c.change_count and "减持" in str(c.change_count)]
        parts.append(f"增减持历史：增持 {len(buy)} 次 减持 {len(sell)} 次")
    if not top10 and not change:
        return f"{symbol}（{quarter}）：无高管增减持数据"
    return f"（{quarter}）" + "；".join(parts)

from __future__ import annotations

from cn_stock_mcp.app.models.macro import (
    MacroCalendarItem,
    MacroDataFormat,
    MacroDataPoint,
    MacroEntry,
    MacroOverviewItem,
)


def _to_float(value) -> float | None:
    if value is None or value == "" or value is False:
        return None
    try:
        f = float(value)
        import math
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _compute_surprise(actual: float | None, forecast: float | None) -> str | None:
    if actual is None or forecast is None:
        return None
    if actual > forecast:
        return "beat"
    elif actual < forecast:
        return "miss"
    return "in_line"


# ── Format A: [商品, 日期, 今值, 预测值, 前值] ──────────────────

def normalize_format_a(df, entry: MacroEntry) -> list[MacroDataPoint]:
    rows = df.to_dict("records")
    points: list[MacroDataPoint] = []
    for row in rows:
        date_val = str(row.get("日期", ""))[:10]
        actual = _to_float(row.get("今值"))
        forecast = _to_float(row.get("预测值"))
        previous = _to_float(row.get("前值"))
        points.append(MacroDataPoint(
            date=date_val,
            actual=actual,
            forecast=forecast,
            previous=previous,
            surprise=_compute_surprise(actual, forecast),
        ))
    return points


# ── Format A2: [时间, 发布日期, 现值, 前值] ──────────────────────

def normalize_format_a2(df, entry: MacroEntry) -> list[MacroDataPoint]:
    rows = df.to_dict("records")
    points: list[MacroDataPoint] = []
    for row in rows:
        date_val = str(row.get("发布日期", row.get("时间", "")))[:10]
        actual = _to_float(row.get("现值"))
        previous = _to_float(row.get("前值"))
        points.append(MacroDataPoint(
            date=date_val,
            actual=actual,
            forecast=None,
            previous=previous,
            surprise=None,
        ))
    return points


# ── Format B: NBS wide-table ──────────────────────────────────────

def normalize_format_b(df, entry: MacroEntry) -> list[MacroDataPoint]:
    date_col = entry.b_date_col
    value_col = entry.b_value_col
    if not date_col or not value_col:
        return []

    rows = df.to_dict("records")
    points: list[MacroDataPoint] = []
    for row in rows:
        date_val = str(row.get(date_col, ""))[:10]
        actual = _to_float(row.get(value_col))
        points.append(MacroDataPoint(
            date=date_val,
            actual=actual,
            forecast=None,
            previous=None,
            surprise=None,
        ))
    return points


# ── Format C: Special (LPR etc.) ─────────────────────────────────

def normalize_format_c(df, entry: MacroEntry) -> list[MacroDataPoint]:
    col_map = entry.c_col_map or {}
    date_col = "TRADE_DATE"
    # Pick the first mapped column as the primary value
    value_col = list(col_map.keys())[0] if col_map else None
    if not value_col:
        return []

    rows = df.to_dict("records")
    points: list[MacroDataPoint] = []
    for row in rows:
        date_val = str(row.get(date_col, ""))[:10]
        actual = _to_float(row.get(value_col))
        points.append(MacroDataPoint(
            date=date_val,
            actual=actual,
            forecast=None,
            previous=None,
            surprise=None,
        ))
    return points


# ── Dispatch ──────────────────────────────────────────────────────

FORMAT_NORMALIZERS = {
    MacroDataFormat.A: normalize_format_a,
    MacroDataFormat.A2: normalize_format_a2,
    MacroDataFormat.B: normalize_format_b,
    MacroDataFormat.C: normalize_format_c,
}


def normalize_macro_df(df, entry: MacroEntry) -> list[MacroDataPoint]:
    normalizer = FORMAT_NORMALIZERS.get(entry.format)
    if not normalizer:
        return []
    return normalizer(df, entry)


def build_calendar_items(points: list[MacroDataPoint], indicator: str, indicator_name: str, region: str) -> list[MacroCalendarItem]:
    """Filter for future-dated items (forecast exists but actual is None)."""
    items: list[MacroCalendarItem] = []
    for p in points:
        if p.actual is None and (p.forecast is not None or p.previous is not None):
            items.append(MacroCalendarItem(
                indicator=indicator,
                indicator_name=indicator_name,
                date=p.date,
                forecast=p.forecast,
                previous=p.previous,
                region=region,
            ))
    return items


def build_overview_item(point: MacroDataPoint, indicator: str, entry: MacroEntry, region: str) -> MacroOverviewItem:
    return MacroOverviewItem(
        indicator=indicator,
        indicator_name=entry.name,
        date=point.date,
        actual=point.actual,
        forecast=point.forecast,
        previous=point.previous,
        surprise=point.surprise,
        unit=entry.unit,
        freq=entry.freq,
    )


def build_macro_summary_text(
    indicator_name: str,
    unit: str,
    latest: MacroDataPoint | None,
    history: list[MacroDataPoint],
    overview_items: dict[str, MacroOverviewItem] | None = None,
) -> str:
    parts: list[str] = []

    if overview_items:
        for key, item in overview_items.items():
            val_str = f"{item.actual}{item.unit}" if item.actual is not None else "暂无"
            surprise_str = ""
            if item.surprise == "beat":
                surprise_str = "超预期"
            elif item.surprise == "miss":
                surprise_str = "不及预期"
            parts.append(f"{item.indicator_name}({item.date or ''}): {val_str}{surprise_str}")
        return "；".join(parts)

    if latest is None and not history:
        return f"{indicator_name}数据暂无"

    if latest:
        val_str = f"{latest.actual}{unit}" if latest.actual is not None else "暂无"
        surprise_str = ""
        if latest.surprise == "beat":
            surprise_str = "，超预期"
        elif latest.surprise == "miss":
            surprise_str = "，不及预期"
        parts.append(f"{indicator_name}({latest.date}): {val_str}{surprise_str}")

    if len(history) >= 2:
        recent = [p for p in history if p.actual is not None]
        if len(recent) >= 2:
            last2 = recent[-2:]
            if last2[0].actual and last2[1].actual:
                direction = "↑" if last2[1].actual > last2[0].actual else "↓" if last2[1].actual < last2[0].actual else "→"
                parts.append(f"近两期{direction}")

    return "，".join(parts)

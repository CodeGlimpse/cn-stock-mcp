from __future__ import annotations

from openclaw_stock_mcp.app.models.financial import (
    FinancialDetailItem,
    FinancialHistoryPoint,
    FinancialSnapshot,
)


# Mapping from abstract_new_ths metric_name to FinancialSnapshot field name
_ABSTRACT_METRIC_MAP = {
    "operating_income_total": "operating_revenue",
    "parent_holder_net_profit": "net_profit",
    "index_deduct_holder_net_profit": "deduct_net_profit",
    "calculate_parent_holder_net_profit_yoy_growth_ratio": "net_profit_yoy",
    "deduct_net_profit_yoy_growth_ratio": "deduct_net_profit_yoy",
    "calculate_operating_income_total_yoy_growth_ratio": "revenue_yoy",
    "basic_eps": "basic_eps",
    "calc_per_net_assets": "per_net_assets",
    "per_capital_reserve": "per_capital_reserve",
    "per_undistributed_profits": "per_undistributed_profits",
    "index_per_operating_cash_flow_net": "per_operating_cash_flow",
    "index_weighted_avg_roe": "roe_weighted",
    "index_full_diluted_roe": "roe_diluted",
    "sale_gross_margin": "sale_gross_margin",
    "sale_net_interest_ratio": "sale_net_margin",
    "assets_debt_ratio": "assets_debt_ratio",
    "equity_ratio": "equity_ratio",
    "current_ratio": "current_ratio",
    "quick_ratio": "quick_ratio",
    "conservative_quick_ratio": "conservative_quick_ratio",
    "inventory_turnover_days": "inventory_turnover_days",
    "inventory_turnover_ratio": "inventory_turnover_ratio",
    "receive_accounts_turnover_days": "receive_accounts_turnover_days",
    "business_cycle": "business_cycle",
}


def _to_float(value) -> float | None:
    if value is None or value == "" or value is False:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_financial_snapshot_from_abstract(
    symbol: str,
    abstract_rows: list[dict],
    report_date: str | None = None,
) -> FinancialSnapshot:
    """Build a FinancialSnapshot from abstract_new_ths rows for a specific report date.

    If report_date is None, uses the latest report_date.
    """
    if not abstract_rows:
        return FinancialSnapshot(symbol=symbol)

    # Determine target report_date
    if report_date is None:
        dates = sorted({str(r.get("report_date", ""))[:10] for r in abstract_rows if r.get("report_date")})
        report_date = dates[-1] if dates else None

    # Filter rows for the target report_date
    target_rows = [r for r in abstract_rows if str(r.get("report_date", ""))[:10] == report_date]

    # Get quarter_name from first row
    quarter_name = None
    for r in target_rows:
        qn = r.get("quarter_name")
        if qn:
            quarter_name = str(qn)
            break

    # Build field dict
    fields: dict = {}
    for row in target_rows:
        metric_name = str(row.get("metric_name", ""))
        field_name = _ABSTRACT_METRIC_MAP.get(metric_name)
        if not field_name:
            continue
        # Prefer 'single' (单季度) for income statement items, 'value' for ratio/balance items
        val = _to_float(row.get("value"))
        single_val = _to_float(row.get("single"))
        # For ratios and per-share metrics, value is the annual/cumulative figure; single is single-quarter
        if field_name in ("operating_revenue", "net_profit", "deduct_net_profit", "basic_eps"):
            fields[field_name] = val
        else:
            fields[field_name] = val

    # YoY fields from separate metric_name rows
    for row in target_rows:
        metric_name = str(row.get("metric_name", ""))
        field_name = _ABSTRACT_METRIC_MAP.get(metric_name)
        if not field_name:
            continue
        if field_name.endswith("_yoy"):
            yoy_val = _to_float(row.get("value"))
            if yoy_val is not None:
                fields[field_name] = yoy_val

    return FinancialSnapshot(
        symbol=symbol,
        report_date=report_date,
        quarter_name=quarter_name,
        **fields,
    )


def build_financial_history_from_abstract(
    abstract_rows: list[dict],
    recent_n: int = 8,
) -> list[FinancialHistoryPoint]:
    """Build a list of FinancialHistoryPoint from abstract rows, one per report_date."""
    if not abstract_rows:
        return []

    # Group by report_date
    date_groups: dict[str, list[dict]] = {}
    for row in abstract_rows:
        rd = str(row.get("report_date", ""))[:10]
        if not rd:
            continue
        date_groups.setdefault(rd, []).append(row)

    # Sort dates descending, take recent_n
    sorted_dates = sorted(date_groups.keys(), reverse=True)[:recent_n]

    # History metric map (subset)
    history_metric_map = {
        "operating_income_total": "operating_revenue",
        "parent_holder_net_profit": "net_profit",
        "calculate_parent_holder_net_profit_yoy_growth_ratio": "net_profit_yoy",
        "calculate_operating_income_total_yoy_growth_ratio": "revenue_yoy",
        "basic_eps": "basic_eps",
        "index_weighted_avg_roe": "roe_weighted",
        "sale_net_interest_ratio": "sale_net_margin",
        "assets_debt_ratio": "assets_debt_ratio",
    }

    points: list[FinancialHistoryPoint] = []
    for rd in sorted_dates:
        rows = date_groups[rd]
        quarter_name = None
        for r in rows:
            qn = r.get("quarter_name")
            if qn:
                quarter_name = str(qn)
                break

        fields: dict = {}
        for row in rows:
            metric_name = str(row.get("metric_name", ""))
            field_name = history_metric_map.get(metric_name)
            if not field_name:
                continue
            fields[field_name] = _to_float(row.get("value"))

        points.append(FinancialHistoryPoint(
            report_date=rd,
            quarter_name=quarter_name,
            **fields,
        ))

    return points


def adapt_akshare_financial_detail_row(row: dict) -> FinancialDetailItem:
    """Adapt a single row from debt_new_ths / cash_new_ths / benefit_ths long-format."""
    return FinancialDetailItem(
        report_date=str(row.get("report_date", ""))[:10],
        report_name=str(row.get("report_name", "")),
        quarter_name=str(row.get("quarter_name", "")),
        metric_name=str(row.get("metric_name", "")),
        value=_to_float(row.get("value")),
        single=_to_float(row.get("single")),
        yoy=_to_float(row.get("yoy")),
        mom=_to_float(row.get("mom")),
        single_yoy=_to_float(row.get("single_yoy")),
    )


def build_financial_summary_text(snapshot: FinancialSnapshot | None, symbol: str) -> str:
    """Build a readable Chinese summary from a FinancialSnapshot."""
    if not snapshot or not snapshot.report_date:
        return f"{symbol} 财务数据暂无"

    parts = [f"{snapshot.quarter_name or snapshot.report_date}"]

    if snapshot.operating_revenue is not None:
        rev = snapshot.operating_revenue / 1e8 if abs(snapshot.operating_revenue) > 1e4 else snapshot.operating_revenue
        unit = "亿" if abs(snapshot.operating_revenue) > 1e4 else ""
        parts.append(f"营收{rev:.2f}{unit}")
        if snapshot.revenue_yoy is not None:
            parts.append(f"同比{snapshot.revenue_yoy * 100:.1f}%")

    if snapshot.net_profit is not None:
        np = snapshot.net_profit / 1e8 if abs(snapshot.net_profit) > 1e4 else snapshot.net_profit
        unit = "亿" if abs(snapshot.net_profit) > 1e4 else ""
        parts.append(f"净利{np:.2f}{unit}")
        if snapshot.net_profit_yoy is not None:
            parts.append(f"同比{snapshot.net_profit_yoy * 100:.1f}%")

    if snapshot.roe_weighted is not None:
        parts.append(f"ROE(加权){snapshot.roe_weighted * 100:.2f}%")

    if snapshot.sale_net_margin is not None:
        parts.append(f"净利率{snapshot.sale_net_margin * 100:.2f}%")

    if snapshot.assets_debt_ratio is not None:
        parts.append(f"负债率{snapshot.assets_debt_ratio * 100:.1f}%")

    if snapshot.basic_eps is not None:
        parts.append(f"EPS {snapshot.basic_eps:.2f}")

    return f"{symbol} " + "，".join(parts) if len(parts) > 1 else f"{symbol} 财务数据暂无"

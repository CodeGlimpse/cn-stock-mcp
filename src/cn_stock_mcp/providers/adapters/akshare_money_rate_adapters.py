from __future__ import annotations

from cn_stock_mcp.app.models.money_rate import (
    InterbankRateItem,
    RepoRateItem,
    ShiborItem,
)


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def adapt_shibor_row(row: dict) -> ShiborItem:
    return ShiborItem(
        date=str(row.get("日期", "")).strip(),
        overnight=_to_float(row.get("O/N-定价")),
        overnight_change=_to_float(row.get("O/N-涨跌幅")),
        week_1=_to_float(row.get("1W-定价")),
        week_1_change=_to_float(row.get("1W-涨跌幅")),
        week_2=_to_float(row.get("2W-定价")),
        week_2_change=_to_float(row.get("2W-涨跌幅")),
        month_1=_to_float(row.get("1M-定价")),
        month_1_change=_to_float(row.get("1M-涨跌幅")),
        month_3=_to_float(row.get("3M-定价")),
        month_3_change=_to_float(row.get("3M-涨跌幅")),
        month_6=_to_float(row.get("6M-定价")),
        month_6_change=_to_float(row.get("6M-涨跌幅")),
        month_9=_to_float(row.get("9M-定价")),
        month_9_change=_to_float(row.get("9M-涨跌幅")),
        year_1=_to_float(row.get("1Y-定价")),
        year_1_change=_to_float(row.get("1Y-涨跌幅")),
    )


def adapt_interbank_row(row: dict) -> InterbankRateItem:
    return InterbankRateItem(
        date=str(row.get("报告日", "")).strip(),
        rate=_to_float(row.get("利率")),
        change=_to_float(row.get("涨跌")),
    )


def adapt_repo_row(row: dict) -> RepoRateItem:
    return RepoRateItem(
        date=str(row.get("date", "")).strip(),
        FR001=_to_float(row.get("FR001")),
        FR007=_to_float(row.get("FR007")),
        FR014=_to_float(row.get("FR014")),
        FDR001=_to_float(row.get("FDR001")),
        FDR007=_to_float(row.get("FDR007")),
        FDR014=_to_float(row.get("FDR014")),
    )


def build_money_rate_summary_text(
    shibor: list, interbank: list, repo: list,
) -> str:
    parts = []
    if shibor:
        latest = shibor[-1] if shibor else None
        if latest and latest.overnight is not None:
            parts.append(f"SHIBOR O/N {latest.overnight}%")
        parts.append(f"SHIBOR曲线 {len(shibor)} 日")
    if interbank:
        latest = interbank[-1] if interbank else None
        if latest and latest.rate is not None:
            parts.append(f"拆借利率 {latest.rate}%")
    if repo:
        latest = repo[-1] if repo else None
        if latest and latest.FR007 is not None:
            parts.append(f"FR007 {latest.FR007}%")
        parts.append(f"回购利率 {len(repo)} 日")
    if not parts:
        return "无货币市场利率数据"
    return "；".join(parts)

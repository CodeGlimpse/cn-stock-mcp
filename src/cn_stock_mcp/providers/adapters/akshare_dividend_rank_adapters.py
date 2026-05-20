from __future__ import annotations

from cn_stock_mcp.app.models.dividend_rank import (
    DividendDetailItem,
    DividendPlanItem,
    DividendRankItem,
)
from cn_stock_mcp.infra.time_utils import normalize_symbol


def _to_float(value):
    if value is None or value == "" or value == "-" or value == "NaN":
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


def adapt_dividend_rank_row(row: dict) -> DividendRankItem:
    raw_code = str(row.get("代码", "")).strip()
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return DividendRankItem(
        symbol=symbol,
        name=_clean_str(row.get("名称")),
        list_date=_clean_str(row.get("上市日期")),
        total_dividend=_to_float(row.get("累计股息")),
        avg_annual_dividend=_to_float(row.get("年均股息")),
        dividend_count=_to_int(row.get("分红次数")),
        total_financing=_to_float(row.get("融资总额")),
        financing_count=_to_int(row.get("融资次数")),
    )


def adapt_dividend_plan_row(row: dict) -> DividendPlanItem:
    raw_code = str(row.get("代码", "")).strip()
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return DividendPlanItem(
        symbol=symbol,
        name=_clean_str(row.get("名称")),
        bonus_share_ratio=_to_float(row.get("送转股份-送转比例")),
        conversion_ratio=_to_float(row.get("送转股份-转股比例")),
        cash_dividend_ratio=_to_float(row.get("现金分红-现金分红比例")),
        dividend_yield=_to_float(row.get("现金分红-股息率")),
        eps=_to_float(row.get("每股收益")),
        bvps=_to_float(row.get("每股净资产")),
        reserve_per_share=_to_float(row.get("每股公积金")),
        undistributed_per_share=_to_float(row.get("每股未分配利润")),
        net_profit_yoy=_to_float(row.get("净利润同比增长")),
        total_shares=_to_float(row.get("总股本")),
        announce_date=_clean_str(row.get("预案公告日")),
        record_date=_clean_str(row.get("股权登记日")),
        ex_date=_clean_str(row.get("除权除息日")),
        progress=_clean_str(row.get("方案进度")),
    )


def adapt_dividend_detail_row(row: dict) -> DividendDetailItem:
    return DividendDetailItem(
        announce_date=_clean_str(row.get("公告日期")),
        bonus_share=_to_float(row.get("送股")),
        conversion=_to_float(row.get("转增")),
        cash_dividend=_to_float(row.get("派息")),
        progress=_clean_str(row.get("进度")),
        ex_date=_clean_str(row.get("除权除息日")),
        record_date=_clean_str(row.get("股权登记日")),
    )


def build_dividend_summary(rank: list, plan: list, detail: list) -> str:
    parts = []
    if rank:
        high_yield = [r for r in rank if r.avg_annual_dividend is not None and r.avg_annual_dividend >= 3]
        parts.append(f"历史分红排名 {len(rank)} 只（年均≥3%: {len(high_yield)} 只）")
    if plan:
        implemented = [p for p in plan if p.progress and "实施" in str(p.progress)]
        parts.append(f"分红方案 {len(plan)} 条（已实施 {len(implemented)}）")
    if detail:
        paid = [d for d in detail if d.cash_dividend is not None and d.cash_dividend > 0]
        parts.append(f"分红明细 {len(detail)} 条（含派息 {len(paid)} 次）")
    if not parts:
        return "无分红数据"
    return "；".join(parts)

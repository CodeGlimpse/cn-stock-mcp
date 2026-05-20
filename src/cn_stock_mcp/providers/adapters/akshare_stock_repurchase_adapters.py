from __future__ import annotations

from cn_stock_mcp.app.models.stock_repurchase import RepurchaseItem
from cn_stock_mcp.infra.time_utils import normalize_symbol


def _to_float(value):
    if value is None or value == "" or value == "NaN":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s and s != "NaN" and s != "NaT" else None


def adapt_repurchase_row(row: dict) -> RepurchaseItem:
    raw_code = str(row.get("股票代码", "")).strip()
    symbol = normalize_symbol(raw_code) if raw_code else ""
    return RepurchaseItem(
        symbol=symbol,
        name=_clean_str(row.get("股票简称")),
        latest_price=_to_float(row.get("最新价")),
        plan_price_range=_clean_str(row.get("计划回购价格区间")),
        plan_qty_min=_to_float(row.get("计划回购数量区间-下限")),
        plan_qty_max=_to_float(row.get("计划回购数量区间-上限")),
        plan_ratio_min=_to_float(row.get("占公告前一日总股本比例-下限")),
        plan_ratio_max=_to_float(row.get("占公告前一日总股本比例-上限")),
        plan_amount_min=_to_float(row.get("计划回购金额区间-下限")),
        plan_amount_max=_to_float(row.get("计划回购金额区间-上限")),
        start_date=_clean_str(row.get("回购起始时间")),
        progress=_clean_str(row.get("实施进度")),
        done_price_min=_to_float(row.get("已回购股份价格区间-下限")),
        done_price_max=_to_float(row.get("已回购股份价格区间-上限")),
        done_qty=_to_float(row.get("已回购股份数量")),
        done_amount=_to_float(row.get("已回购金额")),
        latest_announce_date=_clean_str(row.get("最新公告日期")),
    )


def build_repurchase_summary(items: list, status: str) -> str:
    if not items:
        return "无回购数据"
    parts = [f"回购明细 {len(items)} 条"]
    if status != "all":
        parts.append(f"筛选: {status}")
    by_progress = {}
    for i in items:
        p = i.progress or "未知"
        by_progress[p] = by_progress.get(p, 0) + 1
    progress_str = "、".join(f"{k} {v}条" for k, v in sorted(by_progress.items(), key=lambda x: -x[1]))
    parts.append(progress_str)
    total_amount = sum(i.done_amount or 0 for i in items)
    if total_amount > 0:
        parts.append(f"已回购总额 {total_amount/1e8:.2f} 亿")
    return "；".join(parts)

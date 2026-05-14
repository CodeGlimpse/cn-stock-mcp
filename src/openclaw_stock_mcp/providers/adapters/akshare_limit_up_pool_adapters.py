from __future__ import annotations

from openclaw_stock_mcp.app.models.limit_up_pool import (
    BrokenItem,
    LimitDownItem,
    LimitUpItem,
    PreviousItem,
    StrongItem,
    SubNewItem,
)


def _to_float(value):
    if value is None or value == "" or value == "NaN" or value == "-" or value == "--":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    if value is None or value == "" or value == "NaN" or value == "-" or value == "--":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clean_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s and s != "NaN" and s != "NaT" and s != "--" and s != "-" else None


def adapt_limit_up_row(row: dict) -> LimitUpItem:
    return LimitUpItem(
        code=_clean_str(row.get("代码")),
        name=_clean_str(row.get("名称")),
        change_pct=_to_float(row.get("涨跌幅")),
        latest_price=_to_float(row.get("最新价")),
        turnover=_to_float(row.get("成交额")),
        float_market_cap=_to_float(row.get("流通市值")),
        total_market_cap=_to_float(row.get("总市值")),
        turnover_rate=_to_float(row.get("换手率")),
        seal_amount=_to_float(row.get("封板资金")),
        first_seal_time=_clean_str(row.get("首次封板时间")),
        last_seal_time=_clean_str(row.get("最后封板时间")),
        broken_count=_to_int(row.get("炸板次数")),
        limit_stat=_clean_str(row.get("涨停统计")),
        consecutive_limit=_to_int(row.get("连板数")),
        industry=_clean_str(row.get("所属行业")),
    )


def adapt_limit_down_row(row: dict) -> LimitDownItem:
    return LimitDownItem(
        code=_clean_str(row.get("代码")),
        name=_clean_str(row.get("名称")),
        change_pct=_to_float(row.get("涨跌幅")),
        latest_price=_to_float(row.get("最新价")),
        turnover=_to_float(row.get("成交额")),
        float_market_cap=_to_float(row.get("流通市值")),
        total_market_cap=_to_float(row.get("总市值")),
        pe_dynamic=_to_float(row.get("动态市盈率")),
        turnover_rate=_to_float(row.get("换手率")),
        seal_amount=_to_float(row.get("封单资金")),
        last_seal_time=_clean_str(row.get("最后封板时间")),
        board_turnover=_to_float(row.get("板上成交额")),
        consecutive_limit=_to_int(row.get("连续跌停")),
        open_count=_to_int(row.get("开板次数")),
        industry=_clean_str(row.get("所属行业")),
    )


def adapt_strong_row(row: dict) -> StrongItem:
    return StrongItem(
        code=_clean_str(row.get("代码")),
        name=_clean_str(row.get("名称")),
        change_pct=_to_float(row.get("涨跌幅")),
        latest_price=_to_float(row.get("最新价")),
        limit_price=_to_float(row.get("涨停价")),
        turnover=_to_float(row.get("成交额")),
        float_market_cap=_to_float(row.get("流通市值")),
        total_market_cap=_to_float(row.get("总市值")),
        turnover_rate=_to_float(row.get("换手率")),
        speed=_to_float(row.get("涨速")),
        is_new_high=_clean_str(row.get("是否新高")),
        volume_ratio=_to_float(row.get("量比")),
        limit_stat=_clean_str(row.get("涨停统计")),
        reason=_clean_str(row.get("入选理由")),
        industry=_clean_str(row.get("所属行业")),
    )


def adapt_previous_row(row: dict) -> PreviousItem:
    return PreviousItem(
        code=_clean_str(row.get("代码")),
        name=_clean_str(row.get("名称")),
        change_pct=_to_float(row.get("涨跌幅")),
        latest_price=_to_float(row.get("最新价")),
        limit_price=_to_float(row.get("涨停价")),
        turnover=_to_float(row.get("成交额")),
        float_market_cap=_to_float(row.get("流通市值")),
        total_market_cap=_to_float(row.get("总市值")),
        turnover_rate=_to_float(row.get("换手率")),
        speed=_to_float(row.get("涨速")),
        amplitude=_to_float(row.get("振幅")),
        yesterday_seal_time=_clean_str(row.get("昨日封板时间")),
        yesterday_consecutive=_to_int(row.get("昨日连板数")),
        limit_stat=_clean_str(row.get("涨停统计")),
        industry=_clean_str(row.get("所属行业")),
    )


def adapt_sub_new_row(row: dict) -> SubNewItem:
    return SubNewItem(
        code=_clean_str(row.get("代码")),
        name=_clean_str(row.get("名称")),
        change_pct=_to_float(row.get("涨跌幅")),
        latest_price=_to_float(row.get("最新价")),
        limit_price=_to_float(row.get("涨停价")),
        turnover=_to_float(row.get("成交额")),
        float_market_cap=_to_float(row.get("流通市值")),
        total_market_cap=_to_float(row.get("总市值")),
        turnover_rate=_to_float(row.get("转手率", row.get("换手率"))),
        open_days=_to_int(row.get("开板几日")),
        open_date=_clean_str(row.get("开板日期")),
        list_date=_clean_str(row.get("上市日期")),
        is_new_high=_clean_str(row.get("是否新高")),
        limit_stat=_clean_str(row.get("涨停统计")),
        industry=_clean_str(row.get("所属行业")),
    )


def adapt_broken_row(row: dict) -> BrokenItem:
    return BrokenItem(
        code=_clean_str(row.get("代码")),
        name=_clean_str(row.get("名称")),
        change_pct=_to_float(row.get("涨跌幅")),
        latest_price=_to_float(row.get("最新价")),
        limit_price=_to_float(row.get("涨停价")),
        turnover=_to_float(row.get("成交额")),
        float_market_cap=_to_float(row.get("流通市值")),
        total_market_cap=_to_float(row.get("总市值")),
        turnover_rate=_to_float(row.get("换手率")),
        speed=_to_float(row.get("涨速")),
        first_seal_time=_clean_str(row.get("首次封板时间")),
        broken_count=_to_int(row.get("炸板次数")),
        limit_stat=_clean_str(row.get("涨停统计")),
        amplitude=_to_float(row.get("振幅")),
        industry=_clean_str(row.get("所属行业")),
    )


def build_limit_up_summary(lu, ld, strong, prev, sub, broken) -> str:
    parts = []
    if lu:
        multi = [i for i in lu if i.consecutive_limit and i.consecutive_limit >= 2]
        parts.append(f"涨停 {len(lu)} 只(连板 {len(multi)})")
    if ld:
        parts.append(f"跌停 {len(ld)} 只")
    if strong:
        parts.append(f"强势 {len(strong)} 只")
    if prev:
        still_up = [i for i in prev if i.change_pct and i.change_pct > 0]
        parts.append(f"昨涨停 {len(prev)} 只(续涨 {len(still_up)})")
    if sub:
        parts.append(f"次新 {len(sub)} 只")
    if broken:
        parts.append(f"炸板 {len(broken)} 只")
    if not parts:
        return "无涨跌停数据"
    return "；".join(parts)

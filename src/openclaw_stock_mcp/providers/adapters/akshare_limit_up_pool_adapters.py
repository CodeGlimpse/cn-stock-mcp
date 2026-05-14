from __future__ import annotations

from collections import defaultdict

from openclaw_stock_mcp.app.models.limit_up_pool import (
    BrokenItem,
    LimitDownItem,
    LimitUpItem,
    LimitUpPoolIndustrySentimentItem,
    LimitUpPoolSentiment,
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


def _industry_key(value: str | None) -> str:
    return value.strip() if value and value.strip() else "unknown"


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


def build_limit_up_sentiment(trade_date: str | None, lu, ld, strong, prev, sub, broken) -> LimitUpPoolSentiment:
    multi_limit_total = sum(1 for i in lu if i.consecutive_limit is not None and i.consecutive_limit >= 2)
    highest_consecutive_limit = max((i.consecutive_limit or 0 for i in lu), default=0) or None
    previous_up_count = sum(1 for i in prev if i.change_pct is not None and i.change_pct > 0)
    previous_up_ratio = (previous_up_count / len(prev)) if prev else None
    broken_denominator = len(lu) + len(broken)
    broken_rate = (len(broken) / broken_denominator) if broken_denominator > 0 else None

    seal_amounts_up = [float(i.seal_amount) for i in lu if i.seal_amount is not None]
    seal_amounts_down = [float(i.seal_amount) for i in ld if i.seal_amount is not None]
    turnover_rates_up = [float(i.turnover_rate) for i in lu if i.turnover_rate is not None]

    ladder_counts: dict[str, int] = {"1": 0, "2": 0, "3": 0, "4": 0, "5+": 0}
    for i in lu:
        level = i.consecutive_limit or 1
        if level >= 5:
            ladder_counts["5+"] += 1
        elif level >= 1:
            ladder_counts[str(level)] += 1
    ladder = {k: v for k, v in ladder_counts.items() if v > 0}

    return LimitUpPoolSentiment(
        trade_date=trade_date,
        limit_up_total=len(lu),
        limit_down_total=len(ld),
        strong_total=len(strong),
        previous_total=len(prev),
        sub_new_total=len(sub),
        broken_total=len(broken),
        multi_limit_total=multi_limit_total,
        highest_consecutive_limit=highest_consecutive_limit,
        previous_up_count=previous_up_count,
        previous_up_ratio=previous_up_ratio,
        broken_rate=broken_rate,
        limit_up_seal_amount_sum=sum(seal_amounts_up) if seal_amounts_up else None,
        limit_down_seal_amount_sum=sum(seal_amounts_down) if seal_amounts_down else None,
        avg_limit_up_turnover_rate=(sum(turnover_rates_up) / len(turnover_rates_up)) if turnover_rates_up else None,
        ladder=ladder,
    )


def build_limit_up_industry_sentiment(lu, ld, strong, prev, sub, broken) -> list[LimitUpPoolIndustrySentimentItem]:
    grouped: dict[str, dict] = defaultdict(lambda: {
        "codes": set(),
        "limit_up_count": 0,
        "multi_limit_count": 0,
        "highest_consecutive_limit": 0,
        "strong_count": 0,
        "previous_count": 0,
        "previous_up_count": 0,
        "sub_new_count": 0,
        "broken_count": 0,
        "limit_down_count": 0,
        "limit_up_seal_amount_sum": 0.0,
        "limit_down_seal_amount_sum": 0.0,
        "has_limit_up_seal": False,
        "has_limit_down_seal": False,
    })

    for item in lu:
        key = _industry_key(item.industry)
        row = grouped[key]
        if item.code:
            row["codes"].add(item.code)
        row["limit_up_count"] += 1
        if item.consecutive_limit is not None and item.consecutive_limit >= 2:
            row["multi_limit_count"] += 1
        row["highest_consecutive_limit"] = max(row["highest_consecutive_limit"], item.consecutive_limit or 0)
        if item.seal_amount is not None:
            row["limit_up_seal_amount_sum"] += float(item.seal_amount)
            row["has_limit_up_seal"] = True

    for item in ld:
        key = _industry_key(item.industry)
        row = grouped[key]
        if item.code:
            row["codes"].add(item.code)
        row["limit_down_count"] += 1
        if item.seal_amount is not None:
            row["limit_down_seal_amount_sum"] += float(item.seal_amount)
            row["has_limit_down_seal"] = True

    for item in strong:
        key = _industry_key(item.industry)
        row = grouped[key]
        if item.code:
            row["codes"].add(item.code)
        row["strong_count"] += 1

    for item in prev:
        key = _industry_key(item.industry)
        row = grouped[key]
        if item.code:
            row["codes"].add(item.code)
        row["previous_count"] += 1
        if item.change_pct is not None and item.change_pct > 0:
            row["previous_up_count"] += 1

    for item in sub:
        key = _industry_key(item.industry)
        row = grouped[key]
        if item.code:
            row["codes"].add(item.code)
        row["sub_new_count"] += 1

    for item in broken:
        key = _industry_key(item.industry)
        row = grouped[key]
        if item.code:
            row["codes"].add(item.code)
        row["broken_count"] += 1

    result: list[LimitUpPoolIndustrySentimentItem] = []
    for industry, row in grouped.items():
        result.append(LimitUpPoolIndustrySentimentItem(
            industry=industry,
            distinct_code_count=len(row["codes"]),
            limit_up_count=row["limit_up_count"],
            multi_limit_count=row["multi_limit_count"],
            highest_consecutive_limit=row["highest_consecutive_limit"] or None,
            strong_count=row["strong_count"],
            previous_count=row["previous_count"],
            previous_up_count=row["previous_up_count"],
            sub_new_count=row["sub_new_count"],
            broken_count=row["broken_count"],
            limit_down_count=row["limit_down_count"],
            limit_up_seal_amount_sum=row["limit_up_seal_amount_sum"] if row["has_limit_up_seal"] else None,
            limit_down_seal_amount_sum=row["limit_down_seal_amount_sum"] if row["has_limit_down_seal"] else None,
        ))

    result.sort(
        key=lambda x: (
            x.limit_up_count,
            x.strong_count,
            -x.limit_down_count,
            x.broken_count,
            x.previous_up_count,
        ),
        reverse=True,
    )
    return result


def build_limit_up_summary(lu, ld, strong, prev, sub, broken, sentiment: LimitUpPoolSentiment | None = None) -> str:
    parts = []
    if lu:
        multi = sentiment.multi_limit_total if sentiment is not None else len([i for i in lu if i.consecutive_limit and i.consecutive_limit >= 2])
        parts.append(f"涨停 {len(lu)} 只(连板 {multi})")
    if ld:
        parts.append(f"跌停 {len(ld)} 只")
    if strong:
        parts.append(f"强势 {len(strong)} 只")
    if prev:
        still_up = sentiment.previous_up_count if sentiment is not None else len([i for i in prev if i.change_pct and i.change_pct > 0])
        parts.append(f"昨涨停 {len(prev)} 只(续涨 {still_up})")
    if sub:
        parts.append(f"次新 {len(sub)} 只")
    if broken:
        parts.append(f"炸板 {len(broken)} 只")
    if not parts:
        return "无涨跌停数据"
    return "；".join(parts)

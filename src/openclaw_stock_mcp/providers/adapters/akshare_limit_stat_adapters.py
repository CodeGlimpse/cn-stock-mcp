from __future__ import annotations

from collections import Counter

from openclaw_stock_mcp.app.models.limit_stat import (
    BrokenLimitItem,
    LimitStatSummary,
    LimitUpItem,
    PreviousDayLimitItem,
)


def _to_float(value) -> float | None:
    if value is None or value == "" or value is False:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value) -> int | None:
    if value is None or value == "" or value is False:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _format_symbol(code: str) -> str:
    """Convert 6-digit code to normalized symbol."""
    code = str(code).strip()
    if len(code) != 6:
        return code
    if code.startswith(("6",)):
        return f"{code}.SH"
    return f"{code}.SZ"


# ---- Adapters for stock_zt_pool_em (涨停池) ----

def adapt_em_limit_up_item(row: dict) -> LimitUpItem:
    """Adapt a row from ak.stock_zt_pool_em() to LimitUpItem."""
    code = str(row.get("代码", ""))
    return LimitUpItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        price=_to_float(row.get("最新价")),
        change_percent=_to_float(row.get("涨跌幅")),
        turnover=_to_float(row.get("成交额")),
        turnover_rate=_to_float(row.get("换手率")),
        market_cap=_to_float(row.get("总市值")),
        float_market_cap=_to_float(row.get("流通市值")),
        limit_fund=_to_float(row.get("封板资金")),
        first_limit_time=str(row.get("首次封板时间", "")) or None,
        last_limit_time=str(row.get("最后封板时间", "")) or None,
        board_burst_count=_to_int(row.get("炸板次数")),
        consecutive_boards=_to_int(row.get("连板数")),
        limit_stat=str(row.get("涨停统计", "")) or None,
        sector=str(row.get("所属行业", "")) or None,
    )


# ---- Adapter for stock_zt_pool_zbgc_em (炸板池) ----

def adapt_em_broken_limit_item(row: dict) -> BrokenLimitItem:
    """Adapt a row from ak.stock_zt_pool_zbgc_em() to BrokenLimitItem."""
    code = str(row.get("代码", ""))
    return BrokenLimitItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        price=_to_float(row.get("最新价")),
        change_percent=_to_float(row.get("涨跌幅")),
        limit_price=_to_float(row.get("涨停价")),
        turnover=_to_float(row.get("成交额")),
        turnover_rate=_to_float(row.get("换手率")),
        amplitude=_to_float(row.get("振幅")),
        first_limit_time=str(row.get("首次封板时间", "")) or None,
        board_burst_count=_to_int(row.get("炸板次数")),
        limit_stat=str(row.get("涨停统计", "")) or None,
        sector=str(row.get("所属行业", "")) or None,
    )


# ---- Adapter for stock_zt_pool_previous_em (昨日涨停) ----

def adapt_em_previous_limit_item(row: dict) -> PreviousDayLimitItem:
    """Adapt a row from ak.stock_zt_pool_previous_em() to PreviousDayLimitItem."""
    code = str(row.get("代码", ""))
    return PreviousDayLimitItem(
        symbol=_format_symbol(code),
        name=str(row.get("名称", "")),
        price=_to_float(row.get("最新价")),
        change_percent=_to_float(row.get("涨跌幅")),
        limit_price=_to_float(row.get("涨停价")),
        turnover=_to_float(row.get("成交额")),
        turnover_rate=_to_float(row.get("换手率")),
        speed=_to_float(row.get("涨速")),
        amplitude=_to_float(row.get("振幅")),
        yesterday_limit_time=str(row.get("昨日封板时间", "")) or None,
        yesterday_consecutive_boards=_to_int(row.get("昨日连板数")),
        limit_stat=str(row.get("涨停统计", "")) or None,
        sector=str(row.get("所属行业", "")) or None,
    )


# ---- Aggregation: build LimitStatSummary ----

def build_limit_stat_summary(
    trade_date: str,
    limit_up_items: list[LimitUpItem],
    broken_limit_items: list[BrokenLimitItem],
    previous_limit_items: list[PreviousDayLimitItem],
    limit_down_count: int = 0,
) -> LimitStatSummary:
    """Build aggregated limit statistics from raw pool items."""
    limit_up_count = len(limit_up_items)
    broken_count = len(broken_limit_items)

    # Seal rate
    total_attempted = limit_up_count + broken_count
    seal_rate = (limit_up_count / total_attempted * 100) if total_attempted > 0 else None

    # Consecutive boards distribution
    board_counts: Counter[int] = Counter()
    for item in limit_up_items:
        cb = item.consecutive_boards or 1
        board_counts[cb] += 1
    board_distribution = dict(board_counts)

    # Average and max consecutive boards
    all_boards = [item.consecutive_boards or 1 for item in limit_up_items]
    avg_boards = (sum(all_boards) / len(all_boards)) if all_boards else None
    max_boards = max(all_boards) if all_boards else 0

    # Yesterday continue rate
    yesterday_count = len(previous_limit_items)
    yesterday_continue = sum(
        1 for item in previous_limit_items
        if item.change_percent is not None and item.change_percent >= 9.5
    )
    yesterday_continue_rate = (yesterday_continue / yesterday_count * 100) if yesterday_count > 0 else None

    # By sector
    limit_up_by_sector: Counter[str] = Counter()
    for item in limit_up_items:
        if item.sector:
            limit_up_by_sector[item.sector] += 1

    broken_by_sector: Counter[str] = Counter()
    for item in broken_limit_items:
        if item.sector:
            broken_by_sector[item.sector] += 1

    return LimitStatSummary(
        trade_date=trade_date,
        limit_up_count=limit_up_count,
        broken_limit_count=broken_count,
        limit_down_count=limit_down_count,
        seal_rate=seal_rate,
        avg_consecutive_boards=avg_boards,
        max_consecutive_boards=max_boards,
        board_distribution=board_distribution,
        yesterday_limit_count=yesterday_count,
        yesterday_continue_limit_count=yesterday_continue,
        yesterday_continue_rate=yesterday_continue_rate,
        limit_up_by_sector=dict(limit_up_by_sector),
        broken_limit_by_sector=dict(broken_by_sector),
    )


def build_limit_stat_summary_text(summary: LimitStatSummary) -> str:
    """Build a readable Chinese summary."""
    if summary.limit_up_count == 0 and summary.broken_limit_count == 0:
        return f"{summary.trade_date} 无涨停数据"

    parts = [f"{summary.trade_date}"]

    # Core stats
    parts.append(f"涨停{summary.limit_up_count}只")
    if summary.broken_limit_count > 0:
        parts.append(f"炸板{summary.broken_limit_count}只")
    if summary.seal_rate is not None:
        parts.append(f"封板率{summary.seal_rate:.1f}%")
    if summary.limit_down_count > 0:
        parts.append(f"跌停{summary.limit_down_count}只")

    # Consecutive boards
    if summary.max_consecutive_boards > 1:
        parts.append(f"最高{summary.max_consecutive_boards}连板")
    if summary.avg_consecutive_boards is not None and summary.avg_consecutive_boards > 1:
        parts.append(f"均板{summary.avg_consecutive_boards:.1f}")

    # Board distribution
    dist_parts = []
    for boards in sorted(summary.board_distribution.keys(), reverse=True):
        if boards >= 2:
            count = summary.board_distribution[boards]
            dist_parts.append(f"{boards}板×{count}")
    if dist_parts:
        parts.append("连板分布:" + "，".join(dist_parts))

    # Yesterday continue
    if summary.yesterday_limit_count > 0 and summary.yesterday_continue_rate is not None:
        parts.append(f"昨涨停今继续{summary.yesterday_continue_rate:.0f}%({summary.yesterday_continue_limit_count}/{summary.yesterday_limit_count})")

    # Hot sectors
    hot_sectors = sorted(summary.limit_up_by_sector.items(), key=lambda x: x[1], reverse=True)[:3]
    if hot_sectors:
        sector_str = "，".join(f"{s}({c})" for s, c in hot_sectors)
        parts.append(f"行业涨停:{sector_str}")

    return "，".join(parts)

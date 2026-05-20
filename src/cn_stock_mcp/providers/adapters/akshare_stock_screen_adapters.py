from __future__ import annotations

from cn_stock_mcp.app.models.stock_screen import StockScreenItem
from cn_stock_mcp.infra.time_utils import normalize_symbol


def _to_float(value):
    if value is None or value == "" or value == "-":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def adapt_screen_row(row: dict) -> StockScreenItem:
    raw_code = str(row.get("代码", "")).strip()
    # Sina codes: sh600519, sz000001, bj920000
    symbol = normalize_symbol(raw_code) if raw_code else ""
    latest = _to_float(row.get("最新价"))
    prev_close = _to_float(row.get("昨收"))
    high = _to_float(row.get("最高"))
    low = _to_float(row.get("最低"))
    amplitude = None
    if prev_close and prev_close > 0 and high is not None and low is not None:
        amplitude = round((high - low) / prev_close * 100, 2)

    return StockScreenItem(
        symbol=symbol,
        name=str(row.get("名称", "")).strip(),
        latest_price=latest,
        change_pct=_to_float(row.get("涨跌幅")),
        change_amt=_to_float(row.get("涨跌额")),
        open=_to_float(row.get("今开")),
        high=high,
        low=low,
        prev_close=prev_close,
        volume=_to_float(row.get("成交量")),
        turnover=_to_float(row.get("成交额")),
        amplitude=amplitude,
    )


def build_screen_summary(total_before: int, total_after: int, items: list[StockScreenItem], filter_desc: str) -> str:
    if not items:
        return f"筛选完成：{total_before} 只中无匹配（{filter_desc}）"
    avg_change = None
    changes = [i.change_pct for i in items if i.change_pct is not None]
    if changes:
        avg_change = sum(changes) / len(changes)
    avg_str = f"{avg_change:.2f}%" if avg_change is not None else "未知"
    positive = sum(1 for c in changes if c > 0)
    return f"筛选完成：{total_before} 只 → {total_after} 只（{filter_desc}）；平均涨跌幅 {avg_str}，上涨 {positive}/{len(changes)}"


def build_filter_desc(market: str, min_price, max_price, min_change_pct, max_change_pct, min_volume, min_turnover, min_amplitude, sort_by, top_n) -> str:
    parts = [f"市场={market}"]
    if min_price is not None:
        parts.append(f"价格≥{min_price}")
    if max_price is not None:
        parts.append(f"价格≤{max_price}")
    if min_change_pct is not None:
        parts.append(f"涨跌幅≥{min_change_pct}%")
    if max_change_pct is not None:
        parts.append(f"涨跌幅≤{max_change_pct}%")
    if min_volume is not None:
        parts.append(f"成交量≥{min_volume}")
    if min_turnover is not None:
        parts.append(f"成交额≥{min_turnover}")
    if min_amplitude is not None:
        parts.append(f"振幅≥{min_amplitude}%")
    parts.append(f"排序={sort_by}")
    if top_n:
        parts.append(f"前{top_n}只")
    return "；".join(parts)

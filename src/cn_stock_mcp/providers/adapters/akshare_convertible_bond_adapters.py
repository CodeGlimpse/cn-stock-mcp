from __future__ import annotations

from cn_stock_mcp.app.models.convertible_bond import (
    CBIndexPoint,
    CBRedeemItem,
    CBSpotItem,
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


def _to_int(value) -> int | None:
    if value is None or value == "" or value is False:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _format_cb_symbol(code: str) -> str:
    """Format convertible bond code: 12xxxx → .SZ, 11xxxx → .SH."""
    code = str(code).strip()
    if len(code) != 6:
        return code
    if code.startswith("12") or code.startswith("11"):
        # 可转债代码：上交所11开头，深交所12开头
        if code.startswith("11"):
            return f"{code}.SH"
        return f"{code}.SZ"
    # 其他（如退市代码4开头）
    return code


def _format_stock_symbol(code: str) -> str:
    code = str(code).strip()
    if len(code) != 6:
        return code
    if code.startswith("6") or code.startswith("5"):
        return f"{code}.SH"
    return f"{code}.SZ"


def adapt_cb_spot_row(row: dict) -> CBSpotItem:
    """Adapt a row from ak.bond_cb_jsl()."""
    code = str(row.get("代码", ""))
    stock_code = str(row.get("正股代码", ""))
    return CBSpotItem(
        symbol=_format_cb_symbol(code),
        name=str(row.get("转债名称", "")),
        price=_to_float(row.get("现价")),
        change_percent=_to_float(row.get("涨跌幅")),
        stock_symbol=_format_stock_symbol(stock_code) if stock_code and len(stock_code) == 6 else stock_code or None,
        stock_name=str(row.get("正股名称", "")) or None,
        stock_price=_to_float(row.get("正股价")),
        stock_change=_to_float(row.get("正股涨跌")),
        stock_pb=_to_float(row.get("正股PB")),
        conv_price=_to_float(row.get("转股价")),
        conv_value=_to_float(row.get("转股价值")),
        conv_premium=_to_float(row.get("转股溢价率")),
        rating=str(row.get("债券评级", "")) or None,
        put_trigger_price=_to_float(row.get("回售触发价")),
        call_trigger_price=_to_float(row.get("强赎触发价")),
        cb_ratio=_to_float(row.get("转债占比")),
        maturity_date=str(row.get("到期时间", ""))[:10] or None,
        remaining_years=_to_float(row.get("剩余年限")),
        remaining_size=_to_float(row.get("剩余规模")),
        turnover=_to_float(row.get("成交额")),
        turnover_rate=_to_float(row.get("换手率")),
        ytm=_to_float(row.get("到期税前收益")),
        double_low=_to_float(row.get("双低")),
    )


def adapt_cb_redeem_row(row: dict) -> CBRedeemItem:
    """Adapt a row from ak.bond_cb_redeem_jsl()."""
    code = str(row.get("代码", ""))
    stock_code = str(row.get("正股代码", ""))
    return CBRedeemItem(
        symbol=_format_cb_symbol(code),
        name=str(row.get("名称", "")),
        price=_to_float(row.get("现价")),
        stock_symbol=_format_stock_symbol(stock_code) if stock_code and len(stock_code) == 6 else stock_code or None,
        stock_name=str(row.get("正股名称", "")) or None,
        total_size=_to_float(row.get("规模")),
        remaining_size=_to_float(row.get("剩余规模")),
        conv_start_date=str(row.get("转股起始日", ""))[:10] or None,
        last_trade_date=str(row.get("最后交易日", ""))[:10] or None,
        maturity_date=str(row.get("到期日", ""))[:10] or None,
        conv_price=_to_float(row.get("转股价")),
        call_trigger_ratio=_to_float(row.get("强赎触发比")),
        call_trigger_price=_to_float(row.get("强赎触发价")),
        stock_price=_to_float(row.get("正股价")),
        call_price=_to_float(row.get("强赎价")),
        call_day_count=str(row.get("强赎天计数", "")) or None,
        call_clause=str(row.get("强赎条款", "")) or None,
        call_status=str(row.get("强赎状态", "")) or None,
    )


def adapt_cb_index_row(row: dict) -> CBIndexPoint:
    """Adapt a row from ak.bond_cb_index_jsl()."""
    return CBIndexPoint(
        date=str(row.get("price_dt", ""))[:10],
        price=_to_float(row.get("price")),
        amount=_to_float(row.get("amount")),
        volume=_to_float(row.get("volume")),
        count=_to_int(row.get("count")),
    )


def build_cb_summary_text(
    spot: list[CBSpotItem],
    redeem: list[CBRedeemItem],
    index: list[CBIndexPoint],
) -> str:
    parts: list[str] = []

    if spot:
        parts.append(f"可转债{len(spot)}只")
        low_double = [s for s in spot if s.double_low is not None]
        if low_double:
            lowest = low_double[0]  # sorted by double_low ascending
            parts.append(f"双低最低{lowest.name}({lowest.double_low:.1f})")
        neg_premium = [s for s in spot if s.conv_premium is not None and s.conv_premium < 0]
        if neg_premium:
            parts.append(f"负溢价{len(neg_premium)}只")

    if redeem:
        called = [r for r in redeem if r.call_status and "已公告" in r.call_status]
        near_call = [r for r in redeem if r.call_status and "接近" in r.call_status]
        parts.append(f"强赎监控{len(redeem)}只")
        if called:
            parts.append(f"已公告强赎{len(called)}只")
        if near_call:
            parts.append(f"接近强赎{len(near_call)}只")

    if index:
        latest = index[-1]
        if latest.price is not None:
            parts.append(f"转债指数{latest.price:.2f}")

    return "，".join(parts) if parts else "可转债数据暂无"

from __future__ import annotations

from cn_stock_mcp.app.models.bar import Bar
from cn_stock_mcp.app.models.indicator import IndicatorPoint, IndicatorSeries
from cn_stock_mcp.app.models.market_pool import MarketPoolItem
from cn_stock_mcp.infra.time_utils import normalize_symbol, normalize_time_string


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def adapt_zhitu_bar(raw: dict) -> Bar:
    return Bar(
        time=normalize_time_string(raw.get("t")) or "",
        open=_to_float(raw.get("o")),
        high=_to_float(raw.get("h")),
        low=_to_float(raw.get("l")),
        close=_to_float(raw.get("c")),
        volume=_to_float(raw.get("v")),
        turnover=_to_float(raw.get("a")),
        prev_close=_to_float(raw.get("pc")),
    )


def adapt_zhitu_indicator_series(symbol: str, sec_type: str, interval: str, indicator: str, items: list[dict]) -> IndicatorSeries:
    points: list[IndicatorPoint] = []
    for raw in items:
        values = {k: _to_float(v) for k, v in raw.items() if k != "t"}
        points.append(IndicatorPoint(time=normalize_time_string(raw.get("t")) or "", values=values))
    return IndicatorSeries(
        symbol=symbol,
        name=None,
        market="CN",
        sec_type=sec_type,
        interval=interval,
        indicator=indicator,  # type: ignore[arg-type]
        items=points,
        source="zhitu",
    )


def adapt_zhitu_limit_up_item(raw: dict) -> MarketPoolItem:
    return MarketPoolItem(
        symbol=normalize_symbol(str(raw.get("dm", "")).strip()),
        name=raw.get("mc") or "",
        price=_to_float(raw.get("p")),
        change_percent=_to_float(raw.get("zf")),
        turnover=_to_float(raw.get("cje")),
        turnover_rate=_to_float(raw.get("hs")),
        market_cap=_to_float(raw.get("zsz")),
        float_market_cap=_to_float(raw.get("lt")),
        extra={
            "pool_type": "limit_up",
            "limit_count": raw.get("lbc"),
            "first_limit_time": raw.get("fbt"),
            "last_limit_time": raw.get("lbt"),
            "limit_fund": raw.get("zj"),
            "board_burst_count": raw.get("zbc"),
            "stat": raw.get("tj"),
        },
    )


def adapt_zhitu_limit_down_item(raw: dict) -> MarketPoolItem:
    return MarketPoolItem(
        symbol=normalize_symbol(str(raw.get("dm", "")).strip()),
        name=raw.get("mc") or "",
        price=_to_float(raw.get("p")),
        change_percent=_to_float(raw.get("zf")),
        turnover=_to_float(raw.get("cje")),
        turnover_rate=_to_float(raw.get("hs")),
        market_cap=_to_float(raw.get("zsz")),
        float_market_cap=_to_float(raw.get("lt")),
        extra={
            "pool_type": "limit_down",
            "pe": _to_float(raw.get("pe")),
            "consecutive_limit_down_count": raw.get("lbc"),
            "last_limit_time": raw.get("lbt"),
            "limit_fund": raw.get("zj"),
            "board_trade_amount": _to_float(raw.get("fba")),
            "board_open_count": raw.get("zbc"),
        },
    )


def adapt_zhitu_strong_item(raw: dict) -> MarketPoolItem:
    return MarketPoolItem(
        symbol=normalize_symbol(str(raw.get("dm", "")).strip()),
        name=raw.get("mc") or "",
        price=_to_float(raw.get("p")),
        change_percent=_to_float(raw.get("zf")),
        turnover=_to_float(raw.get("cje")),
        turnover_rate=_to_float(raw.get("hs")),
        market_cap=_to_float(raw.get("zsz")),
        float_market_cap=_to_float(raw.get("lt")),
        extra={
            "pool_type": "strong",
            "limit_price": _to_float(raw.get("ztp")),
            "speed": _to_float(raw.get("zs")),
            "new_high": raw.get("nh"),
            "volume_ratio": _to_float(raw.get("lb")),
            "stat": raw.get("tj"),
        },
    )


def adapt_zhitu_sub_new_item(raw: dict) -> MarketPoolItem:
    return MarketPoolItem(
        symbol=normalize_symbol(str(raw.get("dm", "")).strip()),
        name=raw.get("mc") or "",
        price=_to_float(raw.get("p")),
        change_percent=_to_float(raw.get("zf")),
        turnover=_to_float(raw.get("cje")),
        turnover_rate=_to_float(raw.get("hs")),
        market_cap=_to_float(raw.get("zsz")),
        float_market_cap=_to_float(raw.get("lt")),
        extra={
            "pool_type": "sub_new",
            "limit_price": _to_float(raw.get("ztp")),
            "new_high": raw.get("nh"),
            "stat": raw.get("tj"),
            "open_board_days": raw.get("kb"),
            "open_board_date": raw.get("od"),
            "ipo_date": raw.get("ipod"),
        },
    )


def adapt_zhitu_broken_limit_item(raw: dict) -> MarketPoolItem:
    return MarketPoolItem(
        symbol=normalize_symbol(str(raw.get("dm", "")).strip()),
        name=raw.get("mc") or "",
        price=_to_float(raw.get("p")),
        change_percent=_to_float(raw.get("zdf") if raw.get("zdf") is not None else raw.get("zf")),
        turnover=_to_float(raw.get("cje")),
        turnover_rate=_to_float(raw.get("hs")),
        market_cap=_to_float(raw.get("zsz")),
        float_market_cap=_to_float(raw.get("lt")),
        extra={
            "pool_type": "broken_limit",
            "limit_price": _to_float(raw.get("ztp")),
            "amplitude": _to_float(raw.get("zf")),
            "speed": _to_float(raw.get("zs")),
            "stat": raw.get("tj"),
            "first_limit_time": raw.get("fbt"),
            "board_burst_count": raw.get("zbc"),
        },
    )

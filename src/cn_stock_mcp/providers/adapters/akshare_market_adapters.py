from __future__ import annotations

from cn_stock_mcp.app.models.bar import Bar
from cn_stock_mcp.app.models.market_pool import MarketPoolItem
from cn_stock_mcp.app.models.quote import Quote
from cn_stock_mcp.infra.time_utils import detect_board, normalize_symbol, normalize_time_string


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def adapt_akshare_quote_row(row: dict, symbol: str, sec_type: str) -> Quote:
    return Quote(
        symbol=symbol,
        name=row.get("名称") or row.get("name") or row.get("证券简称"),
        market="CN",
        exchange=symbol.split(".", 1)[1] if "." in symbol else None,
        board=detect_board(symbol, sec_type),
        sec_type=sec_type,  # type: ignore[arg-type]
        price=_to_float(row.get("最新价") or row.get("price")),
        open=_to_float(row.get("今开") or row.get("开盘") or row.get("open")),
        high=_to_float(row.get("最高") or row.get("high")),
        low=_to_float(row.get("最低") or row.get("low")),
        prev_close=_to_float(row.get("昨收") or row.get("prev_close")),
        change=_to_float(row.get("涨跌额") or row.get("change")),
        change_percent=_to_float(row.get("涨跌幅") or row.get("change_percent")),
        amplitude=_to_float(row.get("振幅") or row.get("amplitude")),
        volume=_to_float(row.get("成交量") or row.get("volume")),
        turnover=_to_float(row.get("成交额") or row.get("turnover")),
        turnover_rate=_to_float(row.get("换手率") or row.get("turnover_rate")),
        pe=_to_float(row.get("市盈率-动态") or row.get("市盈率") or row.get("pe")),
        pb=_to_float(row.get("市净率") or row.get("pb")),
        market_cap=_to_float(row.get("总市值") or row.get("market_cap")),
        float_market_cap=_to_float(row.get("流通市值") or row.get("float_market_cap")),
        timestamp=normalize_time_string(row.get("时间") or row.get("timestamp")),
        source="akshare",
    )


def adapt_akshare_bar_row(row: dict) -> Bar:
    return Bar(
        time=normalize_time_string(row.get("日期") or row.get("时间") or row.get("date") or row.get("time")) or "",
        open=_to_float(row.get("开盘") or row.get("open")),
        high=_to_float(row.get("最高") or row.get("high")),
        low=_to_float(row.get("最低") or row.get("low")),
        close=_to_float(row.get("收盘") or row.get("close")),
        volume=_to_float(row.get("成交量") or row.get("volume")),
        turnover=_to_float(row.get("成交额") or row.get("turnover")),
        prev_close=_to_float(row.get("前收") or row.get("prev_close")),
    )


def adapt_akshare_tx_bar_row(row: dict) -> Bar:
    return Bar(
        time=normalize_time_string(row.get("date") or row.get("日期") or row.get("time") or row.get("时间")) or "",
        open=_to_float(row.get("open") or row.get("开盘")),
        high=_to_float(row.get("high") or row.get("最高")),
        low=_to_float(row.get("low") or row.get("最低")),
        close=_to_float(row.get("close") or row.get("收盘")),
        volume=_to_float(row.get("volume") or row.get("成交量")),
        turnover=_to_float(row.get("amount") or row.get("成交额")),
        prev_close=_to_float(row.get("prev_close") or row.get("前收")),
    )


def adapt_akshare_market_pool_row(row: dict, pool_type: str) -> MarketPoolItem:
    """Adapt an EastMoney limit-pool row to the provider-neutral model."""

    code = str(row.get("代码") or row.get("code") or "").strip()
    symbol = normalize_symbol(code)
    return MarketPoolItem(
        symbol=symbol,
        name=str(row.get("名称") or row.get("name") or ""),
        price=_to_float(row.get("最新价") or row.get("price")),
        change_percent=_to_float(row.get("涨跌幅") or row.get("change_percent")),
        turnover=_to_float(row.get("成交额") or row.get("turnover")),
        turnover_rate=_to_float(row.get("换手率") or row.get("转手率") or row.get("turnover_rate")),
        market_cap=_to_float(row.get("总市值") or row.get("market_cap")),
        float_market_cap=_to_float(row.get("流通市值") or row.get("float_market_cap")),
        extra={
            "pool_type": pool_type,
            "limit_price": _to_float(row.get("涨停价") or row.get("limit_price")),
            "limit_count": row.get("连板数") or row.get("涨停统计"),
            "first_limit_time": row.get("首次封板时间"),
            "last_limit_time": row.get("最后封板时间"),
            "industry": row.get("所属行业") or row.get("industry"),
        },
    )

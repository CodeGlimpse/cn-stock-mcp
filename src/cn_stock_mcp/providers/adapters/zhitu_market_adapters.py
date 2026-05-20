from __future__ import annotations

from cn_stock_mcp.app.models.orderbook import OrderBook, OrderBookLevel
from cn_stock_mcp.app.models.quote import Quote
from cn_stock_mcp.infra.time_utils import detect_board, normalize_time_string


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def adapt_zhitu_quote(raw: dict, symbol: str, sec_type: str, exchange: str | None = None, board: str | None = None) -> Quote:
    return Quote(
        symbol=symbol,
        name=None,
        market="CN",
        exchange=exchange,
        board=board or detect_board(symbol, sec_type),
        sec_type=sec_type,
        price=_to_float(raw.get("p")),
        open=_to_float(raw.get("o")),
        high=_to_float(raw.get("h")),
        low=_to_float(raw.get("l")),
        prev_close=_to_float(raw.get("yc")),
        change=_to_float(raw.get("ud")),
        change_percent=_to_float(raw.get("pc")),
        amplitude=_to_float(raw.get("zf")),
        volume=_to_float(raw.get("v") if raw.get("v") is not None else raw.get("tv")),
        turnover=_to_float(raw.get("cje")),
        turnover_rate=_to_float(raw.get("tr") if raw.get("tr") is not None else raw.get("hs")),
        pe=_to_float(raw.get("pe")),
        pb=_to_float(raw.get("pb_ratio") if raw.get("pb_ratio") is not None else raw.get("sjl")),
        market_cap=_to_float(raw.get("sz") if raw.get("sz") is not None else raw.get("zsz")),
        float_market_cap=_to_float(raw.get("lt")),
        currency="CNY",
        trading_status=None,
        timestamp=normalize_time_string(raw.get("t")),
        source="zhitu",
    )


def adapt_zhitu_batch_quote(raw: dict, code: str, exchange: str) -> Quote:
    """Adapt a single item from /hs/public/ssjymore batch response.

    Batch response fields differ slightly from single-quote endpoint:
    - Uses 'dm' for code, 'mc' for name
    - No 'yc' (prev_close), no 'ud' (change), no 't' (timestamp)
    - Has 'fm' (5-min change %), 'lb' (volume ratio)
    """
    symbol = f"{code}.{exchange}"
    return Quote(
        symbol=symbol,
        name=raw.get("mc"),
        market="CN",
        exchange=exchange,
        board=detect_board(symbol, "stock"),
        sec_type="stock",
        price=_to_float(raw.get("p")),
        open=_to_float(raw.get("o")),
        high=_to_float(raw.get("h")),
        low=_to_float(raw.get("l")),
        prev_close=None,  # batch endpoint does not provide yc
        change=None,  # batch endpoint does not provide ud
        change_percent=_to_float(raw.get("pc")),
        amplitude=_to_float(raw.get("zf")),
        volume=_to_float(raw.get("v")),
        turnover=_to_float(raw.get("cje")),
        turnover_rate=_to_float(raw.get("hs")),
        pe=_to_float(raw.get("pe")),
        pb=_to_float(raw.get("sjl")),
        market_cap=_to_float(raw.get("sz")),
        float_market_cap=_to_float(raw.get("lt")),
        currency="CNY",
        trading_status=None,
        timestamp=None,  # batch endpoint does not provide timestamp
        source="zhitu",
    )


def adapt_zhitu_orderbook(raw: dict, symbol: str) -> OrderBook:
    bids: list[OrderBookLevel] = []
    asks: list[OrderBookLevel] = []

    pb = raw.get("pb")
    vb = raw.get("vb")
    ps = raw.get("ps")
    vs = raw.get("vs")

    if isinstance(pb, list) and isinstance(vb, list):
        for price, volume in zip(pb, vb):
            bid_price = _to_float(price)
            bid_volume = _to_float(volume)
            if bid_price is not None or bid_volume is not None:
                bids.append(OrderBookLevel(price=bid_price, volume=bid_volume))

    if isinstance(ps, list) and isinstance(vs, list):
        for price, volume in zip(ps, vs):
            ask_price = _to_float(price)
            ask_volume = _to_float(volume)
            if ask_price is not None or ask_volume is not None:
                asks.append(OrderBookLevel(price=ask_price, volume=ask_volume))

    if not bids and not asks:
        for i in range(5):
            bid_price = _to_float(raw.get(f"pb{i+1}"))
            bid_volume = _to_float(raw.get(f"vb{i+1}"))
            ask_price = _to_float(raw.get(f"ps{i+1}"))
            ask_volume = _to_float(raw.get(f"vs{i+1}"))
            if bid_price is not None or bid_volume is not None:
                bids.append(OrderBookLevel(price=bid_price, volume=bid_volume))
            if ask_price is not None or ask_volume is not None:
                asks.append(OrderBookLevel(price=ask_price, volume=ask_volume))

    if not bids and not asks:
        for i in range(5):
            bid_price = _to_float(raw.get(f"pb_{i+1}"))
            bid_volume = _to_float(raw.get(f"vb_{i+1}"))
            ask_price = _to_float(raw.get(f"ps_{i+1}"))
            ask_volume = _to_float(raw.get(f"vs_{i+1}"))
            if bid_price is not None or bid_volume is not None:
                bids.append(OrderBookLevel(price=bid_price, volume=bid_volume))
            if ask_price is not None or ask_volume is not None:
                asks.append(OrderBookLevel(price=ask_price, volume=ask_volume))

    return OrderBook(
        symbol=symbol,
        timestamp=normalize_time_string(raw.get("t")),
        bids=bids,
        asks=asks,
        source="zhitu",
    )

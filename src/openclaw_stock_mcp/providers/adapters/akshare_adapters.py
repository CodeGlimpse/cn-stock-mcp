from __future__ import annotations

from openclaw_stock_mcp.app.models.instrument import Instrument
from openclaw_stock_mcp.infra.time_utils import detect_board, normalize_exchange, normalize_symbol


def _guess_index_exchange(raw_code: str, exchange: str | None) -> str | None:
    if exchange:
        return exchange
    if raw_code.startswith("399"):
        return "SZ"
    if raw_code.startswith("899"):
        return "BJ"
    if raw_code.startswith("000"):
        return "SH"
    return None


def _guess_fund_exchange(raw_code: str, exchange: str | None) -> str | None:
    if exchange:
        return exchange
    if raw_code.startswith(("50", "51", "56", "58")):
        return "SH"
    if raw_code.startswith(("15", "16")):
        return "SZ"
    return None


def adapt_akshare_stock_list_row(row: dict) -> Instrument:
    raw_code = str(
        row.get("symbol")
        or row.get("代码")
        or row.get("证券代码")
        or row.get("code")
        or ""
    ).strip()
    raw_name = row.get("name") or row.get("名称") or row.get("证券简称")
    exchange = normalize_exchange(row.get("exchange") or row.get("交易所"))
    symbol = normalize_symbol(raw_code, exchange) if raw_code else ""
    return Instrument(
        symbol=symbol,
        name=raw_name,
        market="CN",
        exchange=(symbol.split(".", 1)[1] if "." in symbol else None),
        board=(detect_board(symbol, "stock") if symbol else None),
        sec_type="stock",
        raw_symbol=raw_code or None,
        source="akshare",
    )


def adapt_akshare_index_list_row(row: dict) -> Instrument:
    raw_code = str(
        row.get("symbol")
        or row.get("代码")
        or row.get("指数代码")
        or row.get("index_code")
        or row.get("code")
        or ""
    ).strip()
    raw_name = row.get("name") or row.get("名称") or row.get("指数名称") or row.get("display_name")
    exchange = normalize_exchange(row.get("exchange") or row.get("交易所"))
    index_exchange = _guess_index_exchange(raw_code, exchange)
    symbol = normalize_symbol(raw_code, index_exchange) if raw_code else ""
    return Instrument(
        symbol=symbol,
        name=raw_name,
        market="CN",
        exchange=(symbol.split(".", 1)[1] if "." in symbol else None),
        board="index",
        sec_type="index",
        raw_symbol=raw_code or None,
        source="akshare",
    )


def adapt_akshare_fund_list_row(row: dict) -> Instrument:
    raw_code = str(row.get("symbol") or row.get("代码") or row.get("基金代码") or row.get("code") or "").strip()
    raw_name = row.get("name") or row.get("名称") or row.get("基金简称")
    exchange = normalize_exchange(row.get("exchange") or row.get("交易所"))
    fund_exchange = _guess_fund_exchange(raw_code, exchange)
    symbol = normalize_symbol(raw_code, fund_exchange) if raw_code else ""
    return Instrument(
        symbol=symbol,
        name=raw_name,
        market="CN",
        exchange=(symbol.split(".", 1)[1] if "." in symbol else None),
        board="fund",
        sec_type="fund",
        raw_symbol=raw_code or None,
        source="akshare",
    )

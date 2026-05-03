from __future__ import annotations

from openclaw_stock_mcp.app.models.instrument import Instrument
from openclaw_stock_mcp.infra.time_utils import detect_board, normalize_exchange, normalize_symbol


def adapt_zhitu_stock_list_item(raw: dict) -> Instrument:
    exchange = normalize_exchange(raw.get("jys"))
    symbol = normalize_symbol(str(raw.get("dm", "")).strip(), exchange)
    return Instrument(
        symbol=symbol,
        name=raw.get("mc"),
        market="CN",
        exchange=exchange,
        board=detect_board(symbol, "stock"),
        sec_type="stock",
        raw_symbol=str(raw.get("dm", "")).strip() or None,
        source="zhitu",
    )


def adapt_zhitu_index_list_item(raw: dict) -> Instrument:
    exchange = normalize_exchange(raw.get("jys"))
    symbol = normalize_symbol(str(raw.get("dm", "")).strip(), exchange)
    return Instrument(
        symbol=symbol,
        name=raw.get("mc"),
        market="CN",
        exchange=exchange,
        board="index",
        sec_type="index",
        raw_symbol=str(raw.get("dm", "")).strip() or None,
        source="zhitu",
    )


def adapt_zhitu_fund_list_item(raw: dict) -> Instrument:
    exchange = normalize_exchange(raw.get("jys"))
    symbol = normalize_symbol(str(raw.get("dm", "")).strip(), exchange)
    return Instrument(
        symbol=symbol,
        name=raw.get("mc"),
        market="CN",
        exchange=exchange,
        board="fund",
        sec_type="fund",
        raw_symbol=str(raw.get("dm", "")).strip() or None,
        source="zhitu",
    )


def adapt_zhitu_sector_list_item(raw: dict) -> Instrument:
    symbol = normalize_symbol(str(raw.get("dm", "")).strip())
    return Instrument(
        symbol=symbol,
        name=raw.get("mc"),
        market="CN",
        exchange="BK",
        board="sector",
        sec_type="sector",
        raw_symbol=str(raw.get("dm", "")).strip() or None,
        source="zhitu",
    )


def adapt_zhitu_primary_sector_item(raw: dict) -> Instrument:
    name = str(raw.get("mc") or raw.get("name") or "").strip()
    dm = str(raw.get("dm") or "").strip()
    primary_key = name or dm or "UNKNOWN"
    symbol = f"PRIMARY:{primary_key}"
    return Instrument(
        symbol=symbol,
        name=name or dm or None,
        market="CN",
        exchange="BK",
        board="sector-primary",
        sec_type="sector",
        raw_symbol=dm or name or None,
        source="zhitu",
    )


def adapt_zhitu_sector_member_item(raw: dict) -> Instrument:
    exchange = normalize_exchange(raw.get("jys"))
    symbol = normalize_symbol(str(raw.get("dm", "")).strip(), exchange)
    return Instrument(
        symbol=symbol,
        name=raw.get("mc"),
        market="CN",
        exchange=exchange,
        board=detect_board(symbol, "stock"),
        sec_type="stock",
        raw_symbol=str(raw.get("dm", "")).strip() or None,
        source="zhitu",
    )

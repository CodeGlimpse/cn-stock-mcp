from __future__ import annotations

from openclaw_stock_mcp.app.models.sector_quote import SectorQuote
from openclaw_stock_mcp.infra.time_utils import normalize_time_string


def _to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def adapt_zhitu_sector_quote(raw: dict, symbol: str, sector_type: str | None = None) -> SectorQuote:
    """Adapt a sector index quote from Zhitu /hz/real/ssjy endpoint.

    Sector indices use the same endpoint as regular indices but have
    symbols like 101076.BKZS for concept sectors.
    """
    return SectorQuote(
        symbol=symbol,
        name=raw.get("mc") or raw.get("name"),
        market="CN",
        sector_type=sector_type,
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
        turnover_rate=_to_float(raw.get("hs")),
        currency="CNY",
        timestamp=normalize_time_string(raw.get("t")),
        source="zhitu",
    )

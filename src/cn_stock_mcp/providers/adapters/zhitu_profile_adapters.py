from __future__ import annotations

from cn_stock_mcp.app.models.profile import (
    StockProfile,
    DividendRecord,
    UnlockRecord,
    QuarterProfit,
)


def _to_float(value):
    if value is None or value == "" or value == "--":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_concepts(idea: str | None) -> list[str]:
    if not idea:
        return []
    return [c.strip() for c in idea.split(",") if c.strip()]


def adapt_zhitu_profile(raw: dict, symbol: str) -> StockProfile:
    return StockProfile(
        symbol=symbol,
        name=raw.get("name"),
        ename=raw.get("ename"),
        market=raw.get("market"),
        list_date=raw.get("ldate"),
        issue_price=raw.get("sprice"),
        registered_capital=raw.get("rprice"),
        industry=raw.get("instype"),
        organization_type=raw.get("organ"),
        business_scope=raw.get("bscope"),
        description=raw.get("desc"),
        concepts=_parse_concepts(raw.get("idea")),
        address=raw.get("addr"),
        office_address=raw.get("oaddr"),
        website=raw.get("site"),
        email=raw.get("email"),
        phone=raw.get("phone"),
        secretary=raw.get("secre"),
        source="zhitu",
    )


def adapt_zhitu_dividend(raw: dict) -> DividendRecord:
    return DividendRecord(
        announce_date=raw.get("sdate"),
        bonus_per_10=_to_float(raw.get("give")),
        transfer_per_10=_to_float(raw.get("change")),
        dividend_per_10=_to_float(raw.get("send")),
        progress=raw.get("line"),
        ex_dividend_date=raw.get("cdate") if raw.get("cdate") and raw.get("cdate") != "--" else None,
        record_date=raw.get("edate") if raw.get("edate") and raw.get("edate") != "--" else None,
    )


def adapt_zhitu_unlock(raw: dict) -> UnlockRecord:
    return UnlockRecord(
        unlock_date=raw.get("rdate"),
        unlock_amount=_to_float(raw.get("ramount")),
        unlock_value=_to_float(raw.get("rprice")),
        batch=raw.get("batch"),
        announce_date=raw.get("pdate"),
    )


def adapt_zhitu_quarter_profit(raw: dict) -> QuarterProfit:
    return QuarterProfit(
        period=raw.get("date"),
        revenue=_to_float(raw.get("reven")),
        net_profit=_to_float(raw.get("nprof")),
        eps=_to_float(raw.get("eps")),
    )


def build_dividend_summary(dividends: list[DividendRecord]) -> dict:
    if not dividends:
        return {"total_years": 0, "avg_dividend_per_10": None, "dividend_years": []}

    dividend_values = [d.dividend_per_10 for d in dividends if d.dividend_per_10 is not None and d.dividend_per_10 > 0]
    dividend_years = sorted(set(
        d.announce_date[:4] for d in dividends
        if d.announce_date and d.dividend_per_10 is not None and d.dividend_per_10 > 0
    ))

    return {
        "total_years": len(dividend_years),
        "avg_dividend_per_10": (sum(dividend_values) / len(dividend_values)) if dividend_values else None,
        "dividend_years": dividend_years,
        "latest_dividend": dividends[0].model_dump() if dividends else None,
    }


def build_unlock_risk(unlocks: list[UnlockRecord]) -> dict:
    if not unlocks:
        return {"has_future_unlock": False, "total_unlock_value": None, "upcoming_unlocks": []}

    upcoming = [u for u in unlocks if u.unlock_amount and u.unlock_amount > 0]
    total_value = sum(u.unlock_value or 0 for u in upcoming)

    return {
        "has_future_unlock": len(upcoming) > 0,
        "total_unlock_value": total_value if total_value > 0 else None,
        "upcoming_count": len(upcoming),
        "upcoming_unlocks": [u.model_dump() for u in upcoming[:5]],
    }

from __future__ import annotations

from openclaw_stock_mcp.app.models.derivatives_data import (
    FuturesHistItem,
    FuturesSpotItem,
    OptionContractItem,
    QVIXItem,
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


# ── Futures Spot ──────────────────────────────────────────────────

def adapt_futures_spot_row(row: dict) -> FuturesSpotItem:
    """Adapt a row from ak.futures_zh_realtime()."""
    return FuturesSpotItem(
        symbol=str(row.get("symbol", "")),
        exchange=str(row.get("exchange", "")) or None,
        name=str(row.get("name", "")) or None,
        price=_to_float(row.get("trade")),
        settlement=_to_float(row.get("settlement")),
        prev_settlement=_to_float(row.get("prevsettlement")) or _to_float(row.get("presettlement")),
        open=_to_float(row.get("open")),
        high=_to_float(row.get("high")),
        low=_to_float(row.get("low")),
        close=_to_float(row.get("close")),
        volume=_to_float(row.get("volume")),
        position=_to_float(row.get("position")),
        change_percent=_to_float(row.get("changepercent")),
        trade_date=str(row.get("tradedate", ""))[:10] or None,
        tick_time=str(row.get("ticktime", "")) or None,
    )


# ── Futures History ───────────────────────────────────────────────

def adapt_futures_hist_row(row: dict) -> FuturesHistItem:
    """Adapt a row from ak.futures_zh_daily_sina()."""
    return FuturesHistItem(
        date=str(row.get("date", ""))[:10],
        open=_to_float(row.get("open")),
        high=_to_float(row.get("high")),
        low=_to_float(row.get("low")),
        close=_to_float(row.get("close")),
        volume=_to_float(row.get("volume")),
        position=_to_float(row.get("hold")),
        settle=_to_float(row.get("settle")),
    )


# ── Option List (SSE) ─────────────────────────────────────────────

def adapt_option_sse_row(row: dict) -> OptionContractItem:
    """Adapt a row from ak.option_current_day_sse()."""
    return OptionContractItem(
        code=str(row.get("合约编码", "")),
        contract_code=str(row.get("合约交易代码", "")) or None,
        name=str(row.get("合约简称", "")) or None,
        underlying=str(row.get("标的券名称及代码", "")) or None,
        option_type=str(row.get("类型", "")) or None,
        strike=_to_float(row.get("行权价")),
        unit=_to_int(row.get("合约单位")),
        expire_date=str(row.get("到期日", ""))[:10] or None,
        exchange="SSE",
    )


# ── Option List (SZSE) ───────────────────────────────────────────

def adapt_option_szse_row(row: dict) -> OptionContractItem:
    """Adapt a row from ak.option_current_day_szse()."""
    return OptionContractItem(
        code=str(row.get("合约编码", "")),
        contract_code=str(row.get("合约代码", "")) or None,
        name=str(row.get("合约简称", "")) or None,
        underlying=str(row.get("标的证券简称(代码)", "")) or None,
        option_type=str(row.get("合约类型", "")) or None,
        strike=_to_float(row.get("行权价")),
        unit=_to_int(row.get("合约单位")),
        expire_date=str(row.get("到期日", ""))[:10] or None,
        exchange="SZSE",
        upper_limit=_to_float(row.get("涨停价格")),
        lower_limit=_to_float(row.get("跌停价格")),
        prev_settle=_to_float(row.get("前结算价")),
        total_position=_to_float(row.get("合约总持仓")),
    )


# ── QVIX ─────────────────────────────────────────────────────────

def adapt_qvix_row(row: dict) -> QVIXItem:
    """Adapt a row from ak.index_option_*_qvix()."""
    return QVIXItem(
        date=str(row.get("date", ""))[:10],
        open=_to_float(row.get("open")),
        high=_to_float(row.get("high")),
        low=_to_float(row.get("low")),
        close=_to_float(row.get("close")),
    )


# ── Summary ───────────────────────────────────────────────────────

def build_derivatives_summary_text(
    futures_spot: list[FuturesSpotItem],
    futures_hist: list[FuturesHistItem],
    option_list: list[OptionContractItem],
    qvix: list[QVIXItem],
) -> str:
    parts: list[str] = []

    if futures_spot:
        parts.append(f"期货主力{len(futures_spot)}只")
        up = [f for f in futures_spot if f.change_percent is not None and f.change_percent > 0]
        down = [f for f in futures_spot if f.change_percent is not None and f.change_percent < 0]
        parts.append(f"涨{len(up)}跌{len(down)}")

    if futures_hist:
        latest = futures_hist[-1]
        if latest.close is not None:
            parts.append(f"最新收盘{latest.close}")

    if option_list:
        call = [o for o in option_list if o.option_type and "购" in o.option_type]
        put = [o for o in option_list if o.option_type and "沽" in o.option_type]
        parts.append(f"期权合约{len(option_list)}只(购{len(call)}/沽{len(put)})")

    if qvix:
        latest = qvix[-1]
        if latest.close is not None:
            parts.append(f"QVIX{latest.close:.2f}")

    return "，".join(parts) if parts else "衍生品数据暂无"

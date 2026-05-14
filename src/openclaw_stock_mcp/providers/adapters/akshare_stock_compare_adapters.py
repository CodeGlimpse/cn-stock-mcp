from __future__ import annotations

from openclaw_stock_mcp.app.models.stock_compare import StockCompareItem, StockCompareResult
from openclaw_stock_mcp.infra.time_utils import normalize_symbol


def _to_float(value):
    if value is None or value == "" or value == "NaN":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s and s != "NaN" and s != "NaT" else None


def merge_quote(item: StockCompareItem, row: dict) -> StockCompareItem:
    """Merge Sina spot data into compare item."""
    raw_code = str(row.get("代码", "")).strip()
    code = raw_code.lstrip("sh").lstrip("sz").lstrip("bj")
    symbol = normalize_symbol(raw_code) if raw_code else ""
    if item.symbol != symbol:
        return item
    return item.model_copy(update={
        "name": _clean_str(row.get("名称")) or item.name,
        "latest_price": _to_float(row.get("最新价")),
        "change_pct": _to_float(row.get("涨跌幅")),
        "volume": _to_float(row.get("成交量")),
        "turnover": _to_float(row.get("成交额")),
        "source_quote": "akshare_sina",
    })


def merge_valuation(item: StockCompareItem, quote) -> StockCompareItem:
    """Merge Zhitu quote data (PE/PB/market_cap) into compare item."""
    q_symbol = getattr(quote, "symbol", "")
    if item.symbol != q_symbol:
        return item
    return item.model_copy(update={
        "name": getattr(quote, "name", None) or item.name,
        "latest_price": getattr(quote, "price", None) or item.latest_price,
        "change_pct": getattr(quote, "change_percent", None) or item.change_pct,
        "amplitude": getattr(quote, "amplitude", None),
        "volume": getattr(quote, "volume", None) or item.volume,
        "turnover": getattr(quote, "turnover", None) or item.turnover,
        "pe": getattr(quote, "pe", None),
        "pb": getattr(quote, "pb", None),
        "market_cap": getattr(quote, "market_cap", None),
        "float_market_cap": getattr(quote, "float_market_cap", None),
        "turnover_rate": getattr(quote, "turnover_rate", None),
        "source_valuation": "zhitu",
    })


def merge_financial(item: StockCompareItem, raw_rows: list[dict]) -> StockCompareItem:
    """Merge AKShare financial abstract into compare item.

    stock_financial_abstract returns a transposed table:
    columns = report dates, rows = indicators.
    We extract the latest column for key indicators.
    """
    if not raw_rows:
        return item

    # Find key indicators
    indicator_map = {
        "营业总收入": "revenue",
        "归母净利润": "net_profit",
        "净资产收益率": "roe",
        "毛利率": "gross_margin",
        "资产负债率": "debt_ratio",
        "每股收益": "eps",
    }

    updates = {"source_financial": "akshare"}
    # Find the latest date column (2nd column after '指标')
    if len(raw_rows) > 0:
        all_keys = list(raw_rows[0].keys())
        date_cols = [k for k in all_keys if k not in ("选项", "指标") and len(k) == 8 and k.isdigit()]
        latest_col = date_cols[0] if date_cols else None

        for row in raw_rows:
            indicator = str(row.get("指标", "")).strip()
            target_key = indicator_map.get(indicator)
            if target_key and latest_col and latest_col in row:
                val = _to_float(row[latest_col])
                if val is not None:
                    updates[target_key] = val

    return item.model_copy(update=updates)


def merge_dividend(item: StockCompareItem, dividend_yield: float | None, eps: float | None) -> StockCompareItem:
    updates = {}
    if dividend_yield is not None:
        updates["dividend_yield"] = dividend_yield
    if eps is not None:
        updates["eps"] = eps
    if not updates:
        return item
    return item.model_copy(update=updates)


def build_compare_summary(items: list[StockCompareItem], includes: list[str]) -> str:
    if not items:
        return "无对比数据"
    names = [i.name or i.symbol for i in items]
    parts = [f"对比 {' vs '.join(names[:5])}"]
    if len(names) > 5:
        parts.append(f"等 {len(names)} 只")
    pe_items = [i for i in items if i.pe is not None]
    if pe_items:
        pe_min = min(i.pe for i in pe_items)
        pe_max = max(i.pe for i in pe_items)
        parts.append(f"PE {pe_min:.1f}~{pe_max:.1f}")
    mc_items = [i for i in items if i.market_cap is not None]
    if mc_items:
        parts.append(f"市值 {min(i.market_cap for i in mc_items)/1e8:.0f}~{max(i.market_cap for i in mc_items)/1e8:.0f} 亿")
    return "；".join(parts)

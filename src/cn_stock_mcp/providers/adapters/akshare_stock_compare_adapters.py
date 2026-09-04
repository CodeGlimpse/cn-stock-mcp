from __future__ import annotations

from collections.abc import Mapping, Sequence

from cn_stock_mcp.app.models.financial import FinancialSnapshot
from cn_stock_mcp.app.models.stock_compare import StockCompareItem
from cn_stock_mcp.infra.time_utils import normalize_symbol


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


def _get_value(value, key: str, default=None):
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def _first_not_none(*values):
    for value in values:
        if value is not None:
            return value
    return None


def _to_percent(value):
    """Normalize ratio-like financial fields to percentage points.

    The normalized AKShare financial model stores ratios as fractions (for
    example 0.125), while some legacy wide tables expose 12.5.  Values in
    [-1, 1] are therefore interpreted as fractions; larger values are kept.
    """

    number = _to_float(value)
    if number is not None and -1 <= number <= 1:
        return number * 100
    return number


def merge_quote(item: StockCompareItem, row) -> StockCompareItem:
    """Merge a legacy Sina row or a normalized Quote into a compare item."""
    if not isinstance(row, Mapping) or ("symbol" in row and "代码" not in row):
        symbol = _get_value(row, "symbol", "")
        try:
            symbol = normalize_symbol(str(symbol)) if symbol else ""
        except Exception:
            symbol = str(symbol)
        if symbol != item.symbol:
            return item
        updates = {
            "name": _get_value(row, "name") or item.name,
            "latest_price": _first_not_none(_get_value(row, "price"), item.latest_price),
            "change_pct": _first_not_none(_get_value(row, "change_percent"), item.change_pct),
            "volume": _first_not_none(_get_value(row, "volume"), item.volume),
            "turnover": _first_not_none(_get_value(row, "turnover"), item.turnover),
            "amplitude": _first_not_none(_get_value(row, "amplitude"), item.amplitude),
            "source_quote": _get_value(row, "source", "") or item.source_quote,
        }
        return item.model_copy(update=updates)

    raw_code = str(row.get("代码", "")).strip()
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


def merge_valuation(item: StockCompareItem, quote, source: str | None = None) -> StockCompareItem:
    """Merge normalized provider quote data (PE/PB/market_cap) into compare item."""
    q_symbol = _get_value(quote, "symbol", "")
    try:
        q_symbol = normalize_symbol(str(q_symbol)) if q_symbol else ""
    except Exception:
        q_symbol = str(q_symbol)
    if item.symbol != q_symbol:
        return item
    return item.model_copy(update={
        "name": _get_value(quote, "name") or item.name,
        "latest_price": _first_not_none(_get_value(quote, "price"), item.latest_price),
        "change_pct": _first_not_none(_get_value(quote, "change_percent"), item.change_pct),
        "amplitude": _first_not_none(_get_value(quote, "amplitude"), item.amplitude),
        "volume": _first_not_none(_get_value(quote, "volume"), item.volume),
        "turnover": _first_not_none(_get_value(quote, "turnover"), item.turnover),
        "pe": _first_not_none(_get_value(quote, "pe"), item.pe),
        "pb": _first_not_none(_get_value(quote, "pb"), item.pb),
        "market_cap": _first_not_none(_get_value(quote, "market_cap"), item.market_cap),
        "float_market_cap": _first_not_none(_get_value(quote, "float_market_cap"), item.float_market_cap),
        "turnover_rate": _first_not_none(_get_value(quote, "turnover_rate"), item.turnover_rate),
        "source_valuation": source or _get_value(quote, "source") or "unknown",
    })


def merge_financial(item: StockCompareItem, raw_result) -> StockCompareItem:
    """Merge AKShare financial abstract into compare item.

    stock_financial_abstract returns a transposed table:
    columns = report dates, rows = indicators.
    We extract the latest column for key indicators.
    """
    snapshot = None
    raw_rows = raw_result
    # Current provider contract is (raw_rows, FinancialSnapshot, history).
    if isinstance(raw_result, tuple):
        raw_rows = raw_result[0] if len(raw_result) > 0 else []
        snapshot = raw_result[1] if len(raw_result) > 1 else None
    elif isinstance(raw_result, FinancialSnapshot):
        snapshot = raw_result
        raw_rows = []
    elif isinstance(raw_result, Mapping):
        snapshot = raw_result.get("snapshot")
        raw_rows = raw_result.get("rows", raw_result.get("raw_rows", []))

    if snapshot is not None:
        updates = {
            "revenue": _to_float(_get_value(snapshot, "operating_revenue")),
            "net_profit": _to_float(_get_value(snapshot, "net_profit")),
            "roe": _to_percent(_get_value(snapshot, "roe_weighted")),
            "gross_margin": _to_percent(_get_value(snapshot, "sale_gross_margin")),
            "debt_ratio": _to_percent(_get_value(snapshot, "assets_debt_ratio")),
            "eps": _to_float(_get_value(snapshot, "basic_eps")),
            "source_financial": "akshare",
        }
        metric_updates = {key: value for key, value in updates.items() if key != "source_financial" and value is not None}
        if not metric_updates:
            return item
        metric_updates["source_financial"] = "akshare"
        return item.model_copy(update=metric_updates)

    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, (str, bytes, bytearray)) or not raw_rows:
        return item

    # Find key indicators
    indicator_map = {
        "营业总收入": "revenue", "营业收入": "revenue", "营业总收入(元)": "revenue",
        "归母净利润": "net_profit", "归属于母公司股东的净利润": "net_profit",
        "净资产收益率": "roe", "净资产收益率(加权)": "roe", "加权平均净资产收益率": "roe",
        "毛利率": "gross_margin", "销售毛利率": "gross_margin",
        "资产负债率": "debt_ratio", "每股收益": "eps", "基本每股收益": "eps",
    }

    updates: dict[str, object] = {}
    # Find the latest date column (2nd column after '指标')
    if len(raw_rows) > 0:
        if not isinstance(raw_rows[0], Mapping):
            return item
        all_keys = list(raw_rows[0].keys())
        date_cols = [k for k in all_keys if k not in ("选项", "指标") and len(k) == 8 and k.isdigit()]
        latest_col = max(date_cols) if date_cols else None

        for row in raw_rows:
            if not isinstance(row, Mapping):
                continue
            indicator = str(row.get("指标", row.get("metric_name", ""))).strip()
            target_key = indicator_map.get(indicator)
            if target_key and latest_col and latest_col in row:
                val = _to_percent(row[latest_col]) if target_key in {"roe", "gross_margin", "debt_ratio"} else _to_float(row[latest_col])
                if val is not None:
                    updates[target_key] = val

        # The current normalized provider shape uses ``metric_name`` plus a
        # ``value`` column rather than Chinese wide-table date columns.
        if not updates and any(isinstance(row, Mapping) and "metric_name" in row for row in raw_rows):
            dated_rows = [row for row in raw_rows if isinstance(row, Mapping) and row.get("report_date")]
            latest_date = max((str(row.get("report_date"))[:10] for row in dated_rows), default=None)
            for row in dated_rows:
                if latest_date and str(row.get("report_date"))[:10] != latest_date:
                    continue
                target_key = {
                    "operating_income_total": "revenue",
                    "parent_holder_net_profit": "net_profit",
                    "index_weighted_avg_roe": "roe",
                    "sale_gross_margin": "gross_margin",
                    "assets_debt_ratio": "debt_ratio",
                    "basic_eps": "eps",
                }.get(str(row.get("metric_name", "")))
                if not target_key:
                    continue
                raw_value = row.get("value")
                val = _to_percent(raw_value) if target_key in {"roe", "gross_margin", "debt_ratio"} else _to_float(raw_value)
                if val is not None:
                    updates[target_key] = val

    if not updates:
        return item
    updates["source_financial"] = "akshare"

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

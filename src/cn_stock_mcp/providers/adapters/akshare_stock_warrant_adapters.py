from __future__ import annotations

from cn_stock_mcp.app.models.stock_warrant import OptionItem


def _to_float(value):
    if value is None or value == "" or value == "NaN" or value == "-" or value == "--":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s and s != "NaN" and s != "NaT" and s != "--" and s != "-" else None


def adapt_option_row(row: dict) -> OptionItem:
    return OptionItem(
        symbol=_clean_str(row.get("合约名称", row.get("代码", row.get("合约代码")))),
        name=_clean_str(row.get("合约名称", row.get("名称"))),
        latest_price=_to_float(row.get("最新价", row.get("现价", row.get("收盘价")))),
        change_pct=_to_float(row.get("涨跌幅", row.get("涨跌"))),
        change_amt=_to_float(row.get("涨跌额", row.get("涨跌值"))),
        volume=_to_float(row.get("成交量", row.get("总成交量"))),
        open_interest=_to_float(row.get("持仓量", row.get("空盘量"))),
        strike=_to_float(row.get("行权价", row.get("执行价格"))),
        expiry=_clean_str(row.get("到期日", row.get("最后交易日"))),
        option_type=None,
    )


def build_warrant_summary(etf: list, commodity: list, index: list) -> str:
    parts = []
    if etf:
        call = [o for o in etf if o.option_type == "认购" or (o.name and "购" in str(o.name))]
        put = [o for o in etf if o.option_type == "认沽" or (o.name and "沽" in str(o.name))]
        parts.append(f"ETF期权 {len(etf)} 只")
    if commodity:
        parts.append(f"商品期权 {len(commodity)} 只")
    if index:
        parts.append(f"股指期权 {len(index)} 只")
    if not parts:
        return "无期权数据"
    return "；".join(parts)

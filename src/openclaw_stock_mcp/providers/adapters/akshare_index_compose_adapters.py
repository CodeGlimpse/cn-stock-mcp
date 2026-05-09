from __future__ import annotations

from openclaw_stock_mcp.app.models.index_compose import IndexComposeSummary, IndexConstituentItem


def _normalize_symbol(code: str) -> str:
    code = str(code or "").strip()
    if len(code) == 6:
        if code.startswith("6"):
            return f"{code}.SH"
        return f"{code}.SZ"
    return code


def _to_float(v):
    if v is None or v == "" or v is False:
        return None
    try:
        return float(v)
    except Exception:
        return None


def adapt_index_compose_rows(rows: list[dict], include_weight: bool = True) -> list[IndexConstituentItem]:
    items: list[IndexConstituentItem] = []
    for row in rows:
        code = str(row.get("成分券代码") or "").strip()
        symbol = _normalize_symbol(code)
        name = str(row.get("成分券名称") or "")
        exchange = str(row.get("交易所") or "") or None
        weight = _to_float(row.get("权重")) if include_weight else None
        date = str(row.get("日期") or "")[:10] or None
        idx_code = str(row.get("指数代码") or "") or None
        idx_name = str(row.get("指数名称") or "") or None
        items.append(
            IndexConstituentItem(
                symbol=symbol,
                name=name,
                exchange=exchange,
                weight=weight,
                date=date,
                index_code=idx_code,
                index_name=idx_name,
            )
        )
    return items


def build_index_compose_summary(index_code: str, items: list[IndexConstituentItem]) -> IndexComposeSummary:
    index_name = items[0].index_name if items else None
    as_of_date = items[0].date if items else None
    weights = [it.weight for it in items if it.weight is not None]

    total_weight = sum(weights) if weights else None
    sorted_weights = sorted(weights, reverse=True) if weights else []
    top10_weight = sum(sorted_weights[:10]) if sorted_weights else None
    top5_weight = sum(sorted_weights[:5]) if sorted_weights else None
    max_weight = max(sorted_weights) if sorted_weights else None
    min_weight = min(sorted_weights) if sorted_weights else None

    return IndexComposeSummary(
        index_code=index_code,
        index_name=index_name,
        as_of_date=as_of_date,
        constituent_count=len(items),
        total_weight=total_weight,
        top10_weight=top10_weight,
        top5_weight=top5_weight,
        max_weight=max_weight,
        min_weight=min_weight,
    )


def build_index_compose_summary_text(summary: IndexComposeSummary) -> str:
    parts = [f"{summary.index_code}"]
    if summary.index_name:
        parts.append(summary.index_name)
    if summary.as_of_date:
        parts.append(summary.as_of_date)
    parts.append(f"成分股{summary.constituent_count}只")
    if summary.total_weight is not None:
        parts.append(f"总权重{summary.total_weight:.2f}%")
    if summary.top10_weight is not None:
        parts.append(f"前10权重{summary.top10_weight:.2f}%")
    if summary.max_weight is not None:
        parts.append(f"最大权重{summary.max_weight:.2f}%")
    return "，".join(parts)

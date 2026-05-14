from __future__ import annotations

from openclaw_stock_mcp.app.models.index_enhance import IndexEnhanceResult
from openclaw_stock_mcp.app.usecases.index_compose import IndexComposeUseCase
from openclaw_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.adapters.index_enhance_adapters import (
    build_enhance_members,
    build_index_enhance_summary,
    build_index_enhance_summary_text,
    calc_enhanced_return,
    calc_index_return,
    normalize_index_code,
    normalize_stock_symbol,
)


class _HistoryRequest:
    def __init__(self, symbol: str, sec_type: str, interval: str, start_date, end_date, limit: int, adjust):
        self.symbol = symbol
        self.sec_type = sec_type
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.limit = limit
        self.adjust = adjust
        self.provider = None


class _ComposeRequest:
    def __init__(self, index_code: str, top_n: int, include_weight: bool, sort_by: str, descending: bool):
        self.index_code = index_code
        self.top_n = top_n
        self.include_weight = include_weight
        self.sort_by = sort_by
        self.descending = descending


class IndexEnhanceUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.index_compose = IndexComposeUseCase()
        self.stock_history = StockHistoryUseCase()

    def execute(self, request) -> dict:
        index_code = normalize_index_code(request.index_code)
        limit = request.top_n
        weighting = request.weighting

        compose = self.index_compose.execute(_ComposeRequest(
            index_code=index_code,
            top_n=limit,
            include_weight=True,
            sort_by="weight",
            descending=True,
        ))
        constituents = compose.get("items", [])

        index_symbol = self._index_symbol(index_code)
        history = self.stock_history.execute(_HistoryRequest(
            symbol=index_symbol,
            sec_type="index",
            interval="1d",
            start_date=request.start_date,
            end_date=request.end_date,
            limit=1,
            adjust=None,
        ))
        benchmark_return = calc_index_return(history.get("items", []))

        symbols = [normalize_stock_symbol(self._field(c, "symbol"), self._field(c, "exchange")) for c in constituents]
        quotes = self._get_quotes(symbols)
        members = build_enhance_members(constituents, quotes, benchmark_return)
        enhanced_return, total_weight = calc_enhanced_return(members, weighting)
        if weighting == "equal":
            total_weight = None

        summary_obj = compose.get("summary")
        index_name = summary_obj.get("index_name") if isinstance(summary_obj, dict) else None
        summary = build_index_enhance_summary(
            index_code=index_code,
            index_name=index_name,
            benchmark_return=benchmark_return,
            enhanced_return=enhanced_return,
            members=members,
            total_weight=total_weight,
            weighting=weighting,
        )
        summary_text = build_index_enhance_summary_text(summary)

        result = IndexEnhanceResult(summary=summary, members=members, summary_text=summary_text)
        payload = result.model_dump()
        payload["compose_used_fallback_endpoint"] = compose.get("used_fallback_endpoint", False)
        return payload

    def _get_quotes(self, symbols: list[str]) -> dict[str, object]:
        if not symbols:
            return {}
        results: dict[str, object] = {}
        for symbol in symbols:
            selection = self.router.choose_provider(tool_name="stock_quote", symbol=symbol, sec_type="stock")
            for provider_name in [selection.primary, *selection.fallback]:
                provider = self.router.get_provider(provider_name)
                try:
                    quote = provider.get_quote(symbol, "stock")
                    results[quote.symbol] = quote
                    break
                except Exception:
                    continue
        return results

    @staticmethod
    def _field(item, name: str):
        if isinstance(item, dict):
            return item.get(name)
        return getattr(item, name, None)

    @staticmethod
    def _index_symbol(index_code: str) -> str:
        if index_code.startswith(("399", "159")):
            return f"{index_code}.SZ"
        if index_code.startswith("899"):
            return f"{index_code}.BJ"
        return f"{index_code}.SH"

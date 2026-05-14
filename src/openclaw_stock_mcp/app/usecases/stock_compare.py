from __future__ import annotations

from openclaw_stock_mcp.app.models.stock_compare import StockCompareItem, StockCompareResult
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.providers.adapters.akshare_stock_compare_adapters import (
    build_compare_summary,
    merge_dividend,
    merge_financial,
    merge_quote,
    merge_valuation,
)


class StockCompareUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    def execute(self, request) -> dict:
        symbols = request.symbols
        sec_type = getattr(request, "sec_type", "stock")
        include = request.include

        # Resolve all symbols
        resolved_map = {}
        for sym in symbols:
            resolved = self.resolver.resolve(sym, sec_type)
            resolved_map[resolved.symbol] = resolved

        # Initialize items
        items = [StockCompareItem(symbol=sym, name="") for sym in resolved_map]

        # Layer 1: quote (from stock_screen Sina cache — 0 requests if cached)
        if "quote" in include:
            items = self._merge_quote_layer(items)

        # Layer 2: valuation (Zhitu batch — 1 request)
        if "valuation" in include:
            items = self._merge_valuation_layer(items, resolved_map, sec_type)

        # Layer 3: financial (AKShare — N requests)
        if "financial" in include:
            items = self._merge_financial_layer(items, resolved_map)

        # Layer 4: dividend (from dividend_rank cache — 0 requests if cached)
        if "dividend" in include:
            items = self._merge_dividend_layer(items)

        summary = build_compare_summary(items, include)

        result = StockCompareResult(
            items=items,
            total_count=len(items),
            symbols_compared=list(resolved_map.keys()),
            summary=summary,
        )
        return result.model_dump()

    def _merge_quote_layer(self, items: list[StockCompareItem]) -> list[StockCompareItem]:
        """Use stock_screen's Sina spot cache."""
        try:
            from openclaw_stock_mcp.app.usecases.stock_screen import StockScreenUseCase
            screen_uc = StockScreenUseCase()
            raw_rows = screen_uc.spot_cache.get("screen:spot_all")
            if raw_rows is None:
                return items
            result = []
            for item in items:
                matched = False
                for row in raw_rows:
                    merged = merge_quote(item, row)
                    if merged.source_quote:
                        result.append(merged)
                        matched = True
                        break
                if not matched:
                    result.append(item)
            return result
        except Exception:
            return items

    def _merge_valuation_layer(self, items: list[StockCompareItem], resolved_map: dict, sec_type: str) -> list[StockCompareItem]:
        """Use Zhitu batch quote — 1 request for up to 10 symbols."""
        try:
            provider = self.router.get_provider("zhitu")
            symbols_list = list(resolved_map.keys())
            quotes = provider.get_quotes(symbols_list, sec_type=sec_type)
            # quotes is a dict: {orig_symbol: Quote}
            result = []
            for item in items:
                quote = quotes.get(item.symbol)
                if quote is not None:
                    result.append(merge_valuation(item, quote))
                else:
                    result.append(item)
            return result
        except Exception:
            return items

    def _merge_financial_layer(self, items: list[StockCompareItem], resolved_map: dict) -> list[StockCompareItem]:
        """Use AKShare stock_financial_abstract — N requests."""
        try:
            provider = self.router.get_provider("akshare")
            result = []
            for item in items:
                code = item.symbol.split(".", 1)[0]
                try:
                    raw_rows = provider.get_financial_abstract(symbol=code)
                    result.append(merge_financial(item, raw_rows))
                except Exception:
                    result.append(item)
            return result
        except Exception:
            return items

    def _merge_dividend_layer(self, items: list[StockCompareItem]) -> list[StockCompareItem]:
        """Use dividend_rank cache, filter by symbol."""
        try:
            from openclaw_stock_mcp.app.usecases.dividend_rank import DividendRankUseCase
            div_uc = DividendRankUseCase()
            raw_rows = div_uc.rank_cache.get("dividend:history_rank")
            if raw_rows is None:
                return items
            result = []
            for item in items:
                dy = None
                eps = None
                for row in raw_rows:
                    from openclaw_stock_mcp.infra.time_utils import normalize_symbol
                    raw_code = str(row.get("代码", "")).strip()
                    sym = normalize_symbol(raw_code) if raw_code else ""
                    if sym == item.symbol:
                        avg_div = row.get("年均股息")
                        if avg_div is not None and avg_div != "" and str(avg_div) != "NaN":
                            try:
                                dy = float(avg_div)
                            except (TypeError, ValueError):
                                pass
                        break
                result.append(merge_dividend(item, dy, eps))
            return result
        except Exception:
            return items

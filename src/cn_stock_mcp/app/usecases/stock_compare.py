from __future__ import annotations

from collections.abc import Mapping, Sequence

from cn_stock_mcp.app.models.stock_compare import StockCompareItem, StockCompareResult
from cn_stock_mcp.app.services.error_mapper import serialize_exception
from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.app.services.symbol_resolver import SymbolResolver
from cn_stock_mcp.providers.adapters.akshare_stock_compare_adapters import (
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

        resolved_map = {}
        errors: list[dict] = []
        for sym in symbols:
            try:
                resolved = self.resolver.resolve(sym, sec_type)
                resolved_map[resolved.symbol] = resolved
            except Exception as exc:
                errors.append({"symbol": sym, **serialize_exception(exc)})

        items = [StockCompareItem(symbol=sym, name="") for sym in resolved_map]
        layer_meta: dict = {}

        if "quote" in include:
            items, layer_errors, layer_info = self._merge_quote_layer(items, resolved_map, sec_type)
            errors.extend(layer_errors)
            layer_meta["quote"] = layer_info

        if "valuation" in include:
            items, layer_errors, layer_info = self._merge_valuation_layer(
                items, resolved_map, sec_type, getattr(request, "provider", None)
            )
            errors.extend(layer_errors)
            layer_meta["valuation"] = layer_info

        if "financial" in include:
            items, layer_errors = self._merge_financial_layer(items)
            errors.extend(layer_errors)
            layer_meta["financial"] = {"provider": "akshare"}

        if "dividend" in include:
            items, layer_errors, layer_info = self._merge_dividend_layer(items)
            errors.extend(layer_errors)
            layer_meta["dividend"] = layer_info

        result = StockCompareResult(
            items=items,
            total_count=len(items),
            symbols_compared=list(resolved_map.keys()),
            summary=build_compare_summary(items, include),
            partial_failure=bool(errors),
            errors=errors,
            meta={"layers": layer_meta},
        )
        return result.model_dump()

    def _merge_quote_layer(
        self,
        items: list[StockCompareItem],
        resolved_map: dict,
        sec_type: str,
    ) -> tuple[list[StockCompareItem], list[dict], dict]:
        """Use the shared Sina cache, then fetch symbols missing from it."""

        errors: list[dict] = []
        cached_count = 0
        fetched_count = 0
        try:
            from cn_stock_mcp.app.usecases.stock_screen import StockScreenUseCase

            raw_rows = StockScreenUseCase().spot_cache.get("screen:spot_all") or []
        except Exception as exc:
            raw_rows = []
            errors.append({"layer": "quote", **serialize_exception(exc)})

        result: list[StockCompareItem] = []
        for item in items:
            merged_item = item
            for row in raw_rows:
                candidate = merge_quote(item, row)
                if candidate.source_quote:
                    merged_item = candidate
                    cached_count += 1
                    break
            result.append(merged_item)

        # Cache misses previously became silent empty successes. Fetch each
        # missing symbol through the regular fallback chain instead.
        for index, item in enumerate(result):
            if item.source_quote:
                continue
            try:
                resolved = resolved_map.get(item.symbol)
                symbol_sec_type = getattr(resolved, "sec_type", sec_type)
                selection = self.router.choose_provider(
                    "stock_quote", symbol=item.symbol, sec_type=symbol_sec_type
                )
                quote, _meta = run_with_fallback_meta(
                    self.router,
                    selection,
                    lambda provider, symbol=item.symbol, st=symbol_sec_type: provider.get_quote(symbol, st),
                )
                merged_item = merge_quote(item, quote)
                result[index] = merged_item
                if merged_item.source_quote:
                    fetched_count += 1
                else:
                    errors.append(
                        {
                            "layer": "quote",
                            "symbol": item.symbol,
                            "error_code": "PARTIAL_RESULT",
                            "message": "quote provider returned an unusable result",
                            "retryable": True,
                        }
                    )
            except Exception as exc:
                errors.append({"layer": "quote", "symbol": item.symbol, **serialize_exception(exc)})

        return result, errors, {"cached": cached_count, "fetched": fetched_count}

    def _merge_valuation_layer(
        self,
        items: list[StockCompareItem],
        resolved_map: dict,
        sec_type: str,
        preferred: str | None = None,
    ) -> tuple[list[StockCompareItem], list[dict], dict]:
        """Fetch valuation quotes through the declared route and fallback."""

        errors: list[dict] = []
        symbols_list = list(resolved_map.keys())
        try:
            selection = self.router.choose_provider(
                "stock_compare", sec_type=sec_type, preferred=preferred
            )
            quotes, fallback_meta = run_with_fallback_meta(
                self.router,
                selection,
                lambda provider: provider.get_quotes(symbols_list, sec_type=sec_type),
                should_fallback_result=lambda value: not self._quote_sequence(value),
            )
            quote_map = self._quote_map(quotes)
            result: list[StockCompareItem] = []
            for item in items:
                quote = quote_map.get(item.symbol)
                if quote is None:
                    result.append(item)
                    errors.append(
                        {
                            "layer": "valuation",
                            "symbol": item.symbol,
                            "error_code": "PARTIAL_RESULT",
                            "message": "symbol missing from valuation provider result",
                            "retryable": True,
                        }
                    )
                else:
                    result.append(merge_valuation(item, quote, source=fallback_meta.final_provider))
            return result, errors, {
                "selected_primary": fallback_meta.selected_primary,
                "selected_fallback": fallback_meta.selected_fallback,
                "attempted": fallback_meta.attempted,
                "final_provider": fallback_meta.final_provider,
                "used_fallback": fallback_meta.used_fallback,
            }
        except Exception as exc:
            errors.append({"layer": "valuation", **serialize_exception(exc)})
            return items, errors, {}

    def _merge_financial_layer(self, items: list[StockCompareItem]) -> tuple[list[StockCompareItem], list[dict]]:
        """Fetch the current tuple-based AKShare financial contract."""

        errors: list[dict] = []
        try:
            provider = self.router.get_provider("akshare")
        except Exception as exc:
            return items, [{"layer": "financial", **serialize_exception(exc)}]

        result: list[StockCompareItem] = []
        for item in items:
            code = item.symbol.split(".", 1)[0]
            try:
                raw_result = provider.get_financial_abstract(symbol=code)
                merged = merge_financial(item, raw_result)
                result.append(merged)
                if not merged.source_financial:
                    errors.append(
                        {
                            "layer": "financial",
                            "symbol": item.symbol,
                            "error_code": "PARTIAL_RESULT",
                            "message": "financial provider returned no usable metrics",
                            "retryable": True,
                        }
                    )
            except Exception as exc:
                result.append(item)
                errors.append({"layer": "financial", "symbol": item.symbol, **serialize_exception(exc)})
        return result, errors

    @staticmethod
    def _quote_sequence(value) -> list:
        if isinstance(value, Mapping):
            return list(value.values())
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return list(value)
        return []

    @classmethod
    def _quote_map(cls, value) -> dict[str, object]:
        from cn_stock_mcp.infra.time_utils import normalize_symbol

        result: dict[str, object] = {}
        for quote in cls._quote_sequence(value):
            symbol = quote.get("symbol") if isinstance(quote, Mapping) else getattr(quote, "symbol", None)
            if not symbol:
                continue
            try:
                normalized = normalize_symbol(str(symbol))
            except Exception:
                normalized = str(symbol)
            result[normalized] = quote
        return result

    def _merge_dividend_layer(self, items: list[StockCompareItem]) -> tuple[list[StockCompareItem], list[dict], dict]:
        """Use dividend_rank cache, filter by symbol."""

        try:
            from cn_stock_mcp.app.usecases.dividend_rank import DividendRankUseCase

            raw_rows = DividendRankUseCase().rank_cache.get("dividend:history_rank")
            if raw_rows is None:
                return items, [
                    {
                        "layer": "dividend",
                        "error_code": "PARTIAL_RESULT",
                        "message": "dividend cache is not warmed; call dividend_rank first",
                        "retryable": True,
                    }
                ], {"cache_hit": False}
            result = []
            errors: list[dict] = []
            for item in items:
                dy = None
                eps = None
                for row in raw_rows:
                    from cn_stock_mcp.infra.time_utils import normalize_symbol

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
                if dy is None:
                    errors.append(
                        {
                            "layer": "dividend",
                            "symbol": item.symbol,
                            "error_code": "PARTIAL_RESULT",
                            "message": "symbol missing from dividend cache",
                            "retryable": True,
                        }
                    )
            return result, errors, {"cache_hit": True, "row_count": len(raw_rows)}
        except Exception as exc:
            return items, [{"layer": "dividend", **serialize_exception(exc)}], {"cache_hit": False}

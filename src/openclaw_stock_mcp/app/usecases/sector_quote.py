from __future__ import annotations

import time

from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver


class SectorQuoteUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    @staticmethod
    def _filter_items(
        items: list,
        min_turnover: float | None,
        min_change_percent: float | None,
        exclude_null_fields: bool,
        sort_by: str | None,
    ):
        filtered = []
        for item in items:
            turnover = getattr(item, "turnover", None)
            change_percent = getattr(item, "change_percent", None)

            if min_turnover is not None:
                if turnover is None or turnover < min_turnover:
                    continue
            if min_change_percent is not None:
                if change_percent is None or change_percent < min_change_percent:
                    continue
            if exclude_null_fields and sort_by in {"turnover", "change_percent"}:
                if getattr(item, sort_by, None) is None:
                    continue
            filtered.append(item)
        return filtered

    @staticmethod
    def _sort_items(items: list, sort_by: str | None, descending: bool):
        if sort_by not in {"change_percent", "turnover"}:
            return items

        def _key(item):
            value = getattr(item, sort_by, None)
            return value if value is not None else float("-inf")

        return sorted(items, key=_key, reverse=descending)

    def execute(self, request):
        items = []
        errors = []
        meta_items = []

        for raw_symbol in request.symbols:
            symbol_started_at = time.perf_counter()
            try:
                resolved = self.resolver.resolve(raw_symbol, "sector")
                selection = self.router.choose_provider(
                    tool_name="sector_quote",
                    symbol=resolved.symbol,
                    sec_type="sector",
                    preferred=getattr(request, "provider", None),
                )
                quote, fallback_meta = run_with_fallback_meta(
                    self.router,
                    selection,
                    lambda provider: provider.get_sector_quote(resolved.symbol, getattr(request, "sector_type", None)),
                )
                items.append(quote)
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": resolved.symbol,
                        "selected_primary": fallback_meta.selected_primary,
                        "selected_fallback": fallback_meta.selected_fallback,
                        "attempted": fallback_meta.attempted,
                        "final_provider": fallback_meta.final_provider,
                        "used_fallback": fallback_meta.used_fallback,
                        "provider_used": fallback_meta.final_provider or selection.primary,
                        "fallback_chain": [selection.primary, *selection.fallback],
                        "latency_ms": int((time.perf_counter() - symbol_started_at) * 1000),
                    }
                )
            except Exception as exc:
                from openclaw_stock_mcp.app.services.error_mapper import serialize_exception

                errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": None,
                        "selected_primary": None,
                        "selected_fallback": None,
                        "attempted": [],
                        "final_provider": None,
                        "used_fallback": False,
                        "provider_used": None,
                        "fallback_chain": [],
                        "latency_ms": int((time.perf_counter() - symbol_started_at) * 1000),
                    }
                )

        sort_by = getattr(request, "sort_by", None)
        descending = bool(getattr(request, "descending", True))
        top_n = getattr(request, "top_n", None)
        min_turnover = getattr(request, "min_turnover", None)
        min_change_percent = getattr(request, "min_change_percent", None)
        exclude_null_fields = bool(getattr(request, "exclude_null_fields", False))
        return_mode = getattr(request, "return_mode", "full")

        filtered_items = self._filter_items(
            items=items,
            min_turnover=min_turnover,
            min_change_percent=min_change_percent,
            exclude_null_fields=exclude_null_fields,
            sort_by=sort_by,
        )
        sorted_items = self._sort_items(filtered_items, sort_by, descending)
        ranked_items = sorted_items[:top_n] if top_n is not None else sorted_items

        output_items = ranked_items if return_mode == "ranked_only" else sorted_items

        return {
            "items": output_items,
            "partial_failure": len(errors) > 0,
            "errors": errors,
            "meta": {
                "per_symbol": meta_items,
                "sort_by": sort_by,
                "descending": descending,
                "top_n": top_n,
                "min_turnover": min_turnover,
                "min_change_percent": min_change_percent,
                "exclude_null_fields": exclude_null_fields,
                "return_mode": return_mode,
                "filtered_from": len(items),
                "filtered_count": len(filtered_items),
                "ranked_count": len(ranked_items),
                "provider_used": sorted({m.get("provider_used") for m in meta_items if m.get("provider_used")}),
                "fallback_chain": sorted({tuple(m.get("fallback_chain", [])) for m in meta_items if m.get("fallback_chain")}),
                "latency_ms": sum(int(m.get("latency_ms") or 0) for m in meta_items),
            },
        }

import time

from cn_stock_mcp.app.services.cache_service import CacheService
from cn_stock_mcp.app.services.error_mapper import serialize_exception
from cn_stock_mcp.app.services.fallback import run_with_fallback_meta
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.app.services.provider_types import ProviderSelection
from cn_stock_mcp.app.services.symbol_resolver import SymbolResolver
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.errors import ProviderError


class StockQuoteUseCase:
    _shared_quote_cache: CacheService | None = None

    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()
        settings = get_settings()
        if StockQuoteUseCase._shared_quote_cache is None:
            StockQuoteUseCase._shared_quote_cache = CacheService(
                maxsize=4096, ttl=max(int(settings.cache_ttl_quote_seconds or 10), 1)
            )
        self.quote_cache = StockQuoteUseCase._shared_quote_cache

    def _selection_from_preference(self, preferences: list[str] | None) -> ProviderSelection | None:
        if not preferences:
            return None
        ordered = [p for p in preferences if p in {"akshare", "zhitu"}]
        if not ordered:
            return None
        primary = ordered[0]
        fallback = [p for p in ordered[1:] if p != primary]
        return ProviderSelection(primary=primary, fallback=fallback)

    def _validate_symbol_sec_type(self, raw_symbol: str, requested_sec_type: str | None):
        if not requested_sec_type:
            return
        inferred_sec_type = self.resolver.infer_sec_type(raw_symbol)
        if inferred_sec_type != requested_sec_type:
            raise ProviderError(
                "INVALID_ARGUMENT",
                f"Symbol {raw_symbol} is inferred as {inferred_sec_type}, which conflicts with requested sec_type={requested_sec_type}",
                retryable=False,
            )

    def _can_use_batch(self, symbols: list[str], sec_type: str | None, selection: ProviderSelection) -> bool:
        if selection.primary != "zhitu":
            return False
        if sec_type and sec_type != "stock":
            return False
        if len(symbols) < 2:
            return False
        for sym in symbols:
            resolved = self.resolver.resolve(sym, sec_type or "stock")
            normalized = resolved.symbol.upper()
            code = normalized.split(".", 1)[0]
            exchange = normalized.split(".", 1)[1] if "." in normalized else None
            if resolved.sec_type != "stock":
                return False
            if normalized.endswith(".BJ"):
                return False
            if code.startswith("688"):
                return False
            if exchange not in {"SH", "SZ"}:
                return False
        return True

    def execute(self, request):
        started_at = time.perf_counter()
        items = []
        errors = []
        meta_items = []
        forced_selection = self._selection_from_preference(getattr(request, "provider_preference", None))

        resolved_symbols = []
        for raw_symbol in request.symbols:
            try:
                self._validate_symbol_sec_type(raw_symbol, request.sec_type)
                resolved = self.resolver.resolve(raw_symbol, request.sec_type)
                resolved_symbols.append((raw_symbol, resolved))
            except Exception as exc:
                errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                meta_items.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": None,
                        "sec_type": request.sec_type,
                        "selected_primary": None,
                        "selected_fallback": None,
                        "attempted": [],
                        "final_provider": None,
                        "used_fallback": False,
                        "provider_used": None,
                        "fallback_chain": [],
                        "latency_ms": 0,
                    }
                )

        if not resolved_symbols:
            return {
                "items": items,
                "partial_failure": len(errors) > 0,
                "errors": errors,
                "meta": {"per_symbol": meta_items},
            }

        first_resolved = resolved_symbols[0][1]
        selection = forced_selection or self.router.choose_provider(
            tool_name="stock_quote",
            symbol=first_resolved.symbol,
            sec_type=first_resolved.sec_type,
            preferred=getattr(request, "provider", None),
        )

        if self._can_use_batch([sym for sym, _ in resolved_symbols], request.sec_type, selection):
            try:
                provider = self.router.get_provider(selection.primary)
                if hasattr(provider, "get_quotes_with_meta"):
                    quotes, batch_meta = provider.get_quotes_with_meta([sym for sym, _ in resolved_symbols], request.sec_type)
                else:
                    quotes = provider.get_quotes([sym for sym, _ in resolved_symbols], request.sec_type)
                    batch_meta = getattr(provider, "last_batch_meta", None) or {}

                quote_by_symbol = {q.symbol: q for q in quotes}
                for raw_symbol, resolved in resolved_symbols:
                    quote = quote_by_symbol.get(resolved.symbol)
                    symbol_batch_meta = (batch_meta.get("per_symbol") or {}).get(raw_symbol, {}) if isinstance(batch_meta, dict) else {}
                    if quote is not None:
                        items.append(quote)
                        meta_items.append(
                            {
                                "symbol": raw_symbol,
                                "resolved_symbol": resolved.symbol,
                                "sec_type": resolved.sec_type,
                                "selected_primary": selection.primary,
                                "selected_fallback": selection.fallback,
                                "attempted": [selection.primary],
                                "final_provider": selection.primary,
                                "used_fallback": False,
                                "provider_used": selection.primary,
                                "fallback_chain": [selection.primary, *selection.fallback],
                                "latency_ms": 0,
                                "batch_attempted": bool(batch_meta.get("batch_attempted")) if isinstance(batch_meta, dict) else True,
                                "batch_failed": bool(symbol_batch_meta.get("batch_failed")),
                                "batch_fallback_used": bool(symbol_batch_meta.get("batch_fallback_used")) if isinstance(batch_meta, dict) else False,
                                "batch_fallback_mode": symbol_batch_meta.get("batch_fallback_mode"),
                                "batch_error": symbol_batch_meta.get("batch_error"),
                            }
                        )
                    else:
                        err = symbol_batch_meta.get("batch_error") or {
                            "error_code": "PARTIAL_RESULT",
                            "message": "symbol missing from batch result",
                            "retryable": True,
                        }
                        errors.append({"symbol": raw_symbol, **err})
                        meta_items.append(
                            {
                                "symbol": raw_symbol,
                                "resolved_symbol": resolved.symbol,
                                "sec_type": resolved.sec_type,
                                "selected_primary": selection.primary,
                                "selected_fallback": selection.fallback,
                                "attempted": [selection.primary],
                                "final_provider": None,
                                "used_fallback": False,
                                "provider_used": None,
                                "fallback_chain": [selection.primary, *selection.fallback],
                                "latency_ms": 0,
                                "batch_attempted": bool(batch_meta.get("batch_attempted")) if isinstance(batch_meta, dict) else True,
                                "batch_failed": True,
                                "batch_fallback_used": bool(symbol_batch_meta.get("batch_fallback_used")) if isinstance(batch_meta, dict) else False,
                                "batch_fallback_mode": symbol_batch_meta.get("batch_fallback_mode"),
                                "batch_error": err,
                            }
                        )
            except Exception as exc:
                for raw_symbol, resolved in resolved_symbols:
                    errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                    meta_items.append(
                        {
                            "symbol": raw_symbol,
                            "resolved_symbol": resolved.symbol,
                            "sec_type": resolved.sec_type,
                            "selected_primary": selection.primary,
                            "selected_fallback": selection.fallback,
                            "attempted": [selection.primary],
                            "final_provider": None,
                            "used_fallback": False,
                            "provider_used": None,
                            "fallback_chain": [selection.primary, *selection.fallback],
                            "latency_ms": 0,
                        }
                    )
        else:
            for raw_symbol, resolved in resolved_symbols:
                sym_selection = forced_selection or self.router.choose_provider(
                    tool_name="stock_quote",
                    symbol=resolved.symbol,
                    sec_type=resolved.sec_type,
                    preferred=getattr(request, "provider", None),
                )
                # Check cache for individual quote
                cache_key = f"quote:{resolved.symbol}:{resolved.sec_type}"
                cached = self.quote_cache.get(cache_key)
                if cached is not None:
                    items.append(cached)
                    meta_items.append(
                        {
                            "symbol": raw_symbol,
                            "resolved_symbol": resolved.symbol,
                            "sec_type": resolved.sec_type,
                            "selected_primary": sym_selection.primary,
                            "selected_fallback": sym_selection.fallback,
                            "attempted": [],
                            "final_provider": "cache",
                            "used_fallback": False,
                            "provider_used": "cache",
                            "fallback_chain": [sym_selection.primary, *sym_selection.fallback],
                            "latency_ms": 0,
                        }
                    )
                    continue

                try:
                    quote, fallback_meta = run_with_fallback_meta(
                        self.router,
                        sym_selection,
                        lambda provider: provider.get_quote(resolved.symbol, resolved.sec_type),
                    )
                    items.append(quote)
                    self.quote_cache.set(cache_key, quote)
                    meta_items.append(
                        {
                            "symbol": raw_symbol,
                            "resolved_symbol": resolved.symbol,
                            "sec_type": resolved.sec_type,
                            "selected_primary": fallback_meta.selected_primary,
                            "selected_fallback": fallback_meta.selected_fallback,
                            "attempted": fallback_meta.attempted,
                            "final_provider": fallback_meta.final_provider,
                            "used_fallback": fallback_meta.used_fallback,
                            "provider_used": fallback_meta.final_provider or sym_selection.primary,
                            "fallback_chain": [sym_selection.primary, *sym_selection.fallback],
                            "latency_ms": 0,
                        }
                    )
                except Exception as exc:
                    errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                    meta_items.append(
                        {
                            "symbol": raw_symbol,
                            "resolved_symbol": resolved.symbol,
                            "sec_type": resolved.sec_type,
                            "selected_primary": sym_selection.primary,
                            "selected_fallback": sym_selection.fallback,
                            "attempted": [sym_selection.primary, *sym_selection.fallback],
                            "final_provider": None,
                            "used_fallback": False,
                            "provider_used": None,
                            "fallback_chain": [sym_selection.primary, *sym_selection.fallback],
                            "latency_ms": 0,
                        }
                    )

        return {
            "items": items,
            "partial_failure": len(errors) > 0,
            "errors": errors,
            "meta": {
                "per_symbol": meta_items,
                "provider_used": sorted({m.get("provider_used") for m in meta_items if m.get("provider_used")}),
                "fallback_chain": sorted({tuple(m.get("fallback_chain", [])) for m in meta_items if m.get("fallback_chain")}),
                "batch": {
                    "attempted": any(m.get("batch_attempted") for m in meta_items),
                    "failed": any(m.get("batch_failed") for m in meta_items),
                    "fallback_used": any(m.get("batch_fallback_used") for m in meta_items),
                    "fallback_mode": next((m.get("batch_fallback_mode") for m in meta_items if m.get("batch_fallback_mode")), None),
                    "failed_symbols": [m.get("symbol") for m in meta_items if m.get("batch_failed")],
                },
                "latency_ms": int((time.perf_counter() - started_at) * 1000),
            },
        }

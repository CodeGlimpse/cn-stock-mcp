from __future__ import annotations

import time
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any

from pydantic import BaseModel

from cn_stock_mcp.app.services.error_mapper import serialize_exception
from cn_stock_mcp.app.services.symbol_resolver import SymbolResolver
from cn_stock_mcp.app.usecases.stock_financial import StockFinancialUseCase
from cn_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from cn_stock_mcp.app.usecases.stock_profile import StockProfileUseCase
from cn_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase
from cn_stock_mcp.server.schemas import (
    StockFinancialRequest,
    StockHistoryRequest,
    StockProfileRequest,
    StockQuoteRequest,
)


class StockSnapshotUseCase:
    """Bounded composition of existing stock data use cases."""

    MAX_SYMBOLS = 5
    MAX_WORKERS = 3

    def __init__(self) -> None:
        self.resolver = SymbolResolver()
        self.quote = StockQuoteUseCase()
        self.history = StockHistoryUseCase()
        self.financial = StockFinancialUseCase()
        self.profile = StockProfileUseCase()

    @staticmethod
    def _to_dict(value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.model_dump(mode="python")
        if isinstance(value, dict):
            return {key: StockSnapshotUseCase._to_dict(child) for key, child in value.items()}
        if isinstance(value, list):
            return [StockSnapshotUseCase._to_dict(child) for child in value]
        return value

    @staticmethod
    def _error(symbol: str, section: str, exc: Exception | dict[str, Any]) -> dict[str, Any]:
        detail = serialize_exception(exc) if isinstance(exc, Exception) else dict(exc)
        return {"symbol": symbol, "section": section, **detail}

    @staticmethod
    def _timeout_error(symbol: str, section: str) -> dict[str, Any]:
        return {
            "symbol": symbol,
            "section": section,
            "error_code": "PROVIDER_TIMEOUT",
            "message": "stock_snapshot total timeout budget was exceeded",
            "retryable": True,
        }

    def _profile_sections(self, include: set[str]) -> set[str]:
        sections = set()
        if "valuation" in include:
            sections.add("valuation")
        if "events" in include:
            sections.add("events")
        if "risk" in include:
            sections.add("risk")
        return sections

    def _load_symbol_sections(self, raw_symbol: str, resolved_symbol: str, request, include: set[str]) -> dict[str, Any]:
        sections: dict[str, Any] = {}
        errors: list[dict[str, Any]] = []

        if "history" in include:
            try:
                history = self.history.execute(
                    StockHistoryRequest(
                        symbol=resolved_symbol,
                        interval=request.history_interval,
                        sec_type=request.sec_type,
                        limit=request.history_limit,
                        adjust=request.adjust,
                        provider=request.provider,
                    )
                )
                sections["history"] = {
                    "interval": history.get("interval"),
                    "items": self._to_dict(history.get("items", [])),
                    "count": history.get("count", 0),
                    "source": history.get("source"),
                    "meta": history.get("meta", {}),
                }
            except Exception as exc:
                errors.append(self._error(raw_symbol, "history", exc))

        if "financial" in include:
            try:
                financial = self.financial.execute(
                    StockFinancialRequest(
                        symbol=resolved_symbol,
                        include=["snapshot", "history"],
                        history_n=4,
                    )
                )
                sections["financial"] = {
                    "snapshot": self._to_dict(financial.get("snapshot")),
                    "history": self._to_dict(financial.get("history", [])),
                    "summary": financial.get("summary"),
                    "source": financial.get("source"),
                }
            except Exception as exc:
                errors.append(self._error(raw_symbol, "financial", exc))

        profile_sections = self._profile_sections(include)
        if profile_sections:
            profile_include = ["profile"]
            if "valuation" in profile_sections:
                profile_include.append("valuation")
            if "events" in profile_sections:
                profile_include.extend(["dividends", "unlocks", "profits"])
            elif "risk" in profile_sections:
                profile_include.append("unlocks")
            try:
                profile = self.profile.execute(
                    StockProfileRequest(
                        symbol=resolved_symbol,
                        include=list(dict.fromkeys(profile_include)),
                        provider="zhitu",
                    )
                )
                if "valuation" in profile_sections:
                    sections["valuation"] = profile.get("valuation")
                if "events" in profile_sections:
                    sections["events"] = {
                        "dividends": profile.get("dividends", []),
                        "unlocks": profile.get("unlocks", []),
                        "quarter_profits": profile.get("quarter_profits", []),
                    }
                if "risk" in profile_sections:
                    unlock_risk = profile.get("unlock_risk")
                    risk_tags = []
                    if unlock_risk and unlock_risk.get("has_future_unlock"):
                        risk_tags.append("future_unlock")
                    if unlock_risk is None:
                        risk_tags.append("risk_data_unavailable")
                    sections["risk"] = {
                        "unlock_risk": unlock_risk,
                        "risk_tags": risk_tags,
                    }
            except Exception as exc:
                for section in sorted(profile_sections):
                    errors.append(self._error(raw_symbol, section, exc))

        return {"sections": sections, "errors": errors}

    def execute(self, request) -> dict[str, Any]:
        started_at = time.perf_counter()
        include = set(request.include)
        deadline = time.monotonic() + request.max_total_timeout_seconds
        items = [
            {
                "symbol": raw_symbol,
                "resolved_symbol": None,
                "quote": None,
                "history": None,
                "financial": None,
                "valuation": None,
                "events": None,
                "risk": None,
                "errors": [],
            }
            for raw_symbol in request.symbols
        ]
        top_errors: list[dict[str, Any]] = []
        resolved_items: list[tuple[int, str, str]] = []

        for index, raw_symbol in enumerate(request.symbols):
            try:
                resolved = self.resolver.resolve(raw_symbol, request.sec_type)
                items[index]["resolved_symbol"] = resolved.symbol
                resolved_items.append((index, raw_symbol, resolved.symbol))
            except Exception as exc:
                error = self._error(raw_symbol, "resolve", exc)
                items[index]["errors"].append(error)
                top_errors.append(error)

        executor = ThreadPoolExecutor(
            max_workers=min(self.MAX_WORKERS, max(1, len(resolved_items))),
            thread_name_prefix="stock-snapshot",
        )
        timed_out = False
        try:
            if "quote" in include and resolved_items and time.monotonic() < deadline:
                quote_future = executor.submit(
                    self.quote.execute,
                    StockQuoteRequest(
                        symbols=[raw for _, raw, _ in resolved_items],
                        sec_type=request.sec_type,
                        provider=request.provider,
                    ),
                )
                try:
                    quote_result = quote_future.result(timeout=max(0, deadline - time.monotonic()))
                    quote_by_symbol = {
                        self._to_dict(quote).get("symbol"): self._to_dict(quote)
                        for quote in quote_result.get("items", [])
                    }
                    quote_errors = {
                        error.get("symbol"): error
                        for error in quote_result.get("errors", [])
                        if isinstance(error, dict)
                    }
                    for index, raw_symbol, resolved_symbol in resolved_items:
                        quote = quote_by_symbol.get(resolved_symbol)
                        if quote is not None:
                            items[index]["quote"] = quote
                        else:
                            error = quote_errors.get(raw_symbol) or {
                                "symbol": raw_symbol,
                                "section": "quote",
                                "error_code": "PARTIAL_RESULT",
                                "message": "quote was not returned for the requested symbol",
                                "retryable": True,
                            }
                            error = {**error, "section": "quote"}
                            items[index]["errors"].append(error)
                            top_errors.append(error)
                except FuturesTimeoutError:
                    timed_out = True
                    quote_future.cancel()
                    for index, raw_symbol, _ in resolved_items:
                        error = self._timeout_error(raw_symbol, "quote")
                        items[index]["errors"].append(error)
                        top_errors.append(error)
            elif "quote" in include:
                timed_out = True
                for _, raw_symbol, _ in resolved_items:
                    error = self._timeout_error(raw_symbol, "quote")
                    top_errors.append(error)

            section_futures: list[tuple[int, Future]] = []
            for index, raw_symbol, resolved_symbol in resolved_items:
                if time.monotonic() >= deadline:
                    timed_out = True
                    error = self._timeout_error(raw_symbol, "snapshot")
                    items[index]["errors"].append(error)
                    top_errors.append(error)
                    continue
                section_futures.append(
                    (
                        index,
                        executor.submit(
                            self._load_symbol_sections,
                            raw_symbol,
                            resolved_symbol,
                            request,
                            include,
                        ),
                    )
                )

            for index, future in section_futures:
                raw_symbol = items[index]["symbol"]
                try:
                    loaded = future.result(timeout=max(0, deadline - time.monotonic()))
                    for section, value in loaded["sections"].items():
                        items[index][section] = value
                    items[index]["errors"].extend(loaded["errors"])
                    top_errors.extend(loaded["errors"])
                except FuturesTimeoutError:
                    timed_out = True
                    future.cancel()
                    error = self._timeout_error(raw_symbol, "snapshot")
                    items[index]["errors"].append(error)
                    top_errors.append(error)
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        missing_fields = []
        for item in items:
            for section in include:
                if item.get(section) is None:
                    missing_fields.append(f"{item['symbol']}.{section}")

        successful_items = sum(1 for item in items if not item["errors"])
        return {
            "symbols": request.symbols,
            "items": items,
            "count": len(items),
            "reviewed_count": successful_items,
            "partial_failure": bool(top_errors),
            "errors": top_errors,
            "meta": {
                "requested_sections": sorted(include),
                "history_interval": request.history_interval,
                "history_limit": request.history_limit,
                "max_total_timeout_seconds": request.max_total_timeout_seconds,
                "timed_out": timed_out,
                "missing_fields": missing_fields,
                "latency_ms": int((time.perf_counter() - started_at) * 1000),
                "transaction_support": False,
            },
        }

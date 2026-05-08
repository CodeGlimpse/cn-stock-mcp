from __future__ import annotations

from datetime import date as dt_date

from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver


class EventCalendarUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()
        self.resolver = SymbolResolver()

    @staticmethod
    def _priority_rank(event_type: str, event_priority: list[str]) -> int:
        try:
            return event_priority.index(event_type)
        except ValueError:
            return len(event_priority) + 99

    @staticmethod
    def _in_range(value: str | None, start_date: str | None, end_date: str | None) -> bool:
        if not value:
            return False
        try:
            d = dt_date.fromisoformat(value)
        except Exception:
            return False
        if start_date:
            if d < dt_date.fromisoformat(start_date):
                return False
        if end_date:
            if d > dt_date.fromisoformat(end_date):
                return False
        return True

    def execute(self, request):
        event_types = set(getattr(request, "event_types", None) or ["dividend", "unlock", "profit"])
        next_event_only = bool(getattr(request, "next_event_only", False))
        event_priority = list(getattr(request, "event_priority", None) or ["unlock", "dividend", "profit"])
        today_iso = dt_date.today().isoformat()
        errors = []
        items = []
        per_symbol = []

        for raw_symbol in request.symbols:
            try:
                resolved = self.resolver.resolve(raw_symbol, "stock")
                selection = self.router.choose_provider(
                    tool_name="event_calendar",
                    symbol=resolved.symbol,
                    sec_type="stock",
                    preferred=getattr(request, "provider", None),
                )
                include = ["profile"]
                if "dividend" in event_types:
                    include.append("dividends")
                if "unlock" in event_types:
                    include.append("unlocks")
                if "profit" in event_types:
                    include.append("profits")

                detail, fallback_meta = run_with_fallback_meta(
                    self.router,
                    selection,
                    lambda provider: provider.get_profile(resolved.symbol, include=include),
                )

                symbol_events = []
                if "dividend" in event_types:
                    for d in detail.dividends:
                        date_val = d.ex_dividend_date or d.record_date or d.announce_date
                        if self._in_range(date_val, request.start_date, request.end_date):
                            symbol_events.append(
                                {
                                    "symbol": resolved.symbol,
                                    "name": detail.profile.name,
                                    "event_type": "dividend",
                                    "event_date": date_val,
                                    "announce_date": d.announce_date,
                                    "record_date": d.record_date,
                                    "progress": d.progress,
                                    "payload": d.model_dump(),
                                }
                            )

                if "unlock" in event_types:
                    for u in detail.unlocks:
                        if self._in_range(u.unlock_date, request.start_date, request.end_date):
                            symbol_events.append(
                                {
                                    "symbol": resolved.symbol,
                                    "name": detail.profile.name,
                                    "event_type": "unlock",
                                    "event_date": u.unlock_date,
                                    "announce_date": u.announce_date,
                                    "record_date": None,
                                    "progress": None,
                                    "payload": u.model_dump(),
                                }
                            )

                if "profit" in event_types:
                    for p in detail.quarter_profits:
                        if self._in_range(p.period, request.start_date, request.end_date):
                            symbol_events.append(
                                {
                                    "symbol": resolved.symbol,
                                    "name": detail.profile.name,
                                    "event_type": "profit",
                                    "event_date": p.period,
                                    "announce_date": None,
                                    "record_date": None,
                                    "progress": None,
                                    "payload": p.model_dump(),
                                }
                            )

                symbol_events.sort(key=lambda x: x.get("event_date") or "")
                if next_event_only:
                    future_events = [e for e in symbol_events if (e.get("event_date") or "") >= today_iso]
                    if future_events:
                        nearest_date = min((e.get("event_date") or "") for e in future_events)
                        nearest_same_day = [e for e in future_events if (e.get("event_date") or "") == nearest_date]
                        nearest_same_day.sort(key=lambda e: self._priority_rank(e.get("event_type") or "", event_priority))
                        symbol_events = nearest_same_day[:1]
                    else:
                        symbol_events = []
                items.extend(symbol_events)
                per_symbol.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": resolved.symbol,
                        "selected_primary": fallback_meta.selected_primary,
                        "selected_fallback": fallback_meta.selected_fallback,
                        "attempted": fallback_meta.attempted,
                        "final_provider": fallback_meta.final_provider,
                        "used_fallback": fallback_meta.used_fallback,
                        "provider_used": fallback_meta.final_provider or selection.primary,
                    }
                )
            except Exception as exc:
                errors.append({"symbol": raw_symbol, **serialize_exception(exc)})
                per_symbol.append(
                    {
                        "symbol": raw_symbol,
                        "resolved_symbol": None,
                        "selected_primary": None,
                        "selected_fallback": None,
                        "attempted": [],
                        "final_provider": None,
                        "used_fallback": False,
                        "provider_used": None,
                    }
                )

        items.sort(key=lambda x: (x.get("event_date") or "", x.get("symbol") or ""))

        return {
            "items": items,
            "count": len(items),
            "partial_failure": len(errors) > 0,
            "errors": errors,
            "meta": {
                "per_symbol": per_symbol,
                "event_types": sorted(event_types),
                "start_date": request.start_date,
                "end_date": request.end_date,
                "provider_used": sorted({m.get("provider_used") for m in per_symbol if m.get("provider_used")}),
                "next_event_only": next_event_only,
                "event_priority": event_priority,
                "as_of_date": today_iso,
            },
        }

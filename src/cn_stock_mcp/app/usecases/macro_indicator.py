from __future__ import annotations

from cn_stock_mcp.app.models.macro import (
    INDICATOR_REGISTRY,
    OVERVIEW_PRESETS,
    MacroDataPoint,
    MacroIndicatorResult,
    MacroOverviewItem,
)
from cn_stock_mcp.app.services.provider_router import ProviderRouter
from cn_stock_mcp.providers.adapters.akshare_macro_adapters import (
    build_calendar_items,
    build_macro_summary_text,
    build_overview_item,
    normalize_macro_df,
)


class MacroIndicatorUseCase:
    def __init__(self) -> None:
        self.router = ProviderRouter()

    def execute(self, request) -> dict:
        indicator = request.indicator.strip().lower()
        region = request.region
        include = request.include
        history_n = request.history_n

        # ── Overview mode ──────────────────────────────────
        if "overview" in include:
            return self._execute_overview(region, history_n)

        # ── Single indicator ────────────────────────────────
        key = (region, indicator)
        entry = INDICATOR_REGISTRY.get(key)
        if entry is None:
            available = sorted(f"{r}:{i}" for r, i in INDICATOR_REGISTRY)
            raise ValueError(
                f"Unknown indicator '{indicator}' for region '{region}'. "
                f"Available: {', '.join(available)}"
            )

        provider = self.router.get_provider("akshare")
        df = provider.get_macro_raw(entry.func)
        all_points = normalize_macro_df(df, entry)

        # Filter by date range if specified
        if request.start_date or request.end_date:
            all_points = self._filter_by_date(all_points, request.start_date, request.end_date)

        result = MacroIndicatorResult(
            indicator=indicator,
            indicator_name=entry.name,
            region=region,
            unit=entry.unit,
            frequency=entry.freq,
        )

        # latest
        if "latest" in include and all_points:
            latest = self._find_latest(all_points)
            result.latest = latest

        # history
        if "history" in include:
            history_points = all_points[-history_n:]
            result.history = history_points
            result.history_count = len(history_points)

        # calendar
        if "calendar" in include:
            result.calendar = build_calendar_items(all_points, indicator, entry.name, region)

        result.summary = build_macro_summary_text(
            entry.name, entry.unit, result.latest, result.history
        )
        return result.model_dump()

    def _execute_overview(self, region: str, history_n: int) -> dict:
        preset = OVERVIEW_PRESETS.get(region, [])
        if not preset:
            raise ValueError(f"No overview preset for region '{region}'")

        provider = self.router.get_provider("akshare")
        overview_items: dict[str, MacroOverviewItem] = {}
        errors: list[str] = []

        for rgn, ind in preset:
            entry = INDICATOR_REGISTRY.get((rgn, ind))
            if not entry:
                continue
            try:
                df = provider.get_macro_raw(entry.func)
                points = normalize_macro_df(df, entry)
                latest = self._find_latest(points) if points else None
                overview_items[ind] = build_overview_item(latest, ind, entry, rgn) if latest else MacroOverviewItem(
                    indicator=ind, indicator_name=entry.name, unit=entry.unit, freq=entry.freq,
                )
            except Exception as exc:
                errors.append(f"{entry.name}: {exc}")

        summary = build_macro_summary_text("", "", None, [], overview_items=overview_items)

        result = MacroIndicatorResult(
            indicator="overview",
            indicator_name=f"{region} 宏观概览",
            region=region,
            overview=overview_items,
            summary=summary,
        )
        if errors:
            result.overview = {**result.overview, "_errors": errors}
        return result.model_dump()

    @staticmethod
    def _find_latest(points: list[MacroDataPoint]) -> MacroDataPoint | None:
        for p in reversed(points):
            if p.actual is not None:
                return p
        # Fallback: return last point even if actual is None
        return points[-1] if points else None

    @staticmethod
    def _filter_by_date(points: list[MacroDataPoint], start: str | None, end: str | None) -> list[MacroDataPoint]:
        filtered = points
        if start:
            filtered = [p for p in filtered if p.date >= start]
        if end:
            filtered = [p for p in filtered if p.date <= end]
        return filtered

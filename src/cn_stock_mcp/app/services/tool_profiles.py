from __future__ import annotations

from collections.abc import Iterable


RETAIL_V1_PREVIEW = frozenset(
    {
        "stock_search",
        "market_brief",
        "stock_snapshot",
        "stock_quote",
        "stock_history",
        "stock_review",
        "watchlist_review",
        "trading_calendar",
        "sector_review",
        "hot_theme_tracker",
    }
)

TOOL_PROFILES: dict[str, frozenset[str] | None] = {
    "full": None,
    "retail_v1_preview": RETAIL_V1_PREVIEW,
}

SAFE_FALLBACK_PROFILE = "retail_v1_preview"


def select_tool_names(names: Iterable[str], profile: str) -> set[str]:
    normalized = str(profile or "").strip()
    # A typo or corrupted profile must not silently expose every low-level
    # tool.  Keep the bounded retail surface as the safe fallback; callers
    # can opt into ``full`` explicitly.
    if normalized not in TOOL_PROFILES:
        normalized = SAFE_FALLBACK_PROFILE
    allowed = TOOL_PROFILES[normalized]
    if allowed is None:
        return set(names)
    return {name for name in names if name in allowed}

from __future__ import annotations

from openclaw_stock_mcp.app.services.provider_types import ProviderSelection
from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.providers.akshare_provider import AKShareProvider
from openclaw_stock_mcp.providers.errors import ProviderError
from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider

# ── Table-driven provider routing ──────────────────────────────────
# Each entry: tool_name → (primary, fallback_list)
# Tools with symbol/sec_type overrides are handled in _apply_overrides().

_TOOL_ROUTES: dict[str, tuple[str, list[str]]] = {
    # ── AKShare-only ──
    "trading_calendar":     ("akshare", []),
    "capital_flow":         ("akshare", []),
    "stock_financial":      ("akshare", []),
    "limit_stat":           ("akshare", []),
    "northbound":           ("akshare", []),
    "index_compose":        ("akshare", []),
    "earnings_quality":     ("akshare", []),
    "macro_indicator":      ("akshare", []),
    "dragon_tiger":         ("akshare", []),
    "etf_snapshot":         ("akshare", []),
    "convertible_bond":     ("akshare", []),
    "derivatives_data":     ("akshare", []),
    "margin_trading":       ("akshare", []),
    "block_trade":          ("akshare", []),
    "institute_hold":       ("akshare", []),
    "money_rate":           ("akshare", []),
    "stock_screen":         ("akshare", []),
    # ── Zhitu-only ──
    "market_pool":          ("zhitu", []),
    "stock_orderbook":      ("zhitu", []),
    "stock_profile":        ("zhitu", []),
    "sector_quote":         ("zhitu", []),
    "event_calendar":       ("zhitu", []),
    "sector_lookup":        ("zhitu", []),
    # ── Zhitu primary, AKShare fallback ──
    "market_overview":      ("zhitu", ["akshare"]),
    "valuation_rank":       ("zhitu", ["akshare"]),
    "industry_valuation_rank": ("zhitu", ["akshare"]),
    # ── Mixed / symbol-dependent (base; overrides may change) ──
    "stock_search":         ("akshare", ["zhitu"]),
    "stock_review":         ("akshare", []),
}

# Default for tools not in the table
_DEFAULT_ROUTE: tuple[str, list[str]] = ("akshare", ["zhitu"])


class ProviderRouter:
    def __init__(self) -> None:
        self._settings = get_settings()
        self.akshare = AKShareProvider()
        self.zhitu = ZhituProvider()

    # ── public API ──────────────────────────────────────────────

    def choose_provider(
        self,
        tool_name: str,
        symbol: str | None = None,
        sec_type: str | None = None,
        preferred: str | None = None,
    ) -> ProviderSelection:
        selection = self._resolve(tool_name, symbol, sec_type, preferred)
        return self._filter_selection(selection)

    def get_provider(self, name: str):
        if not self._is_enabled(name):
            raise ProviderError("PROVIDER_DISABLED", f"Provider {name} is disabled by configuration", retryable=False)
        if name == "zhitu":
            return self.zhitu
        return self.akshare

    # ── internal ─────────────────────────────────────────────────

    def _resolve(
        self,
        tool_name: str,
        symbol: str | None,
        sec_type: str | None,
        preferred: str | None,
    ) -> ProviderSelection:
        # 1. Explicit preferred overrides everything
        if preferred == "akshare":
            return ProviderSelection(primary="akshare", fallback=["zhitu"])
        if preferred == "zhitu":
            return ProviderSelection(primary="zhitu", fallback=["akshare"])

        # 2. Symbol/sec_type overrides for specific tools
        override = self._apply_overrides(tool_name, symbol, sec_type)
        if override is not None:
            return override

        # 3. Table lookup
        primary, fallback = _TOOL_ROUTES.get(tool_name, _DEFAULT_ROUTE)
        return ProviderSelection(primary=primary, fallback=fallback)

    def _apply_overrides(
        self,
        tool_name: str,
        symbol: str | None,
        sec_type: str | None,
    ) -> ProviderSelection | None:
        """Return a ProviderSelection if symbol/sec_type triggers an override,
        otherwise None to fall through to the table."""
        normalized = (symbol or "").upper()

        is_bj = normalized.endswith(".BJ") or normalized.startswith(("430", "83", "87", "92"))
        is_star = normalized.startswith("688") or normalized.startswith("688.")

        if tool_name == "stock_quote":
            if sec_type in ("index", "fund"):
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            if is_bj or is_star:
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            # SH/SZ main-board stock
            return ProviderSelection(primary="zhitu", fallback=["akshare"])

        if tool_name == "stock_history":
            if sec_type == "index":
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            if sec_type == "stock":
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            return ProviderSelection(primary="akshare", fallback=[])

        if tool_name == "technical_indicator":
            if sec_type in ("stock", "index"):
                return ProviderSelection(primary="zhitu", fallback=["akshare"])
            return ProviderSelection(primary="zhitu", fallback=[])

        return None

    def _is_enabled(self, name: str) -> bool:
        if name == "zhitu":
            return self._settings.zhitu_enabled
        if name == "akshare":
            return self._settings.akshare_enabled
        return True

    def _filter_selection(self, selection: ProviderSelection) -> ProviderSelection:
        providers = [selection.primary, *selection.fallback]
        filtered = [p for p in providers if self._is_enabled(p)]
        if not filtered:
            raise ProviderError("PROVIDER_DISABLED", "No enabled provider for selection", retryable=False)
        return ProviderSelection(primary=filtered[0], fallback=filtered[1:])

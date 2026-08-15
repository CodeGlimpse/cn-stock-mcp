from __future__ import annotations

from functools import lru_cache

from cn_stock_mcp.app.services.provider_types import ProviderSelection
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.providers.akshare_provider import AKShareProvider
from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.providers.zhitu_provider import ZhituProvider

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
    "index_enhance":        ("akshare", []),
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
    "insider_trade":        ("akshare", []),
    "dividend_rank":        ("akshare", []),
    "shareholder_change":  ("akshare", []),
    "disclosure_calendar": ("akshare", []),
    "stock_repurchase":   ("akshare", []),
    "stock_compare":      ("zhitu", ["akshare"]),
    "stock_snapshot":     ("composite", ["zhitu", "akshare"]),
    "industry_chain":     ("akshare", []),
    "stock_warrant":      ("akshare", []),
    "fund_flow":          ("akshare", []),
    "limit_up_pool":      ("akshare", []),
    "sec_reveal":         ("akshare", []),
    # ── Zhitu-only ──
    "market_pool":          ("zhitu", []),
    "stock_orderbook":      ("zhitu", []),
    "stock_profile":        ("zhitu", []),
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
_DEFAULT_ORDER_TOOLS = {"stock_search", "market_overview"}


@lru_cache(maxsize=1)
def _shared_providers() -> tuple[AKShareProvider, ZhituProvider]:
    """Build the process-wide providers used by all routers.

    A ZhituProvider owns an httpx client, whose SSL context creation is
    expensive on Windows.  UseCases historically created their own router,
    so constructing the MCP registry duplicated that work dozens of times.
    Provider state (connection pool, token health, and small provider caches)
    is safe and useful to share for the lifetime of the server process.
    """

    return AKShareProvider(), ZhituProvider()


class ProviderRouter:
    def __init__(self) -> None:
        self._settings = get_settings()
        self.akshare, self.zhitu = _shared_providers()

    # ── public API ──────────────────────────────────────────────

    @classmethod
    def describe_route(cls, tool_name: str) -> dict[str, object]:
        """Return a stable, read-only provider route description for tooling/docs."""
        primary, fallback = _TOOL_ROUTES.get(tool_name, _DEFAULT_ROUTE)
        return {
            "primary": primary,
            "fallback": list(fallback),
            "mode": "composite" if primary == "composite" else "provider",
        }

    def choose_provider(
        self,
        tool_name: str,
        symbol: str | None = None,
        sec_type: str | None = None,
        preferred: str | None = None,
    ) -> ProviderSelection:
        selection = self._resolve(tool_name, symbol, sec_type, preferred)
        return self._filter_selection(selection)

    def filter_selection(self, selection: ProviderSelection) -> ProviderSelection:
        """Apply enabled-provider and fallback settings to an explicit selection."""
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
        # 1. Explicit preferred overrides primary choice, but preserve tool-level fallback policy
        if preferred in {"akshare", "zhitu"}:
            primary, fallback = _TOOL_ROUTES.get(tool_name, _DEFAULT_ROUTE)
            providers = [preferred, primary, *fallback]
            deduped: list[str] = []
            for name in providers:
                if name not in deduped:
                    deduped.append(name)
            return ProviderSelection(primary=deduped[0], fallback=deduped[1:])

        # 2. Symbol/sec_type overrides for specific tools
        override = self._apply_overrides(tool_name, symbol, sec_type)
        if override is not None:
            return override

        # 3. Table lookup
        primary, fallback = _TOOL_ROUTES.get(tool_name, _DEFAULT_ROUTE)
        selection = ProviderSelection(primary=primary, fallback=fallback)
        if tool_name in _DEFAULT_ORDER_TOOLS or tool_name not in _TOOL_ROUTES:
            return self._apply_default_provider_order(selection)
        return selection

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
        if not self._settings.enable_provider_fallback:
            filtered = filtered[:1]
        return ProviderSelection(primary=filtered[0], fallback=filtered[1:])

    def _apply_default_provider_order(self, selection: ProviderSelection) -> ProviderSelection:
        configured = [
            item.strip().lower()
            for item in str(self._settings.default_provider_order or "").split(",")
            if item.strip().lower() in {"akshare", "zhitu"}
        ]
        ordered: list[str] = []
        for name in [*configured, selection.primary, *selection.fallback]:
            if name not in ordered:
                ordered.append(name)
        selected = [name for name in ordered if name in {selection.primary, *selection.fallback}]
        return ProviderSelection(primary=selected[0], fallback=selected[1:])

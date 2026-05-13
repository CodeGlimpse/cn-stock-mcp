"""Tests for provider enabled/disabled switch."""
import pytest

from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.providers.errors import ProviderError


def test_default_both_enabled():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_quote", symbol="600519.SH", sec_type="stock")
    assert sel.primary == "zhitu"


def test_zhitu_disabled_falls_back_to_akshare():
    router = ProviderRouter()
    router._settings.zhitu_enabled = False
    sel = router.choose_provider(tool_name="stock_quote", symbol="600519.SH", sec_type="stock")
    assert sel.primary == "akshare"


def test_akshare_disabled_no_fallback_raises():
    router = ProviderRouter()
    router._settings.akshare_enabled = False
    # trading_calendar is akshare-only; disabling akshare should raise
    # because there's no fallback
    with pytest.raises(ProviderError, match="No enabled provider"):
        router.choose_provider(tool_name="trading_calendar")


def test_get_provider_raises_for_disabled():
    router = ProviderRouter()
    router._settings.zhitu_enabled = False
    with pytest.raises(ProviderError, match="disabled"):
        router.get_provider("zhitu")


def test_get_provider_works_for_enabled():
    router = ProviderRouter()
    provider = router.get_provider("akshare")
    assert provider.name == "akshare"


def test_both_disabled_raises():
    router = ProviderRouter()
    router._settings.zhitu_enabled = False
    router._settings.akshare_enabled = False
    with pytest.raises(ProviderError, match="No enabled provider"):
        router.choose_provider(tool_name="stock_quote", symbol="600519.SH", sec_type="stock")

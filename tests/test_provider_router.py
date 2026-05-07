from openclaw_stock_mcp.app.services.provider_router import ProviderRouter


def test_stock_quote_stock_main_route_defaults_to_zhitu_primary():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_quote", symbol="600519.SH", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_stock_quote_bj_route_no_fallback():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_quote", symbol="430001.BJ", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == []


def test_stock_history_index_route_prefers_zhitu():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_history", symbol="000001.SH", sec_type="index")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_stock_history_stock_route_now_prefers_zhitu():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_history", symbol="600519.SH", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_technical_indicator_stock_route_allows_fallback():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="technical_indicator", symbol="600519.SH", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_hot_theme_tracker_defaults_to_akshare_primary_by_generic_rule():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="hot_theme_tracker")
    assert sel.primary == "akshare"
    assert sel.fallback == ["zhitu"]

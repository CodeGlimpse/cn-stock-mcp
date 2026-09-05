from cn_stock_mcp.app.services.provider_router import ProviderRouter


def test_provider_instances_are_shared_between_routers():
    first = ProviderRouter()
    second = ProviderRouter()

    assert first.akshare is second.akshare
    assert first.zhitu is second.zhitu


def test_stock_quote_stock_main_route_defaults_to_zhitu_primary():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_quote", symbol="600519.SH", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_stock_quote_bj_route_has_akshare_fallback():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_quote", symbol="430001.BJ", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


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


def test_stock_quote_star_has_akshare_fallback():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_quote", symbol="688001.SH", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_provider_fallback_can_be_disabled():
    router = ProviderRouter()
    router._settings.enable_provider_fallback = False

    sel = router.choose_provider(tool_name="stock_search")

    assert sel.primary == "akshare"
    assert sel.fallback == []


def test_default_provider_order_reorders_generic_routes():
    router = ProviderRouter()
    router._settings.default_provider_order = "zhitu,akshare"

    sel = router.choose_provider(tool_name="stock_search")

    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_default_provider_order_does_not_change_fixed_single_source_route():
    router = ProviderRouter()
    router._settings.default_provider_order = "zhitu,akshare"

    sel = router.choose_provider(tool_name="trading_calendar")

    assert sel.primary == "akshare"
    assert sel.fallback == []


def test_explicit_preference_overrides_default_provider_order():
    router = ProviderRouter()
    router._settings.default_provider_order = "akshare,zhitu"

    sel = router.choose_provider(tool_name="stock_search", preferred="zhitu")

    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_catalog_routes_match_symbol_aware_runtime_defaults():
    for name in ("stock_quote", "stock_history", "technical_indicator"):
        route = ProviderRouter.describe_route(name)
        assert route["primary"] == "zhitu"
        assert route["fallback"] == ["akshare"]


def test_market_pool_route_advertises_akshare_fallback():
    route = ProviderRouter.describe_route("market_pool")
    assert route["primary"] == "zhitu"
    assert route["fallback"] == ["akshare"]


def test_fund_indicator_uses_akshare_derived_route():
    router = ProviderRouter()
    selection = router.choose_provider(
        tool_name="technical_indicator", symbol="510050.SH", sec_type="fund"
    )
    assert selection.primary == "akshare"
    assert selection.fallback == []


def test_market_overview_runtime_matches_catalog_even_with_default_order():
    router = ProviderRouter()
    router._settings.default_provider_order = "akshare,zhitu"

    selection = router.choose_provider(tool_name="market_overview", sec_type="index")

    assert selection.primary == "zhitu"
    assert selection.fallback == ["akshare"]


def test_composite_catalog_routes_name_all_actual_providers():
    route = ProviderRouter.describe_route("market_brief")
    assert route["mode"] == "composite"
    assert route["primary"] == "composite"
    assert route["providers"] == ["zhitu", "akshare"]

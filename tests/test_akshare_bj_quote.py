from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pandas as pd

from openclaw_stock_mcp.app.services.provider_router import ProviderRouter
from openclaw_stock_mcp.app.services.symbol_resolver import SymbolResolver
from openclaw_stock_mcp.providers.akshare_provider import AKShareProvider
from openclaw_stock_mcp.providers.errors import ProviderError


def _make_bj_spot_df(rows: list[dict] | None = None) -> pd.DataFrame:
    if rows is None:
        rows = [
            {
                "序号": 1,
                "代码": "430001",
                "名称": "BJ测试股A",
                "最新价": 12.5,
                "涨跌幅": 3.21,
                "涨跌额": 0.39,
                "成交量": 100000.0,
                "成交额": 1250000.0,
                "振幅": 5.0,
                "最高": 13.0,
                "最低": 12.0,
                "今开": 12.1,
                "昨收": 12.11,
                "量比": 1.5,
                "换手率": 2.3,
                "市盈率-动态": 30.0,
                "市净率": 3.0,
                "总市值": 5000000000.0,
                "流通市值": 3000000000.0,
            },
            {
                "序号": 2,
                "代码": "830001",
                "名称": "BJ测试股B",
                "最新价": 8.0,
                "涨跌幅": -1.0,
                "涨跌额": -0.08,
                "成交量": 50000.0,
                "成交额": 400000.0,
                "振幅": 2.0,
                "最高": 8.2,
                "最低": 7.9,
                "今开": 8.1,
                "昨收": 8.08,
                "量比": 0.8,
                "换手率": 1.0,
                "市盈率-动态": 20.0,
                "市净率": 2.0,
                "总市值": 2000000000.0,
                "流通市值": 1000000000.0,
            },
        ]
    return pd.DataFrame(rows)


def test_akshare_get_quote_bj_returns_quote():
    provider = AKShareProvider()
    mock_ak = MagicMock()
    mock_ak.stock_bj_a_spot_em.return_value = _make_bj_spot_df()

    with patch.object(provider, "_require_ak", return_value=mock_ak):
        quote = provider.get_quote("430001.BJ", "stock")

    assert quote.symbol == "430001.BJ"
    assert quote.name == "BJ测试股A"
    assert quote.price == 12.5
    assert quote.open == 12.1
    assert quote.high == 13.0
    assert quote.low == 12.0
    assert quote.prev_close == 12.11
    assert quote.change == 0.39
    assert quote.change_percent == 3.21
    assert quote.volume == 100000.0
    assert quote.turnover == 1250000.0
    assert quote.pe == 30.0
    assert quote.pb == 3.0
    assert quote.market_cap == 5000000000.0
    assert quote.float_market_cap == 3000000000.0
    assert quote.exchange == "BJ"
    assert quote.board == "beijing"
    assert quote.source == "akshare"


def test_akshare_get_quote_bj_not_found_raises():
    provider = AKShareProvider()
    mock_ak = MagicMock()
    mock_ak.stock_bj_a_spot_em.return_value = _make_bj_spot_df()

    with patch.object(provider, "_require_ak", return_value=mock_ak):
        try:
            provider.get_quote("999999.BJ", "stock")
            assert False, "Should have raised"
        except ProviderError as exc:
            assert exc.code == "UNSUPPORTED_MARKET"
            assert "999999" in exc.message


def test_akshare_get_quote_non_bj_raises():
    provider = AKShareProvider()
    try:
        provider.get_quote("600519.SH", "stock")
        assert False, "Should have raised"
    except ProviderError as exc:
        assert exc.code == "UNSUPPORTED_SEC_TYPE"


def test_akshare_get_quotes_bj_batch():
    provider = AKShareProvider()
    mock_ak = MagicMock()
    mock_ak.stock_bj_a_spot_em.return_value = _make_bj_spot_df()

    with patch.object(provider, "_require_ak", return_value=mock_ak):
        quotes = provider.get_quotes(["430001.BJ", "830001.BJ"], "stock")

    assert len(quotes) == 2
    assert quotes[0].symbol == "430001.BJ"
    assert quotes[1].symbol == "830001.BJ"
    assert quotes[0].name == "BJ测试股A"
    assert quotes[1].name == "BJ测试股B"


def test_akshare_get_quotes_bj_partial():
    provider = AKShareProvider()
    mock_ak = MagicMock()
    mock_ak.stock_bj_a_spot_em.return_value = _make_bj_spot_df()

    with patch.object(provider, "_require_ak", return_value=mock_ak):
        quotes = provider.get_quotes(["430001.BJ", "999999.BJ"], "stock")

    # Only the found one should be returned
    assert len(quotes) == 1
    assert quotes[0].symbol == "430001.BJ"


def test_akshare_bj_spot_cache_ttl():
    provider = AKShareProvider()
    provider._bj_spot_cache_ttl = 2  # 2 seconds for test
    mock_ak = MagicMock()
    mock_ak.stock_bj_a_spot_em.return_value = _make_bj_spot_df()

    with patch.object(provider, "_require_ak", return_value=mock_ak):
        provider.get_quote("430001.BJ", "stock")
        assert mock_ak.stock_bj_a_spot_em.call_count == 1

        # Second call within TTL should use cache
        provider.get_quote("830001.BJ", "stock")
        assert mock_ak.stock_bj_a_spot_em.call_count == 1

        # After TTL expires, should fetch again
        provider._bj_spot_cache = (provider._bj_spot_cache[0] - 3, provider._bj_spot_cache[1])
        provider.get_quote("430001.BJ", "stock")
        assert mock_ak.stock_bj_a_spot_em.call_count == 2


def test_provider_router_stock_quote_bj_has_akshare_fallback():
    router = ProviderRouter()
    sel = router.choose_provider(tool_name="stock_quote", symbol="430001.BJ", sec_type="stock")
    assert sel.primary == "zhitu"
    assert sel.fallback == ["akshare"]


def test_provider_router_stock_quote_bj_prefix_has_akshare_fallback():
    router = ProviderRouter()
    for sym in ["830001.BJ", "870001.BJ", "920001.BJ"]:
        sel = router.choose_provider(tool_name="stock_quote", symbol=sym, sec_type="stock")
        assert sel.primary == "zhitu"
        assert sel.fallback == ["akshare"], f"Expected akshare fallback for {sym}"


def test_stock_quote_bj_fallback_from_zhitu_to_akshare():
    """Integration: zhitu fails -> akshare BJ spot fallback works."""
    from openclaw_stock_mcp.app.services.fallback import run_with_fallback_meta
    from openclaw_stock_mcp.app.services.provider_types import ProviderSelection

    router = ProviderRouter()
    selection = ProviderSelection(primary="zhitu", fallback=["akshare"])

    # Make zhitu fail
    with patch.object(router.zhitu, "get_quote", side_effect=ProviderError("PROVIDER_UNAVAILABLE", "zhitu down", retryable=True)):
        mock_ak = MagicMock()
        mock_ak.stock_bj_a_spot_em.return_value = _make_bj_spot_df()
        with patch.object(router.akshare, "_require_ak", return_value=mock_ak):
            quote, meta = run_with_fallback_meta(
                router,
                selection,
                lambda provider: provider.get_quote("430001.BJ", "stock"),
            )

    assert quote.symbol == "430001.BJ"
    assert meta.used_fallback is True
    assert meta.final_provider == "akshare"

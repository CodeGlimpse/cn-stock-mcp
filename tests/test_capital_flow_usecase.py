import time
from unittest.mock import MagicMock

import pytest

from cn_stock_mcp.app.models.capital_flow import CapitalFlowRecord
from cn_stock_mcp.app.usecases.capital_flow import CapitalFlowUseCase
from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.server.schemas import CapitalFlowRequest


def _payload(flow_type="market", limit=60, allow_stale=False):
    return CapitalFlowRequest(flow_type=flow_type, limit=limit, allow_stale=allow_stale)


def _cached_payload():
    return {
        "flow_type": "market",
        "source": "akshare",
        "summary": "cached",
        "records": [],
        "count": 0,
        "meta": {"provider_used": "akshare", "stale": False},
    }


def test_capital_flow_returns_explicitly_marked_stale_cache_on_retryable_failure():
    uc = CapitalFlowUseCase()
    req = _payload(limit=499, allow_stale=True)
    uc.cache.set(
        uc._cache_key(req),
        {"payload": _cached_payload(), "stored_at": time.time() - uc.cache_ttl_seconds - 30},
    )
    provider = MagicMock()
    provider.get_market_capital_flow.side_effect = ProviderError(
        "PROVIDER_UNAVAILABLE", "upstream down", retryable=True
    )
    uc.router.get_provider = MagicMock(return_value=provider)

    result = uc.execute(req)

    assert result["summary"] == "cached"
    assert result["meta"]["provider_used"] == "cache"
    assert result["meta"]["stale"] is True
    assert result["meta"]["stale_age_seconds"] >= uc.cache_ttl_seconds + 30


def test_capital_flow_does_not_return_stale_cache_by_default():
    uc = CapitalFlowUseCase()
    req = _payload(limit=498, allow_stale=False)
    uc.cache.set(
        uc._cache_key(req),
        {"payload": _cached_payload(), "stored_at": time.time() - uc.cache_ttl_seconds - 30},
    )
    provider = MagicMock()
    provider.get_market_capital_flow.side_effect = ProviderError(
        "PROVIDER_UNAVAILABLE", "upstream down", retryable=True
    )
    uc.router.get_provider = MagicMock(return_value=provider)

    with pytest.raises(ProviderError, match="upstream down"):
        uc.execute(req)


def test_capital_flow_success_records_endpoint_and_cache_metadata():
    uc = CapitalFlowUseCase()
    req = _payload(limit=497)
    provider = MagicMock()
    provider.name = "akshare"
    provider.last_capital_flow_meta = {
        "endpoint_used": "stock_market_fund_flow",
        "used_fallback_endpoint": False,
    }
    provider.get_market_capital_flow.return_value = (
        [CapitalFlowRecord(date="2026-08-15", main_net_inflow=1.0)],
        None,
    )
    uc.router.get_provider = MagicMock(return_value=provider)

    result = uc.execute(req)

    assert result["meta"]["endpoint_used"] == "stock_market_fund_flow"
    assert result["meta"]["cache_hit"] is False
    assert result["meta"]["stale"] is False
    assert uc.cache.get(uc._cache_key(req))["payload"]["flow_type"] == "market"

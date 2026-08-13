from __future__ import annotations

import pytest

from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}
        self.calls = []

    def _get_json(self, path: str, params=None):
        self.calls.append((path, params or {}))
        return [
            {
                "dm": "sh600519",
                "mc": "贵州茅台",
                "p": 1357.07,
                "zf": 1.05,
                "cje": 1984899011.0,
                "lt": 1734131271030.0,
                "zsz": 1734131271030.0,
                "hs": 0.12,
                "lbc": 1,
                "fbt": "09:25:00",
                "lbt": "09:25:00",
                "zj": 1000000,
                "zbc": 0,
                "tj": "1/1",
            }
        ]


@pytest.mark.parametrize("trade_date", ["2026-08-13", "20260813"])
def test_zhitu_market_pool_normalizes_date_for_api(trade_date):
    provider = _Zhitu()

    items = provider.get_market_pool("limit_up", trade_date)

    assert len(items) == 1
    assert provider.calls == [("/hs/pool/ztgc/2026-08-13", {})]
    assert items[0].symbol == "600519.SH"


def test_zhitu_market_pool_rejects_invalid_date_without_upstream_call():
    provider = _Zhitu()

    with pytest.raises(ProviderError) as exc:
        provider.get_market_pool("limit_up", "2026/08/13")

    assert exc.value.code == "INVALID_ARGUMENT"
    assert exc.value.retryable is False
    assert provider.calls == []

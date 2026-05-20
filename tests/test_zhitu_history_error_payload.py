import pytest

from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        pass

    def _get_json(self, path: str, params=None):
        return {"error": "数据不存在"}


def test_zhitu_history_error_payload_raises_provider_error():
    p = _Zhitu()
    with pytest.raises(ProviderError) as exc:
        p.get_history("899050.BJ", "index", "1d", start="2026-04-30", end="2026-04-30")

    assert exc.value.code == "PROVIDER_UNAVAILABLE"
    assert exc.value.retryable is True

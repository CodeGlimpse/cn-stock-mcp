from types import SimpleNamespace

from cn_stock_mcp.infra.config import Settings
from cn_stock_mcp.providers import akshare_provider as module
from cn_stock_mcp.providers.akshare_provider import AKShareProvider


class _Frame:
    empty = False

    def __init__(self, rows):
        self.rows = rows

    def to_dict(self, orient="records"):
        assert orient == "records"
        return list(self.rows)


def test_sector_capital_flow_uses_compatible_endpoint_fallback(monkeypatch):
    lib = SimpleNamespace(
        stock_fund_flow_industry=object(),
        stock_sector_fund_flow_rank=object(),
    )
    provider = AKShareProvider(Settings(capital_flow_circuit_failure_threshold=3))
    calls = []

    def fake_call(endpoint, fn, **kwargs):
        calls.append((endpoint, kwargs))
        if endpoint == "stock_fund_flow_industry":
            from cn_stock_mcp.providers.errors import ProviderError

            raise ProviderError("PROVIDER_UNAVAILABLE", "legacy endpoint down", retryable=True)
        return _Frame(
            [
                {
                    "序号": 1,
                    "名称": "人工智能",
                    "今日涨跌幅": 2.1,
                    "今日主力净流入-净额": 88.0,
                    "今日主力净流入最大股": "示例股份",
                }
            ]
        )

    monkeypatch.setattr(module, "ak", lib)
    monkeypatch.setattr(provider, "_call_capital_flow_endpoint", fake_call)

    items = provider.get_sector_capital_flow("industry")

    assert [call[0] for call in calls] == [
        "stock_fund_flow_industry",
        "stock_sector_fund_flow_rank",
    ]
    assert items[0].sector_name == "人工智能"
    assert provider.last_capital_flow_meta["used_fallback_endpoint"] is True

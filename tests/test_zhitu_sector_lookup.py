from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}

    def _get_json(self, path: str, params=None):
        self.last_path = path
        if path == "/hs/sectors/1000医药":
            return {
                "sector_name": "1000医药",
                "count": 2,
                "stocks": [
                    {"dm": "300122.SZ", "mc": "智飞生物", "jys": "SZ"},
                    {"dm": "600276.SH", "mc": "恒瑞医药", "jys": "SH"},
                ],
            }
        if path == "/hs/sectors/概念指数":
            return {"sector_name": "概念指数", "count": 0, "stocks": []}
        raise AssertionError(f"unexpected path: {path}")


def test_zhitu_sector_children_returns_stock_members_from_stocks_payload():
    provider = _Zhitu()

    items = provider.get_sector_lookup(mode="children", sector_name="1000医药", limit=10)

    assert provider.last_path == "/hs/sectors/1000医药"
    assert len(items) == 2
    assert items[0].sec_type == "stock"
    assert items[0].symbol == "300122.SZ"
    assert items[1].symbol == "600276.SH"


def test_zhitu_sector_children_handles_empty_stocks_payload():
    provider = _Zhitu()

    items = provider.get_sector_lookup(mode="children", sector_name="概念指数", limit=10)

    assert provider.last_path == "/hs/sectors/概念指数"
    assert items == []

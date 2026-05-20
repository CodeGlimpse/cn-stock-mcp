from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}
        self._concept_name_map = None

    def _get_json(self, path: str, params=None):
        self.last_path = path
        if path == "/hs/list/primary":
            return [
                {"dm": "1000医药", "mc": "1000医药"},
                {"dm": "1000信息", "mc": "1000信息"},
            ]
        if path == "/hs/list/sectors":
            return [
                {"dm": "101798.BKZS", "mc": "GN人工智能"},
                {"dm": "101999.BKZS", "mc": "概念指数"},
            ]
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
        if path == "/hs/sectors/GN人工智能":
            return {
                "sector_name": "GN人工智能",
                "count": 1,
                "stocks": [
                    {"dm": "300024.SZ", "mc": "机器人", "jys": "SZ"},
                ],
            }
        raise AssertionError(f"unexpected path: {path}")


def test_zhitu_sector_children_requires_sector_type():
    provider = _Zhitu()

    try:
        provider.get_sector_lookup(mode="children", sector_name="1000医药", limit=10)
        assert False, "expected ProviderError"
    except Exception as exc:
        assert "sector_type is required when mode=children" in str(exc)
        assert not hasattr(provider, "last_path")


def test_zhitu_sector_children_requires_sector_type_for_concept_name():
    provider = _Zhitu()

    try:
        provider.get_sector_lookup(mode="children", sector_name="概念指数", limit=10)
        assert False, "expected ProviderError"
    except Exception as exc:
        assert "sector_type is required when mode=children" in str(exc)
        assert not hasattr(provider, "last_path")


def test_zhitu_sector_children_primary_resolution_when_sector_type_explicit():
    provider = _Zhitu()

    items = provider.get_sector_lookup(mode="children", sector_type="primary", sector_name="医药", limit=10)

    assert provider.last_path == "/hs/sectors/1000医药"
    assert len(items) == 2
    assert items[0].symbol == "300122.SZ"


def test_zhitu_sector_children_concept_resolution_when_sector_type_explicit():
    provider = _Zhitu()

    items = provider.get_sector_lookup(mode="children", sector_type="concept", sector_name="人工智能", limit=10)

    assert provider.last_path == "/hs/sectors/GN人工智能"
    assert len(items) == 1
    assert items[0].symbol == "300024.SZ"

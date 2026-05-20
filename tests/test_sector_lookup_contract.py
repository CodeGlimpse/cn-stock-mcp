from pydantic import ValidationError

from cn_stock_mcp.server.schema_defs._sector import SectorLookupRequest
from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


class _StrictZhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}
        self._concept_name_map = None

    def _get_json(self, path: str, params=None):
        self.last_path = path
        if path == "/hs/list/primary":
            return [{"dm": "1000医药", "mc": "1000医药"}]
        if path == "/hs/list/sectors":
            return [{"dm": "101798.BKZS", "mc": "GN人工智能"}]
        if path == "/hs/sectors/1000医药":
            return {"sector_name": "1000医药", "count": 1, "stocks": [{"dm": "300122.SZ", "mc": "智飞生物", "jys": "SZ"}]}
        if path == "/hs/sectors/GN人工智能":
            return {"sector_name": "GN人工智能", "count": 1, "stocks": [{"dm": "300024.SZ", "mc": "机器人", "jys": "SZ"}]}
        raise ProviderError("INVALID_ARGUMENT", f"unexpected path: {path}", retryable=False)


def test_sector_lookup_request_children_requires_sector_type():
    try:
        SectorLookupRequest(mode="children", sector_name="医药")
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert "sector_type is required when mode=members/children" in str(exc)


def test_sector_lookup_request_list_still_defaults_to_concept():
    req = SectorLookupRequest(mode="list")
    assert req.sector_type == "concept"


def test_sector_lookup_request_children_requires_sector_name():
    try:
        SectorLookupRequest(mode="children", sector_type="primary")
        assert False, "expected ValidationError"
    except ValidationError:
        pass


def test_provider_children_without_sector_type_fails_fast_before_zhitu_call():
    provider = _StrictZhitu()
    try:
        provider.get_sector_lookup(mode="children", sector_name="医药", limit=10)
        assert False, "expected ProviderError"
    except ProviderError as exc:
        assert exc.code == "INVALID_ARGUMENT"
        assert "sector_type is required when mode=children" in exc.message
        assert not hasattr(provider, "last_path")


def test_provider_children_with_explicit_primary_resolves_name():
    provider = _StrictZhitu()
    items = provider.get_sector_lookup(mode="children", sector_type="primary", sector_name="医药", limit=10)
    assert provider.last_path == "/hs/sectors/1000医药"
    assert len(items) == 1
    assert items[0].symbol == "300122.SZ"


def test_provider_children_with_explicit_concept_resolves_name():
    provider = _StrictZhitu()
    items = provider.get_sector_lookup(mode="children", sector_type="concept", sector_name="人工智能", limit=10)
    assert provider.last_path == "/hs/sectors/GN人工智能"
    assert len(items) == 1
    assert items[0].symbol == "300024.SZ"

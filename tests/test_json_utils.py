import json

from cn_stock_mcp.infra.json_utils import dumps_json


def test_dumps_json_converts_non_finite_numbers_to_null():
    payload = json.loads(dumps_json({"nan": float("nan"), "inf": float("inf")}))
    assert payload == {"nan": None, "inf": None}

from openclaw_stock_mcp.app.usecases.sector_leaders import SectorLeadersUseCase


class _Item:
    def __init__(self, symbol: str):
        self.symbol = symbol


class _Lookup:
    def execute(self, req):
        return {"items": [_Item("A.SH"), _Item("B.SH"), _Item("C.SH")], "meta": {"x": 1}}


class _Batch:
    def execute(self, req):
        return {
            "mode": "trade_date_review",
            "requested_trade_date": "2026-05-08",
            "requested_start_date": None,
            "requested_end_date": None,
            "items": [
                {"symbol": "A.SH", "relative_strength": 3, "return": 5, "volume_ratio": 1.2, "max_drawdown": 2},
                {"symbol": "B.SH", "relative_strength": 2, "return": 2, "volume_ratio": 1.1, "max_drawdown": 3},
                {"symbol": "C.SH", "relative_strength": -1, "return": -4, "volume_ratio": 0.8, "max_drawdown": 6},
            ],
            "partial_failure": False,
            "errors": [],
        }


def test_sector_leaders_snapshot_groups():
    uc = SectorLeadersUseCase()
    uc.sector_lookup = _Lookup()
    uc.batch_review = _Batch()

    req = type(
        "Req",
        (),
        {
            "sector_name": "1000信息",
            "sector_type": "primary",
            "trade_date": "2026-05-08",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "zhitu",
            "sort_by": "relative_strength",
            "descending": True,
            "top_n": 2,
            "limit": 100,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    result = uc.execute(req)
    assert len(result["leaders"]) == 2
    assert len(result["draggers"]) == 2
    assert result["leaders"][0]["symbol"] == "A.SH"

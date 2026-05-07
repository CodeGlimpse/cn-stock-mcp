from openclaw_stock_mcp.app.usecases.sector_review import SectorReviewUseCase
from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase


class _MockSectorItem:
    def __init__(self, symbol: str, name: str):
        self.symbol = symbol
        self.name = name


class _MockSectorLookup(SectorLookupUseCase):
    def __init__(self, sector_type_captured: list):
        self._sector_type_captured = sector_type_captured

    def execute(self, request):
        self._sector_type_captured.append(getattr(request, "sector_type", None))
        return {
            "items": [
                _MockSectorItem("600519.SH", "贵州茅台"),
                _MockSectorItem("000001.SZ", "平安银行"),
            ],
            "total": 2,
            "source": "zhitu",
            "meta": {},
        }


class _MockBatchItem:
    def __init__(self, symbol: str, return_pct: float, relative_strength: float):
        self.symbol = symbol
        self.return_pct = return_pct
        self.relative_strength = relative_strength
        self.volume_ratio = 1.0
        self.max_drawdown = 0.0
        self.stats = {}
        self.benchmark = {"symbol": "000001.SH", "name": "上证指数", "return": 0.0}


class _MockStockReviewBatch:
    def __init__(self):
        pass

    def execute(self, request):
        return {
            "items": [
                {"symbol": "600519.SH", "return": 2.0, "relative_strength": 1.0, "volume_ratio": 1.2, "max_drawdown": 1.0, "stats": {"up_streak": 0, "down_streak": 0}, "benchmark": {"symbol": "000001.SH", "name": "上证指数", "return": 0.0}},
                {"symbol": "000001.SZ", "return": -1.0, "relative_strength": -0.5, "volume_ratio": 0.8, "max_drawdown": 2.0, "stats": {"up_streak": 0, "down_streak": 0}, "benchmark": {"symbol": "399001.SZ", "name": "深证成指", "return": 0.0}},
            ],
            "mode": "single_day",
            "requested_trade_date": "2026-05-07",
            "partial_failure": False,
            "errors": [],
            "sort_by": "relative_strength",
            "descending": True,
            "filters": {},
            "filtered_from": 2,
            "groups": {},
        }


def test_sector_review_passes_sector_type_to_lookup():
    captured = []
    uc = SectorReviewUseCase()
    uc.sector_lookup = _MockSectorLookup(captured)
    uc.batch_review = _MockStockReviewBatch()

    req = type("Req", (), {
        "sector_name": "人工智能",
        "sector_type": "concept",
        "trade_date": "2026-05-07",
        "start_date": None,
        "end_date": None,
        "adjust": "none",
        "provider": None,
        "sort_by": "relative_strength",
        "descending": True,
        "top_n": 5,
        "limit": 100,
        "min_relative_strength": None,
        "min_return": None,
        "max_drawdown_limit": None,
        "min_volume_ratio": None,
    })()

    result = uc.execute(req)

    assert captured[0] == "concept"
    assert result["sector_type"] == "concept"
    assert result["subject_name"] == "人工智能"


def test_sector_review_defaults_to_primary():
    captured = []
    uc = SectorReviewUseCase()
    uc.sector_lookup = _MockSectorLookup(captured)
    uc.batch_review = _MockStockReviewBatch()

    req = type("Req", (), {
        "sector_name": "1000信息",
        "trade_date": "2026-05-07",
        "start_date": None,
        "end_date": None,
        "adjust": "none",
        "provider": None,
        "sort_by": "relative_strength",
        "descending": True,
        "top_n": 5,
        "limit": 100,
        "min_relative_strength": None,
        "min_return": None,
        "max_drawdown_limit": None,
        "min_volume_ratio": None,
    })()

    result = uc.execute(req)

    assert captured[0] == "primary"
    assert result["sector_type"] == "primary"

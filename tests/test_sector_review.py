from openclaw_stock_mcp.app.usecases.sector_review import SectorReviewUseCase


class _Member:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name


class _SectorLookup:
    def execute(self, request):
        assert request.mode == "children"
        assert request.sector_name == "算力概念"
        return {
            "mode": "children",
            "sector_name": request.sector_name,
            "items": [
                _Member("000001.SZ", "平安银行"),
                _Member("300750.SZ", "宁德时代"),
                _Member("600519.SH", "贵州茅台"),
            ],
            "total": 3,
            "source": "zhitu",
            "meta": {"used_fallback": False},
        }


class _BatchReview:
    def execute(self, request):
        assert request.symbols == ["000001.SZ", "300750.SZ", "600519.SH"]
        return {
            "mode": "trade_date_review",
            "requested_trade_date": "2026-05-02",
            "requested_start_date": None,
            "requested_end_date": None,
            "sort_by": "relative_strength",
            "descending": True,
            "filters": {
                "min_relative_strength": None,
                "min_return": None,
                "max_drawdown_limit": None,
                "min_volume_ratio": None,
            },
            "items": [
                {
                    "symbol": "300750.SZ",
                    "return": 8.0,
                    "relative_strength": 5.0,
                    "max_drawdown": 3.0,
                    "volume_ratio": 1.5,
                    "tags": ["stronger_than_benchmark", "positive_return", "high_volume"],
                    "summary": "A",
                    "stats": {"up_streak": 2, "down_streak": 0},
                    "benchmark": {"symbol": "399006.SZ", "name": "创业板指", "return": 2.5},
                },
                {
                    "symbol": "600519.SH",
                    "return": 2.0,
                    "relative_strength": 1.0,
                    "max_drawdown": 4.0,
                    "volume_ratio": 1.1,
                    "tags": ["stronger_than_benchmark", "positive_return"],
                    "summary": "B",
                    "stats": {"up_streak": 0, "down_streak": 0},
                    "benchmark": {"symbol": "000001.SH", "name": "上证指数", "return": 1.2},
                },
                {
                    "symbol": "000001.SZ",
                    "return": -3.0,
                    "relative_strength": -1.0,
                    "max_drawdown": 9.0,
                    "volume_ratio": 0.8,
                    "tags": ["drawdown_risk"],
                    "summary": "C",
                    "stats": {"up_streak": 0, "down_streak": 2},
                    "benchmark": {"symbol": "399001.SZ", "name": "深证成指", "return": -0.5},
                },
            ],
            "groups": {
                "strong_candidates": 2,
                "risk_candidates": 1,
                "volume_focus": 1,
                "up_streak_candidates": 1,
            },
            "count": 3,
            "filtered_from": 3,
            "total_symbols": 3,
            "partial_failure": False,
            "errors": [],
            "summary": "batch done",
        }


class _RangeBatchReview:
    def execute(self, request):
        assert request.start_date == "2026-04-01"
        assert request.end_date == "2026-04-30"
        return {
            "mode": "range_review",
            "requested_trade_date": None,
            "requested_start_date": "2026-04-01",
            "requested_end_date": "2026-04-30",
            "sort_by": "relative_strength",
            "descending": True,
            "filters": {
                "min_relative_strength": None,
                "min_return": None,
                "max_drawdown_limit": None,
                "min_volume_ratio": None,
            },
            "items": [
                {
                    "symbol": "300750.SZ",
                    "return": 14.0,
                    "relative_strength": 9.0,
                    "max_drawdown": 4.0,
                    "volume_ratio": 1.6,
                    "tags": ["stronger_than_benchmark", "positive_return", "high_volume"],
                    "summary": "A",
                    "stats": {"up_streak": 3, "down_streak": 0},
                    "benchmark": {"symbol": "399006.SZ", "name": "创业板指", "return": 3.5},
                },
                {
                    "symbol": "600519.SH",
                    "return": -1.0,
                    "relative_strength": -0.5,
                    "max_drawdown": 6.0,
                    "volume_ratio": 0.9,
                    "tags": [],
                    "summary": "B",
                    "stats": {"up_streak": 0, "down_streak": 1},
                    "benchmark": {"symbol": "000001.SH", "name": "上证指数", "return": 1.2},
                },
                {
                    "symbol": "000001.SZ",
                    "return": -2.0,
                    "relative_strength": -1.5,
                    "max_drawdown": 8.5,
                    "volume_ratio": 0.7,
                    "tags": ["drawdown_risk"],
                    "summary": "C",
                    "stats": {"up_streak": 0, "down_streak": 2},
                    "benchmark": {"symbol": "399001.SZ", "name": "深证成指", "return": -0.5},
                },
                {
                    "symbol": "600763.SH",
                    "return": -3.5,
                    "relative_strength": -2.2,
                    "max_drawdown": 9.0,
                    "volume_ratio": 0.6,
                    "tags": ["drawdown_risk"],
                    "summary": "D",
                    "stats": {"up_streak": 0, "down_streak": 3},
                    "benchmark": {"symbol": "000001.SH", "name": "上证指数", "return": 1.2},
                },
            ],
            "groups": {
                "strong_candidates": 1,
                "risk_candidates": 2,
                "volume_focus": 1,
                "up_streak_candidates": 1,
            },
            "count": 4,
            "filtered_from": 4,
            "total_symbols": 4,
            "partial_failure": False,
            "errors": [],
            "summary": "range batch done",
        }


def _build_req():
    return type(
        "Req",
        (),
        {
            "sector_name": "算力概念",
            "trade_date": "2026-05-02",
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


def test_sector_review_aggregates_members_and_batch_review():
    uc = SectorReviewUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.batch_review = _BatchReview()

    result = uc.execute(_build_req())

    assert result["sector_name"] == "算力概念"
    assert result["member_count"] == 3
    assert result["reviewed_count"] == 3
    assert result["leaders"][0]["symbol"] == "300750.SZ"
    assert result["laggards"][0]["symbol"] == "000001.SZ"
    assert result["breadth"]["positive_count"] == 2
    assert result["breadth"]["negative_count"] == 1
    assert result["stats"]["avg_return"] is not None
    assert result["summary"]


def test_sector_review_adds_sentiment_structure_rankings_and_buckets():
    uc = SectorReviewUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.batch_review = _BatchReview()

    result = uc.execute(_build_req())

    assert result["sentiment"]["label"] in {"hot", "warm", "neutral", "cool", "cold"}
    assert result["sentiment"]["label_zh"]
    assert result["rankings"]["leaders_by_return"][0]["symbol"] == "300750.SZ"
    assert result["rankings"]["leaders_by_relative_strength"][0]["symbol"] == "300750.SZ"
    assert result["rankings"]["leaders_by_volume_ratio"][0]["symbol"] == "300750.SZ"
    assert result["rankings"]["drawdown_risk"][0]["symbol"] == "000001.SZ"
    assert result["breadth"]["up_streak_count"] == 1
    assert result["breadth"]["down_streak_count"] == 1
    assert result["stats"]["median_volume_ratio"] is not None
    assert result["stats"]["avg_max_drawdown"] is not None
    assert result["stats"]["return_spread"] == 11.0
    assert result["stats"]["return_stddev"] is not None
    assert result["structure"]["coverage_ratio"] == 1.0
    assert "broad_strength" in result["structure"]["tags"]
    assert "high_dispersion" in result["structure"]["tags"]
    assert result["buckets"]["strong_candidates"][0]["symbol"] == "300750.SZ"
    assert result["buckets"]["risk_alerts"][0]["symbol"] == "000001.SZ"
    assert result["buckets"]["leaders"][0]["symbol"] == "300750.SZ"
    assert result["buckets"]["followers"][0]["symbol"] == "600519.SH"
    assert result["buckets"]["draggers"][0]["symbol"] == "000001.SZ"


def test_sector_review_adds_benchmark_summary_and_continuity():
    uc = SectorReviewUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.batch_review = _BatchReview()

    result = uc.execute(_build_req())

    assert result["benchmark_summary"]["dominant_benchmark_symbol"] in {"399006.SZ", "000001.SH", "399001.SZ"}
    assert result["benchmark_summary"]["dominant_member_count"] == 1
    assert result["benchmark_summary"]["avg_benchmark_return"] is not None
    assert len(result["benchmark_summary"]["benchmark_mix"]) == 3
    assert result["continuity"]["max_up_streak"] == 2
    assert result["continuity"]["max_down_streak"] == 2
    assert result["continuity"]["sustained_strength_count"] == 1
    assert result["continuity"]["sustained_weakness_count"] == 1


def test_sector_review_adds_range_rotation_signals():
    uc = SectorReviewUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.batch_review = _RangeBatchReview()

    req = type(
        "Req",
        (),
        {
            "sector_name": "算力概念",
            "trade_date": None,
            "start_date": "2026-04-01",
            "end_date": "2026-04-30",
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

    assert result["mode"] == "range_review"
    assert result["rotation"]["range_mode"] is True
    assert result["rotation"]["label"] == "leader_driven"
    assert result["rotation"]["label_zh"] == "龙头驱动"
    assert result["rotation"]["top1_return_contribution"] is not None
    assert result["rotation"]["top1_return_contribution"] > 0.9
    assert result["rotation"]["negative_ratio"] > result["rotation"]["positive_ratio"]
    assert result["rotation"]["leader_symbols"][0] == "300750.SZ"
    assert "轮动 龙头驱动" in result["summary"]


def test_sector_review_raises_when_no_members_found():
    uc = SectorReviewUseCase()
    uc.sector_lookup = type("Lookup", (), {"execute": lambda self, request: {"items": [], "total": 0, "source": "zhitu", "meta": {}}})()
    uc.batch_review = _BatchReview()

    req = type(
        "Req",
        (),
        {
            "sector_name": "空板块",
            "trade_date": "2026-05-02",
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

    from openclaw_stock_mcp.providers.errors import ProviderError

    try:
        uc.execute(req)
        assert False, "expected ProviderError"
    except ProviderError as exc:
        assert exc.code == "EMPTY_RESULT"

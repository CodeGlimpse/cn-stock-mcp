from cn_stock_mcp.app.usecases.hot_theme_tracker import HotThemeTrackerUseCase
from cn_stock_mcp.providers.errors import ProviderError
from cn_stock_mcp.server.schemas import HotThemeTrackerRequest


class _SectorLookup:
    def execute(self, request):
        return {
            "items": [
                {"name": "1000信息"},
                {"name": "1000工业"},
                {"name": "1000医药"},
            ],
            "total": 3,
            "source": "zhitu",
            "meta": {},
        }


class _SectorRotation:
    def execute(self, request):
        assert request.top_n >= 3
        return {
            "mode": "trade_date_review",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "partial_failure": False,
            "errors": [],
            "rotation": {"label": "focused_leadership", "score": 2.4},
            "sentiment": {"label": "warm", "normalized_score": 68.0},
            "items": [
                {
                    "sector_name": "1000信息",
                    "avg_return": 4.2,
                    "avg_relative_strength": 2.8,
                    "positive_ratio": 0.75,
                    "stronger_ratio": 0.75,
                    "rotation": {"score": 2.8},
                    "sentiment": {"normalized_score": 76.0},
                    "structure_tags": ["broad_strength"],
                    "leaders": [{"symbol": "300750.SZ"}],
                    "laggards": [{"symbol": "002230.SZ"}],
                    "summary": "信息偏强",
                },
                {
                    "sector_name": "1000工业",
                    "avg_return": 1.5,
                    "avg_relative_strength": 0.5,
                    "positive_ratio": 0.55,
                    "stronger_ratio": 0.5,
                    "rotation": {"score": 1.2},
                    "sentiment": {"normalized_score": 58.0},
                    "structure_tags": ["mixed"],
                    "leaders": [{"symbol": "002594.SZ"}],
                    "laggards": [{"symbol": "601766.SH"}],
                    "summary": "工业中性偏强",
                },
                {
                    "sector_name": "1000医药",
                    "avg_return": -1.2,
                    "avg_relative_strength": -0.8,
                    "positive_ratio": 0.33,
                    "stronger_ratio": 0.33,
                    "rotation": {"score": -0.5},
                    "sentiment": {"normalized_score": 38.0},
                    "structure_tags": ["weak_breadth"],
                    "leaders": [{"symbol": "600276.SH"}],
                    "laggards": [{"symbol": "300122.SZ"}],
                    "summary": "医药偏弱",
                },
            ],
        }


class _MarketPool:
    def execute(self, request):
        if request.pool_type == "limit_up":
            return {
                "items": [{"symbol": "300750.SZ"}, {"symbol": "002594.SZ"}],
                "count": 2,
            }
        return {
            "items": [{"symbol": "300750.SZ"}, {"symbol": "600519.SH"}, {"symbol": "002594.SZ"}],
            "count": 3,
        }


def test_hot_theme_tracker_request_normalizes_and_defaults():
    req = HotThemeTrackerRequest(sector_names=[" 1000信息 ", "1000工业", "1000信息"])

    assert req.trade_date is not None
    assert req.sector_names == ["1000信息", "1000工业"]
    assert req.sector_type == "primary"
    assert req.top_n == 5


def test_hot_theme_tracker_requires_two_distinct_sector_names_when_provided():
    try:
        HotThemeTrackerRequest(sector_names=["1000信息", " 1000信息 "])
        assert False, "expected validation error"
    except Exception as exc:
        assert "at least 2 distinct" in str(exc)


def test_hot_theme_tracker_builds_ranked_themes_and_pool_snapshot():
    uc = HotThemeTrackerUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.sector_rotation = _SectorRotation()
    uc.market_pool = _MarketPool()

    req = type(
        "Req",
        (),
        {
            "sector_names": None,
            "sector_type": "primary",
            "watch_name": "主线观察",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "zhitu",
            "sort_by": "avg_relative_strength",
            "descending": True,
            "top_n": 2,
            "sector_limit": 5,
            "member_limit": 10,
            "member_top_n": 1,
            "pool_top_n": 2,
            "include_pool_snapshot": True,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    result = uc.execute(req)

    assert result["subject_type"] == "hot_theme_tracker"
    assert result["subject_name"] == "主线观察"
    assert result["member_count"] == 3
    assert result["reviewed_count"] == 3
    assert result["leaders"][0]["sector_name"] == "1000信息"
    assert result["laggards"][0]["sector_name"] == "1000医药"
    assert result["themes"][0]["theme_label"] in {"hot", "warm"}
    assert result["pool_snapshot"]["limit_up"]["count"] == 2
    assert result["pool_snapshot"]["strong"]["count"] == 3
    assert result["meta"]["theme_score_schema"]["schema"] == "theme_score_v1"
    assert result["meta"]["source_sector_names"] == ["1000信息", "1000工业", "1000医药"]


def test_hot_theme_tracker_raises_when_resolved_sectors_too_few():
    uc = HotThemeTrackerUseCase()

    class _TinyLookup:
        def execute(self, request):
            return {"items": [{"name": "1000信息"}], "total": 1, "source": "zhitu", "meta": {}}

    uc.sector_lookup = _TinyLookup()
    uc.sector_rotation = _SectorRotation()
    uc.market_pool = _MarketPool()

    req = type(
        "Req",
        (),
        {
            "sector_names": None,
            "sector_type": "primary",
            "watch_name": None,
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "zhitu",
            "sort_by": "avg_relative_strength",
            "descending": True,
            "top_n": 2,
            "sector_limit": 5,
            "member_limit": 10,
            "member_top_n": 1,
            "pool_top_n": 2,
            "include_pool_snapshot": False,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    try:
        uc.execute(req)
        assert False, "expected ProviderError"
    except ProviderError as exc:
        assert exc.code == "INVALID_ARGUMENT"

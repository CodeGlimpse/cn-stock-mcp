from openclaw_stock_mcp.app.usecases.sector_rotation_review import SectorRotationReviewUseCase
from openclaw_stock_mcp.server.schemas import SectorRotationReviewRequest


class _SectorReview:
    def execute(self, request):
        if request.sector_name == "食品饮料":
            raise Exception("upstream failed")

        if request.sector_name == "电力设备":
            return {
                "subject_type": "sector",
                "subject_name": "电力设备",
                "sector_name": "电力设备",
                "mode": "trade_date_review",
                "trade_date": "2026-05-06",
                "requested_trade_date": "2026-05-06",
                "start_date": None,
                "end_date": None,
                "member_count": 4,
                "reviewed_count": 4,
                "breadth": {
                    "positive_count": 3,
                    "negative_count": 1,
                    "flat_count": 0,
                    "stronger_than_benchmark_count": 3,
                    "high_volume_count": 2,
                    "up_streak_count": 1,
                    "down_streak_count": 0,
                },
                "stats": {
                    "avg_return": 4.0,
                    "median_return": 3.5,
                    "avg_relative_strength": 2.5,
                    "median_relative_strength": 2.0,
                    "avg_volume_ratio": 1.3,
                    "median_volume_ratio": 1.2,
                    "max_drawdown_worst": 7.0,
                    "avg_max_drawdown": 3.0,
                    "best_return": 8.0,
                    "worst_return": -1.0,
                    "return_spread": 9.0,
                    "return_stddev": 3.8,
                    "relative_strength_stddev": 2.1,
                },
                "sentiment": {
                    "score": 3.0,
                    "normalized_score": 80.0,
                    "label": "hot",
                    "label_zh": "偏热",
                    "score_semantics": "sentiment_temperature_v1",
                },
                "benchmark_summary": {
                    "dominant_benchmark_symbol": "399006.SZ",
                    "dominant_benchmark_name": "创业板指",
                    "dominant_member_count": 2,
                    "avg_benchmark_return": 1.2,
                    "benchmark_mix": [{"symbol": "399006.SZ", "name": "创业板指", "member_count": 2}],
                },
                "continuity": {
                    "max_up_streak": 2,
                    "max_down_streak": 1,
                    "avg_up_streak": 1.0,
                    "avg_down_streak": 0.3,
                    "sustained_strength_count": 2,
                    "sustained_weakness_count": 0,
                },
                "rotation": {
                    "label": "broad_advance",
                    "label_zh": "普涨轮动",
                    "score": 3.4,
                    "positive_ratio": 0.75,
                    "negative_ratio": 0.25,
                    "outperform_ratio": 0.75,
                    "strong_trend_ratio": 0.5,
                    "weak_trend_ratio": 0.0,
                    "top1_return_contribution": 0.4,
                    "top3_return_contribution": 0.9,
                    "leader_symbols": ["300750.SZ"],
                    "laggard_symbols": ["002000.SZ"],
                    "range_mode": False,
                },
                "structure": {
                    "coverage_ratio": 1.0,
                    "positive_ratio": 0.75,
                    "stronger_ratio": 0.75,
                    "high_volume_ratio": 0.5,
                    "tags": ["broad_strength", "benchmark_outperform", "active_volume"],
                },
                "leaders": [
                    {"symbol": "300750.SZ", "return": 8.0, "relative_strength": 5.0},
                    {"symbol": "688223.SH", "return": 6.0, "relative_strength": 4.5},
                ],
                "laggards": [
                    {"symbol": "002000.SZ", "return": -1.0, "relative_strength": -0.5},
                ],
                "rankings": {},
                "buckets": {},
                "items": [
                    {"symbol": "300750.SZ", "source": "akshare"},
                    {"symbol": "688223.SH", "source": "akshare"},
                ],
                "summary": "电力设备偏强。",
                "partial_failure": False,
                "errors": [],
                "meta": {
                    "sector_lookup": {"source": "zhitu", "total": 4, "meta": {}},
                },
            }

        return {
            "subject_type": "sector",
            "subject_name": "通信设备",
            "sector_name": "通信设备",
            "mode": "trade_date_review",
            "trade_date": "2026-05-06",
            "requested_trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "member_count": 3,
            "reviewed_count": 3,
            "breadth": {
                "positive_count": 1,
                "negative_count": 2,
                "flat_count": 0,
                "stronger_than_benchmark_count": 1,
                "high_volume_count": 1,
                "up_streak_count": 0,
                "down_streak_count": 1,
            },
            "stats": {
                "avg_return": -1.5,
                "median_return": -1.0,
                "avg_relative_strength": -0.8,
                "median_relative_strength": -0.7,
                "avg_volume_ratio": 0.9,
                "median_volume_ratio": 0.9,
                "max_drawdown_worst": 8.5,
                "avg_max_drawdown": 5.0,
                "best_return": 2.0,
                "worst_return": -3.5,
                "return_spread": 5.5,
                "return_stddev": 2.6,
                "relative_strength_stddev": 1.4,
            },
            "sentiment": {
                "score": -1.5,
                "normalized_score": 35.0,
                "label": "cool",
                "label_zh": "偏弱",
                "score_semantics": "sentiment_temperature_v1",
            },
            "benchmark_summary": {
                "dominant_benchmark_symbol": "000001.SH",
                "dominant_benchmark_name": "上证指数",
                "dominant_member_count": 2,
                "avg_benchmark_return": 0.6,
                "benchmark_mix": [{"symbol": "000001.SH", "name": "上证指数", "member_count": 2}],
            },
            "continuity": {
                "max_up_streak": 1,
                "max_down_streak": 2,
                "avg_up_streak": 0.3,
                "avg_down_streak": 1.0,
                "sustained_strength_count": 0,
                "sustained_weakness_count": 2,
            },
            "rotation": {
                "label": "leader_driven",
                "label_zh": "龙头驱动",
                "score": 1.1,
                "positive_ratio": 0.33,
                "negative_ratio": 0.67,
                "outperform_ratio": 0.33,
                "strong_trend_ratio": 0.0,
                "weak_trend_ratio": 0.67,
                "top1_return_contribution": 1.0,
                "top3_return_contribution": 1.0,
                "leader_symbols": ["600941.SH"],
                "laggard_symbols": ["600498.SH"],
                "range_mode": False,
            },
            "structure": {
                "coverage_ratio": 1.0,
                "positive_ratio": 0.33,
                "stronger_ratio": 0.33,
                "high_volume_ratio": 0.33,
                "tags": ["high_dispersion", "drawdown_risk", "weak_breadth"],
            },
            "leaders": [
                {"symbol": "600941.SH", "return": 2.0, "relative_strength": 1.5},
                {"symbol": "300394.SZ", "return": -0.5, "relative_strength": 0.1},
            ],
            "laggards": [
                {"symbol": "600498.SH", "return": -3.5, "relative_strength": -2.0},
            ],
            "rankings": {},
            "buckets": {},
            "items": [
                {"symbol": "600941.SH", "source": "akshare"},
                {"symbol": "600498.SH", "source": "akshare"},
            ],
            "summary": "通信设备分化。",
            "partial_failure": True,
            "errors": [{"symbol": "300394.SZ", "error_code": "PROVIDER_UNAVAILABLE", "message": "x", "retryable": True}],
            "meta": {
                "sector_lookup": {"source": "zhitu", "total": 3, "meta": {}},
            },
        }


def test_sector_rotation_review_schema_normalizes_and_deduplicates_names():
    req = SectorRotationReviewRequest(
        sector_names=[" 电力设备 ", "通信设备", "电力设备"],
        trade_date="2026-05-06",
    )

    assert req.trade_date == "2026-05-06"
    assert req.sector_names == ["电力设备", "通信设备"]
    assert req.sort_by == "avg_relative_strength"


def test_sector_rotation_review_aggregates_multiple_sectors_and_partial_failure():
    uc = SectorRotationReviewUseCase()
    uc.sector_review = _SectorReview()

    req = type(
        "Req",
        (),
        {
            "sector_names": ["电力设备", "通信设备", "食品饮料"],
            "sector_type": "primary",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "zhitu",
            "sort_by": "avg_relative_strength",
            "descending": True,
            "top_n": 2,
            "limit": 100,
            "member_top_n": 1,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    result = uc.execute(req)

    assert result["subject_type"] == "sector_rotation"
    assert result["subject_name"] == "primary_sector_set"
    assert result["mode"] == "trade_date_review"
    assert result["member_count"] == 3
    assert result["reviewed_count"] == 2
    assert result["partial_failure"] is True
    assert result["items"][0]["sector_name"] == "电力设备"
    assert result["rankings"]["leaders_by_avg_relative_strength"][0]["sector_name"] == "电力设备"
    assert result["rankings"]["laggards_by_avg_return"][0]["sector_name"] == "通信设备"
    assert result["leaders"][0]["sector_name"] == "电力设备"
    assert result["laggards"][0]["sector_name"] == "通信设备"
    assert result["breadth"]["positive_sector_count"] == 1
    assert result["breadth"]["negative_sector_count"] == 1
    assert result["breadth"]["leader_driven_sector_count"] == 1
    assert result["stats"]["stock_member_count_total"] == 7
    assert result["stats"]["stock_reviewed_count_total"] == 7
    assert result["sentiment"]["score_semantics"] == "sentiment_temperature_v1"
    assert result["rotation"]["label"] in {"mixed_rotation", "divergent_rotation", "focused_leadership", "broad_sector_advance", "defensive_rotation", "sector_wide_decline"}
    assert result["meta"]["review_envelope_schema"]["schema"] == "review_envelope_v1"
    assert result["meta"]["sentiment_score_schema"]["schema"] == "sentiment_temperature_v1"
    assert result["meta"]["rotation_score_schema"]["schema"] == "rotation_signal_v1"
    assert result["meta"]["item_schema"]["schema"] == "sector_rotation_item_v1"
    assert result["errors"][0]["sector_name"] == "食品饮料"
    assert result["buckets"]["mainline_sectors"][0]["sector_name"] == "电力设备"
    assert result["buckets"]["risk_sectors"][0]["sector_name"] == "通信设备"


def test_sector_rotation_review_raises_when_all_sectors_fail():
    uc = SectorRotationReviewUseCase()

    class _Failing:
        def execute(self, request):
            raise Exception("all failed")

    uc.sector_review = _Failing()

    req = type(
        "Req",
        (),
        {
            "sector_names": ["A", "B"],
            "sector_type": "primary",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "zhitu",
            "sort_by": "avg_relative_strength",
            "descending": True,
            "top_n": 2,
            "limit": 100,
            "member_top_n": 1,
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


def test_sector_rotation_review_uses_limit_for_inner_sector_review_scope():
    uc = SectorRotationReviewUseCase()
    captured = []

    class _CapturingSectorReview:
        def execute(self, request):
            captured.append((request.sector_name, request.top_n, request.limit))
            return _SectorReview().execute(type("Req", (), {**request.__dict__})())

    uc.sector_review = _CapturingSectorReview()

    req = type(
        "Req",
        (),
        {
            "sector_names": ["电力设备", "通信设备"],
            "sector_type": "primary",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "zhitu",
            "sort_by": "avg_relative_strength",
            "descending": True,
            "top_n": 1,
            "limit": 7,
            "member_top_n": 2,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    uc.execute(req)

    assert captured == [("电力设备", 7, 7), ("通信设备", 7, 7)]


def test_sector_rotation_review_collects_results_in_input_order_even_when_parallel():
    uc = SectorRotationReviewUseCase()

    class _ParallelLike:
        def __init__(self):
            self.mapping = {
                "通信设备": _SectorReview().execute(type("Req", (), {"sector_name": "通信设备"})()),
                "电力设备": _SectorReview().execute(type("Req", (), {"sector_name": "电力设备"})()),
            }

        def execute(self, request):
            return self.mapping[request.sector_name]

    uc.sector_review = _ParallelLike()
    uc._collect_sector_results = lambda request, inner_top_n: {
        "通信设备": uc.sector_review.execute(type("Req", (), {**request.__dict__, "sector_name": "通信设备"})()),
        "电力设备": uc.sector_review.execute(type("Req", (), {**request.__dict__, "sector_name": "电力设备"})()),
    }

    req = type(
        "Req",
        (),
        {
            "sector_names": ["电力设备", "通信设备"],
            "sector_type": "primary",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "zhitu",
            "sort_by": "avg_relative_strength",
            "descending": True,
            "top_n": 2,
            "limit": 5,
            "member_top_n": 1,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    result = uc.execute(req)
    assert result["items"][0]["sector_name"] == "电力设备"
    assert result["items"][1]["sector_name"] == "通信设备"

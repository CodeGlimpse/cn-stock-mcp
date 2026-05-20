from cn_stock_mcp.app.usecases.watchlist_review import WatchlistReviewUseCase


class _BatchReview:
    def execute(self, request):
        assert request.symbols == ["600519.SH", "300750.SZ", "000001.SZ", "002594.SZ"]
        return {
            "mode": "trade_date_review",
            "requested_trade_date": "2026-05-06",
            "requested_start_date": None,
            "requested_end_date": None,
            "sort_by": "relative_strength",
            "descending": True,
            "items": [
                {
                    "symbol": "300750.SZ",
                    "mode": "trade_date_review",
                    "trade_date": "2026-05-06",
                    "close": 100.0,
                    "relative_strength": 8.0,
                    "return": 12.0,
                    "max_drawdown": 3.0,
                    "volume_ratio": 1.8,
                    "tags": ["stronger_than_benchmark", "positive_return", "high_volume", "up_streak"],
                    "benchmark": {"symbol": "399006.SZ", "name": "创业板指", "return_pct": 2.0},
                    "stats": {"up_streak": 3, "down_streak": 0},
                    "summary": "A",
                    "source": "akshare",
                },
                {
                    "symbol": "002594.SZ",
                    "mode": "trade_date_review",
                    "trade_date": "2026-05-06",
                    "close": 90.0,
                    "relative_strength": 3.0,
                    "return": 5.0,
                    "max_drawdown": 4.0,
                    "volume_ratio": 1.3,
                    "tags": ["stronger_than_benchmark", "positive_return", "high_volume"],
                    "benchmark": {"symbol": "399001.SZ", "name": "深证成指", "return_pct": 1.0},
                    "stats": {"up_streak": 1, "down_streak": 0},
                    "summary": "B",
                    "source": "akshare",
                },
                {
                    "symbol": "600519.SH",
                    "mode": "trade_date_review",
                    "trade_date": "2026-05-06",
                    "close": 80.0,
                    "relative_strength": -1.0,
                    "return": 1.0,
                    "max_drawdown": 2.0,
                    "volume_ratio": 0.9,
                    "tags": [],
                    "benchmark": {"symbol": "000001.SH", "name": "上证指数", "return_pct": 1.5},
                    "stats": {"up_streak": 0, "down_streak": 0},
                    "summary": "C",
                    "source": "akshare",
                },
                {
                    "symbol": "000001.SZ",
                    "mode": "trade_date_review",
                    "trade_date": "2026-05-06",
                    "close": 70.0,
                    "relative_strength": -12.0,
                    "return": -6.0,
                    "max_drawdown": 10.0,
                    "volume_ratio": 1.4,
                    "tags": ["drawdown_risk", "high_volume", "down_streak"],
                    "benchmark": {"symbol": "399001.SZ", "name": "深证成指", "return_pct": 1.0},
                    "stats": {"up_streak": 0, "down_streak": 3},
                    "summary": "D",
                    "source": "akshare",
                },
            ],
            "count": 4,
            "filtered_from": 4,
            "total_symbols": 4,
            "partial_failure": False,
            "errors": [],
            "summary": "batch done",
        }


def test_watchlist_review_builds_statuses_rankings_and_buckets():
    uc = WatchlistReviewUseCase()
    uc.batch_review = _BatchReview()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH", "300750.SZ", "000001.SZ", "002594.SZ"],
            "watchlist_name": "核心池",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "akshare",
            "sort_by": "watchlist_score",
            "descending": True,
            "top_n": 3,
            "min_watchlist_score": None,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    result = uc.execute(req)

    assert result["subject_type"] == "watchlist"
    assert result["subject_name"] == "核心池"
    assert result["member_count"] == 4
    assert result["reviewed_count"] == 4
    assert result["items"][0]["symbol"] == "300750.SZ"
    assert result["items"][0]["status_label"] == "focus"
    assert result["items"][-1]["status_label"] == "risk_alert"
    assert result["breadth"]["focus_count"] == 1
    assert result["breadth"]["monitor_count"] >= 1
    assert result["breadth"]["risk_alert_count"] == 1
    assert result["buckets"]["focus"][0]["symbol"] == "300750.SZ"
    assert result["buckets"]["risk_alerts"][0]["symbol"] == "000001.SZ"
    assert result["rankings"]["leaders_by_watchlist_score"][0]["symbol"] == "300750.SZ"
    assert result["meta"]["watchlist_score_schema"]["schema"] == "watchlist_score_v1"
    assert result["meta"]["review_envelope_schema"]["schema"] == "review_envelope_v1"


def test_watchlist_review_applies_filters():
    uc = WatchlistReviewUseCase()
    uc.batch_review = _BatchReview()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH", "300750.SZ", "000001.SZ", "002594.SZ"],
            "watchlist_name": None,
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "akshare",
            "sort_by": "watchlist_score",
            "descending": True,
            "top_n": 10,
            "min_watchlist_score": 3.0,
            "min_relative_strength": 2.0,
            "min_return": 3.0,
            "max_drawdown_limit": 5.0,
            "min_volume_ratio": 1.2,
        },
    )()

    result = uc.execute(req)

    assert len(result["items"]) == 2
    assert result["items"][0]["symbol"] == "300750.SZ"
    assert result["items"][1]["symbol"] == "002594.SZ"


def test_watchlist_return_mode_ranked_only():
    from cn_stock_mcp.app.usecases.watchlist_review import WatchlistReviewUseCase

    class _Batch:
        def execute(self, req):
            return {
                "mode": "trade_date_review",
                "requested_trade_date": "2026-05-08",
                "requested_start_date": None,
                "requested_end_date": None,
                "items": [
                    {"symbol": "A", "relative_strength": 2, "return": 3, "max_drawdown": 1, "volume_ratio": 1.1, "tags": [], "stats": {}},
                    {"symbol": "B", "relative_strength": 1, "return": 2, "max_drawdown": 2, "volume_ratio": 1.0, "tags": [], "stats": {}},
                ],
                "partial_failure": False,
                "errors": [],
            }

    uc = WatchlistReviewUseCase()
    uc.batch_review = _Batch()
    req = type("Req", (), {"symbols":["A","B"],"watchlist_name":None,"trade_date":"2026-05-08","start_date":None,"end_date":None,"adjust":"none","provider":"akshare","sort_by":"watchlist_score","descending":True,"top_n":1,"min_watchlist_score":None,"min_relative_strength":None,"min_return":None,"max_drawdown_limit":None,"min_volume_ratio":None,"return_mode":"ranked_only"})()
    result = uc.execute(req)
    assert len(result["items"]) == 1
    assert result["meta"]["filters"]["return_mode"] == "ranked_only"

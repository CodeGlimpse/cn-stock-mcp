from cn_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase


class _Single:
    def execute(self, req):
        mapping = {
            "600519.SH": {"relative_strength_pct": -3.0, "return_pct": -5.0, "max_drawdown_pct": 9.0, "volume_ratio": 1.2, "up_streak": 0, "down_streak": 2},
            "000001.SZ": {"relative_strength_pct": 2.5, "return_pct": 3.0, "max_drawdown_pct": 2.0, "volume_ratio": 0.9, "up_streak": 2, "down_streak": 0},
            "300750.SZ": {"relative_strength_pct": 5.0, "return_pct": 8.0, "max_drawdown_pct": 4.0, "volume_ratio": 1.5, "up_streak": 3, "down_streak": 0},
        }
        stats = mapping[req.symbol]
        return {
            "symbol": req.symbol,
            "mode": "trade_date_review",
            "trade_date": req.trade_date,
            "latest_bar": type("Bar", (), {"close": 100.0})(),
            "benchmark": {"symbol": "000001.SH", "name": "上证指数"},
            "stats": stats,
            "summary": f"summary for {req.symbol}",
            "source": "akshare",
        }


def test_stock_review_batch_sorts_by_relative_strength_desc():
    uc = StockReviewBatchUseCase()
    uc.single = _Single()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH", "000001.SZ", "300750.SZ"],
            "trade_date": "2026-05-01",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "akshare",
            "sort_by": "relative_strength",
            "descending": True,
            "top_n": 2,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    result = uc.execute(req)

    assert result["count"] == 2
    assert result["items"][0]["symbol"] == "300750.SZ"
    assert result["items"][1]["symbol"] == "000001.SZ"
    assert "high_volume" in result["items"][0]["tags"]
    assert result["groups"]["strong_candidates"] >= 1
    assert result["summary"]


def test_stock_review_batch_applies_filters():
    uc = StockReviewBatchUseCase()
    uc.single = _Single()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH", "000001.SZ", "300750.SZ"],
            "trade_date": "2026-05-01",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "akshare",
            "sort_by": "return",
            "descending": True,
            "top_n": 5,
            "min_relative_strength": 1.0,
            "min_return": 1.0,
            "max_drawdown_limit": 5.0,
            "min_volume_ratio": 1.0,
        },
    )()

    result = uc.execute(req)

    assert result["count"] == 1
    assert result["items"][0]["symbol"] == "300750.SZ"


def test_stock_review_batch_keeps_input_order_for_error_collection_with_concurrency():
    class _SingleMaybeFail:
        def execute(self, req):
            if req.symbol == "000001.SZ":
                raise Exception("boom")
            stats = {
                "relative_strength_pct": 1.0,
                "return_pct": 2.0,
                "max_drawdown_pct": 1.0,
                "volume_ratio": 1.0,
                "up_streak": 0,
                "down_streak": 0,
            }
            return {
                "symbol": req.symbol,
                "mode": "trade_date_review",
                "trade_date": req.trade_date,
                "latest_bar": type("Bar", (), {"close": 100.0})(),
                "benchmark": {"symbol": "000001.SH", "name": "上证指数"},
                "stats": stats,
                "summary": f"summary for {req.symbol}",
                "source": "akshare",
            }

    uc = StockReviewBatchUseCase()
    original_run_single = uc._run_single

    def _fake_run_single(symbol, request):
        req = type(
            "Req",
            (),
            {
                "symbol": symbol,
                "trade_date": request.trade_date,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "adjust": request.adjust,
                "provider": request.provider,
            },
        )()
        try:
            return _SingleMaybeFail().execute(req)
        except Exception as exc:
            return exc

    uc._run_single = _fake_run_single

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH", "000001.SZ", "300750.SZ"],
            "trade_date": "2026-05-01",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "akshare",
            "sort_by": "return",
            "descending": True,
            "top_n": 5,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
        },
    )()

    result = uc.execute(req)

    assert result["partial_failure"] is True
    assert result["errors"][0]["symbol"] == "000001.SZ"
    uc._run_single = original_run_single

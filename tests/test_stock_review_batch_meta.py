from openclaw_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase


class _Single:
    def execute(self, req):
        mapping = {
            "600519.SH": {"relative_strength_20d": -3.0, "return_20d": -5.0, "max_drawdown_20d": 9.0, "volume_ratio_5d": 1.2, "up_streak": 0, "down_streak": 2},
            "000001.SZ": {"relative_strength_20d": 2.5, "return_20d": 3.0, "max_drawdown_20d": 2.0, "volume_ratio_5d": 0.9, "up_streak": 2, "down_streak": 0},
            "300750.SZ": {"relative_strength_20d": 5.0, "return_20d": 8.0, "max_drawdown_20d": 4.0, "volume_ratio_5d": 1.5, "up_streak": 3, "down_streak": 0},
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

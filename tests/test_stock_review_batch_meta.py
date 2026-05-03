from openclaw_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase


class _Single:
    def execute(self, req):
        mapping = {
            "600519.SH": {"relative_strength_20d": -3.0, "return_20d": -5.0, "max_drawdown_20d": 6.0, "volume_ratio_5d": 1.2},
            "000001.SZ": {"relative_strength_20d": 2.5, "return_20d": 3.0, "max_drawdown_20d": 2.0, "volume_ratio_5d": 0.9},
            "300750.SZ": {"relative_strength_20d": 5.0, "return_20d": 8.0, "max_drawdown_20d": 4.0, "volume_ratio_5d": 1.5},
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
        },
    )()

    result = uc.execute(req)

    assert result["count"] == 2
    assert result["items"][0]["symbol"] == "300750.SZ"
    assert result["items"][1]["symbol"] == "000001.SZ"
    assert result["summary"]

from cn_stock_mcp.server.schemas import StockReviewBatchRequest


def test_stock_review_batch_request_defaults_trade_date_when_empty():
    req = StockReviewBatchRequest(symbols=["600519.SH", "000001.SZ"])
    assert req.trade_date is not None
    assert req.sort_by == "relative_strength"
    assert req.top_n == 20
    assert req.min_relative_strength is None


def test_stock_review_batch_request_rejects_trade_date_with_range():
    try:
        StockReviewBatchRequest(symbols=["600519.SH"], trade_date="2026-05-01", start_date="2026-04-01", end_date="2026-05-01")
        assert False, "expected validation error"
    except Exception as exc:
        assert "trade_date cannot be combined" in str(exc)

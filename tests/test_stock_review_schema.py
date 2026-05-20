from cn_stock_mcp.server.schemas import StockReviewRequest


def test_stock_review_request_defaults_trade_date_when_empty():
    req = StockReviewRequest(symbol="600519.SH")
    assert req.trade_date is not None
    assert req.start_date is None
    assert req.end_date is None


def test_stock_review_request_rejects_trade_date_with_range():
    try:
        StockReviewRequest(symbol="600519.SH", trade_date="2026-05-01", start_date="2026-04-01", end_date="2026-05-01")
        assert False, "expected validation error"
    except Exception as exc:
        assert "trade_date cannot be combined" in str(exc)

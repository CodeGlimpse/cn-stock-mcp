import pytest
from pydantic import ValidationError

from cn_stock_mcp.server.schemas import HotThemeTrackerRequest, MultiTimeframeReviewRequest, WatchlistReviewRequest, StockCandidateScanRequest, SectorRotationReviewRequest, StockHistoryRequest, TechnicalIndicatorRequest, MarketPoolRequest, StockProfileRequest, EventCalendarRequest, SectorLeadersRequest


def test_stock_history_interval_alias_normalization():
    req = StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="d")
    assert req.interval == "1d"

    req2 = StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="15")
    assert req2.interval == "15m"


def test_stock_history_rejects_1m_interval():
    with pytest.raises(ValidationError) as exc:
        StockHistoryRequest(symbol="000001.SH", sec_type="index", interval="1m")

    assert "1m is not supported" in str(exc.value)


def test_technical_indicator_alias_normalization():
    req = TechnicalIndicatorRequest(symbol="000001.SH", sec_type="index", interval="m", indicator="MACD")
    assert req.interval == "1M"
    assert req.indicator == "macd"


def test_technical_indicator_rejects_1m_interval():
    with pytest.raises(ValidationError) as exc:
        TechnicalIndicatorRequest(symbol="000001.SH", sec_type="index", interval="1m", indicator="macd")

    assert "1m is not supported" in str(exc.value)


def test_sector_rotation_review_rejects_duplicate_or_blank_sector_list():
    with pytest.raises(ValidationError) as exc:
        SectorRotationReviewRequest(sector_names=["电力设备", " 电力设备 ", ""], trade_date="2026-05-06")

    assert "at least 2 distinct" in str(exc.value)


def test_stock_candidate_scan_requires_one_universe_source():
    with pytest.raises(ValidationError) as exc:
        StockCandidateScanRequest()

    assert "at least one of symbols/sector_names/pool_type" in str(exc.value)


def test_stock_candidate_scan_normalizes_pool_and_deduplicates_inputs():
    req = StockCandidateScanRequest(
        symbols=["600519.SH", "600519.SH", " 000001.SZ "],
        sector_names=[" 1000信息 ", "1000信息", "1000工业"],
        pool_type="涨停",
        trade_date="2026-05-06",
    )

    assert req.pool_type == "limit_up"
    assert req.symbols == ["600519.SH", "000001.SZ"]
    assert req.sector_names == ["1000信息", "1000工业"]


def test_market_pool_request_supports_new_pool_aliases():
    sub_new = MarketPoolRequest(pool_type="次新")
    broken_limit = MarketPoolRequest(pool_type="zbgc")

    assert sub_new.pool_type == "sub_new"
    assert broken_limit.pool_type == "broken_limit"


def test_watchlist_review_normalizes_symbols_and_defaults_trade_date():
    req = WatchlistReviewRequest(symbols=[" 600519.SH ", "600519.SH", "000001.SZ"], watchlist_name="  核心池  ")
    assert req.symbols == ["600519.SH", "000001.SZ"]
    assert req.watchlist_name == "核心池"
    assert req.trade_date is not None


def test_watchlist_review_rejects_trade_date_with_range():
    with pytest.raises(ValidationError) as exc:
        WatchlistReviewRequest(symbols=["600519.SH"], trade_date="2026-05-06", start_date="2026-04-01", end_date="2026-05-01")

    assert "trade_date cannot be combined" in str(exc.value)


def test_multi_timeframe_review_normalizes_intervals_and_defaults_indicators():
    req = MultiTimeframeReviewRequest(symbol="600519.SH", intervals=["15", "d", "w", "15"])
    assert req.intervals == ["15m", "1d", "1w"]
    assert req.indicators == ["macd", "ma", "kdj"]


def test_multi_timeframe_review_requires_two_distinct_intervals():
    with pytest.raises(ValidationError) as exc:
        MultiTimeframeReviewRequest(symbol="600519.SH", intervals=["d", "1d"])

    assert "at least 2 distinct" in str(exc.value)


def test_stock_candidate_scan_request_new_filter_fields():
    from cn_stock_mcp.server.schemas import StockCandidateScanRequest

    req = StockCandidateScanRequest(
        symbols=["600519.SH"],
        require_source_tags=[" pool:strong ", "pool:strong"],
        exclude_risk_flags=[" weak_relative_strength ", ""],
        min_up_streak=2,
        max_down_streak=3,
    )

    assert req.require_source_tags == ["pool:strong"]
    assert req.exclude_risk_flags == ["weak_relative_strength"]


def test_stock_candidate_scan_request_reason_tag_filters():
    from cn_stock_mcp.server.schemas import StockCandidateScanRequest

    req = StockCandidateScanRequest(
        symbols=["600519.SH"],
        must_have_reason_tags=[" strong_return ", "high_volume", "strong_return"],
        exclude_reason_tags=[" slight_positive_return ", ""],
    )

    assert req.must_have_reason_tags == ["strong_return", "high_volume"]
    assert req.exclude_reason_tags == ["slight_positive_return"]


def test_hot_theme_tracker_request_requires_two_distinct_sector_names_when_provided():
    with pytest.raises(ValidationError) as exc:
        HotThemeTrackerRequest(sector_names=["1000信息", " 1000信息 "])

    assert "at least 2 distinct" in str(exc.value)


def test_stock_profile_request_supports_valuation_include():
    req = StockProfileRequest(symbol='000001.SZ', include=['profile', 'valuation'])
    assert req.include == ['profile', 'valuation']


def test_event_calendar_request_validation():
    req = EventCalendarRequest(symbols=["600519.SH"], event_types=["dividend", "dividend", "unlock"], start_date="2026-05-01", end_date="2026-05-31")
    assert req.event_types == ["dividend", "unlock"]


def test_sector_leaders_request_defaults():
    req = SectorLeadersRequest(sector_name="1000信息")
    assert req.top_n == 3
    assert req.trade_date is not None


def test_event_calendar_request_next_event_only():
    req = EventCalendarRequest(symbols=["600519.SH"], next_event_only=True)
    assert req.next_event_only is True


def test_event_calendar_request_event_priority():
    req = EventCalendarRequest(symbols=["600519.SH"], event_priority=["unlock", "dividend", "unlock"])
    assert req.event_priority == ["unlock", "dividend"]

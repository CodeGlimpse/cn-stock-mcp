import pytest
from pydantic import ValidationError

from openclaw_stock_mcp.server.schemas import StockCandidateScanRequest, SectorRotationReviewRequest, StockHistoryRequest, TechnicalIndicatorRequest


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

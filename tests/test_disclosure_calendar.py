"""Tests for disclosure_calendar usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.disclosure_calendar import DisclosureCalendarUseCase
from cn_stock_mcp.server.schemas import DisclosureCalendarRequest


def _make_rows():
    return [
        {"股票代码": "000001", "股票简称": "平安银行", "首次预约": "2025-03-15", "初次变更": None, "二次变更": None, "三次变更": None, "实际披露": "2025-03-15"},
        {"股票代码": "000002", "股票简称": "万科A", "首次预约": "2025-03-29", "初次变更": "2025-04-01", "二次变更": None, "三次变更": None, "实际披露": "2025-04-01"},
        {"股票代码": "600519", "股票简称": "贵州茅台", "首次预约": "2025-04-26", "初次变更": None, "二次变更": None, "三次变更": None, "实际披露": None},
    ]


def test_disclosure_calendar_all():
    uc = DisclosureCalendarUseCase()
    mock_provider = MagicMock()
    mock_provider.get_disclosure_calendar.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="2024年报")
        result = uc.execute(req)
    assert result["total_count"] == 3


def test_disclosure_calendar_filter_disclosed():
    uc = DisclosureCalendarUseCase()
    mock_provider = MagicMock()
    mock_provider.get_disclosure_calendar.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="2024年报", status="disclosed")
        result = uc.execute(req)
    # 平安银行 and 万科A have actual_date
    assert result["total_count"] == 2


def test_disclosure_calendar_filter_pending():
    uc = DisclosureCalendarUseCase()
    mock_provider = MagicMock()
    mock_provider.get_disclosure_calendar.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="2024年报", status="pending")
        result = uc.execute(req)
    # Only 茅台 has no actual_date
    assert result["total_count"] == 1
    assert result["items"][0]["symbol"] == "600519.SH"


def test_disclosure_calendar_filter_changed():
    uc = DisclosureCalendarUseCase()
    mock_provider = MagicMock()
    mock_provider.get_disclosure_calendar.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="2024年报", status="changed")
        result = uc.execute(req)
    # 万科A has change_1
    assert result["total_count"] == 1


def test_disclosure_calendar_auto_period():
    uc = DisclosureCalendarUseCase()
    mock_provider = MagicMock()
    mock_provider.get_disclosure_calendar.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="auto")
        result = uc.execute(req)
    # period should be resolved
    assert result["period"] != "auto"


def test_disclosure_calendar_top_n():
    uc = DisclosureCalendarUseCase()
    mock_provider = MagicMock()
    mock_provider.get_disclosure_calendar.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="2024年报", top_n=2)
        result = uc.execute(req)
    assert result["total_count"] == 2


def test_disclosure_calendar_uses_cache():
    uc = DisclosureCalendarUseCase()
    raw = _make_rows()
    uc.cache.set("disclosure:沪深京:2024年报", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="2024年报")
        result = uc.execute(req)
    mock_provider.get_disclosure_calendar.assert_not_called()
    assert result["total_count"] == 3


def test_disclosure_summary():
    uc = DisclosureCalendarUseCase()
    mock_provider = MagicMock()
    mock_provider.get_disclosure_calendar.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DisclosureCalendarRequest(period="2024年报")
        result = uc.execute(req)
    assert "披露日历" in result["summary"]

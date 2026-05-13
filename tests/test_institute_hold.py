"""Tests for institute_hold usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from openclaw_stock_mcp.app.usecases.institute_hold import InstituteHoldUseCase
from openclaw_stock_mcp.server.schemas import InstituteHoldRequest


def _make_summary_rows():
    return [
        {
            "序号": 1,
            "证券代码": "600519",
            "证券简称": "贵州茅台",
            "机构数": 800,
            "机构数变化": 20,
            "持股比例": 55.3,
            "持股比例增幅": 1.2,
            "占流通股比例": 62.1,
            "占流通股比例增幅": -0.5,
        }
    ]


def _make_detail_rows():
    return [
        {
            "序号": 1,
            "持股机构类型": "基金",
            "持股机构代码": "000001",
            "持股机构简称": "华夏成长",
            "持股机构全称": "华夏成长混合型证券投资基金",
            "持股数": 1000000,
            "最新持股数": 1200000,
            "持股比例": 0.8,
            "最新持股比例": 0.96,
            "占流通股比例": 0.5,
            "最新占流通股比例": 0.6,
            "持股比例增幅": 0.16,
            "占流通股比例增幅": 0.1,
        }
    ]


def test_institute_hold_summary():
    uc = InstituteHoldUseCase()
    mock_provider = MagicMock()
    mock_provider.get_institute_hold.return_value = _make_summary_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InstituteHoldRequest(include=["summary"], quarter="20243")
        result = uc.execute(req)
    assert result["summary_count"] == 1
    item = result["summary"][0]
    assert item["symbol"] == "600519.SH"
    assert item["institute_count"] == 800
    assert item["hold_ratio"] == 55.3
    assert item["hold_ratio_change"] == 1.2


def test_institute_hold_detail():
    uc = InstituteHoldUseCase()
    mock_provider = MagicMock()
    mock_provider.get_institute_hold_detail.return_value = _make_detail_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InstituteHoldRequest(include=["detail"], quarter="20243", symbol="600519.SH")
        result = uc.execute(req)
    assert result["detail_count"] == 1
    item = result["detail"][0]
    assert item["institute_type"] == "基金"
    assert item["institute_name"] == "华夏成长"
    assert item["hold_ratio_change"] == 0.16


def test_institute_hold_detail_requires_symbol():
    from pydantic import ValidationError
    try:
        InstituteHoldRequest(include=["detail"], quarter="20243")
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "symbol is required" in str(e)


def test_institute_hold_auto_quarter():
    uc = InstituteHoldUseCase()
    mock_provider = MagicMock()
    mock_provider.get_institute_hold.return_value = []
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InstituteHoldRequest(include=["summary"], quarter="auto")
        result = uc.execute(req)
    assert result["effective_quarter"] != "auto"
    # Should be a valid YYYYQ format
    eq = result["effective_quarter"]
    assert len(eq) == 5
    assert eq[:4].isdigit()
    assert eq[4] in "1234"


def test_institute_hold_top_n():
    uc = InstituteHoldUseCase()
    mock_provider = MagicMock()
    rows = _make_summary_rows() * 10
    mock_provider.get_institute_hold.return_value = rows
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InstituteHoldRequest(include=["summary"], quarter="20243", top_n=3)
        result = uc.execute(req)
    assert result["summary_count"] == 3


def test_institute_hold_summary_text():
    uc = InstituteHoldUseCase()
    mock_provider = MagicMock()
    mock_provider.get_institute_hold.return_value = _make_summary_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InstituteHoldRequest(include=["summary"], quarter="20243")
        result = uc.execute(req)
    assert "20243" in result["summary_text"]
    assert "机构持仓汇总" in result["summary_text"]

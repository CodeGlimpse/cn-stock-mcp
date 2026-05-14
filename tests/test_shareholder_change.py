"""Tests for shareholder_change usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from openclaw_stock_mcp.app.usecases.shareholder_change import ShareholderChangeUseCase
from openclaw_stock_mcp.server.schemas import ShareholderChangeRequest


def _make_top10_rows():
    return [
        {"名次": 1, "股东名称": "中国贵州茅台酒厂(集团)有限责任公司", "股份类型": "流通A股", "持股数": 679957491, "占总股本持股比例": 54.30, "增减": 678094, "变动比率": 0.10},
        {"名次": 2, "股东名称": "香港中央结算有限公司", "股份类型": "流通A股", "持股数": 61040802, "占总股本持股比例": 4.87, "增减": -11825397, "变动比率": -16.23},
        {"名次": 3, "股东名称": "贵州省国有资本运营有限责任公司", "股份类型": "流通A股", "持股数": 56996777, "占总股本持股比例": 4.55, "增减": "不变", "变动比率": "NaN"},
    ]


def _make_change_rows():
    return [
        {"序号": 1, "股东名称": "华夏基金", "股东类型": "基金", "期末持股只数统计-总持有": 150, "期末持股只数统计-新进": 10, "期末持股只数统计-增加": 20, "期末持股只数统计-不变": 80, "期末持股只数统计-减少": 30, "流通市值统计": 5000000000.0, "持有个股": "600519,000858"},
        {"序号": 2, "股东名称": "全国社保基金", "股东类型": "社保", "期末持股只数统计-总持有": 80, "期末持股只数统计-新进": 5, "期末持股只数统计-增加": 15, "期末持股只数统计-不变": 40, "期末持股只数统计-减少": 20, "流通市值统计": 3000000000.0, "持有个股": "600036,601318"},
    ]


def test_shareholder_top10():
    uc = ShareholderChangeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_shareholder_top10.return_value = _make_top10_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = ShareholderChangeRequest(include=["top10"], symbol="600519.SH", quarter="20254")
        result = uc.execute(req)
    assert result["top10_count"] == 3
    item = result["top10"][0]
    assert item["shareholder_name"] == "中国贵州茅台酒厂(集团)有限责任公司"
    assert item["hold_ratio"] == 54.30


def test_shareholder_change():
    uc = ShareholderChangeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_shareholder_change.return_value = _make_change_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = ShareholderChangeRequest(include=["change"], quarter="20254", sort_by="total_hold", top_n=10)
        result = uc.execute(req)
    assert result["change_count"] == 2
    item = result["change"][0]
    assert item["shareholder_name"] == "华夏基金"
    assert item["shareholder_type"] == "基金"
    assert item["total_hold"] == 150


def test_shareholder_change_filter_type():
    uc = ShareholderChangeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_shareholder_change.return_value = _make_change_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = ShareholderChangeRequest(include=["change"], quarter="20254", shareholder_type="社保")
        result = uc.execute(req)
    assert result["change_count"] == 1
    assert result["change"][0]["shareholder_type"] == "社保"


def test_shareholder_top10_requires_symbol():
    from pydantic import ValidationError
    try:
        ShareholderChangeRequest(include=["top10"])
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "symbol is required" in str(e)


def test_shareholder_auto_quarter():
    uc = ShareholderChangeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_shareholder_top10.return_value = _make_top10_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = ShareholderChangeRequest(include=["top10"], symbol="600519.SH", quarter="auto")
        result = uc.execute(req)
    assert result["quarter"] != "auto"
    assert len(result["quarter"]) == 8  # YYYYMMDD


def test_shareholder_change_uses_cache():
    uc = ShareholderChangeUseCase()
    raw = _make_change_rows()
    uc.change_cache.set("shareholder:change:20250930", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = ShareholderChangeRequest(include=["change"], quarter="20254")
        result = uc.execute(req)
    mock_provider.get_shareholder_change.assert_not_called()
    assert result["change_count"] == 2


def test_shareholder_summary():
    uc = ShareholderChangeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_shareholder_top10.return_value = _make_top10_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = ShareholderChangeRequest(include=["top10"], symbol="600519.SH", quarter="20254")
        result = uc.execute(req)
    assert "十大股东" in result["summary"]

"""Tests for insider_trade usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.insider_trade import InsiderTradeUseCase
from cn_stock_mcp.server.schemas import InsiderTradeRequest


def _make_top10_rows():
    return [
        {
            "名次": 1,
            "股东名称": "中国贵州茅台酒厂(集团)有限责任公司",
            "股东性质": "其它",
            "股份类型": "A股",
            "持股数": 679957491,
            "占总流通股本持股比例": 54.30,
            "增减": 745915,
            "变动比率": 0.11,
        },
        {
            "名次": 2,
            "股东名称": "香港中央结算有限公司",
            "股东性质": "其它",
            "股份类型": "A股",
            "持股数": 61040802,
            "占总流通股本持股比例": 4.87,
            "增减": -11825397,
            "变动比率": -16.23,
        },
        {
            "名次": 3,
            "股东名称": "贵州省国有资本运营有限责任公司",
            "股东性质": "投资公司",
            "股份类型": "A股",
            "持股数": 56996777,
            "占总流通股本持股比例": 4.55,
            "增减": "不变",
            "变动比率": "NaN",
        },
    ]


def _make_change_rows():
    return [
        {
            "公告日期": "2024-06-15",
            "变动股东": "中国贵州茅台酒厂(集团)有限责任公司",
            "变动数量": "增持45.25万",
            "交易均价": "未披露",
            "剩余股份总数": "6.42亿",
            "变动期间": "2024.06.11-2024.06.11",
            "变动途径": "二级市场",
        },
        {
            "公告日期": "2023-12-12",
            "变动股东": "某某高管",
            "变动数量": "减持8.23万",
            "交易均价": "1800.5",
            "剩余股份总数": "5.0万",
            "变动期间": "2023.12.11-2023.12.11",
            "变动途径": "二级市场",
        },
    ]


def test_insider_trade_top10():
    uc = InsiderTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_insider_top10.return_value = _make_top10_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InsiderTradeRequest(include=["top10"], symbol="600519.SH", quarter="20254")
        result = uc.execute(req)
    assert result["top10_count"] == 3
    item = result["top10"][0]
    assert item["shareholder_name"] == "中国贵州茅台酒厂(集团)有限责任公司"
    assert item["hold_ratio"] == 54.30
    assert item["change_ratio"] == 0.11


def test_insider_trade_change():
    uc = InsiderTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_insider_change.return_value = _make_change_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InsiderTradeRequest(include=["change"], symbol="600519.SH", quarter="auto")
        result = uc.execute(req)
    assert result["change_count"] == 2
    item = result["change"][0]
    assert item["shareholder_name"] == "中国贵州茅台酒厂(集团)有限责任公司"
    assert "增持" in item["change_count"]


def test_insider_trade_both():
    uc = InsiderTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_insider_top10.return_value = _make_top10_rows()
    mock_provider.get_insider_change.return_value = _make_change_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InsiderTradeRequest(include=["top10", "change"], symbol="600519.SH", quarter="20254")
        result = uc.execute(req)
    assert result["top10_count"] == 3
    assert result["change_count"] == 2
    assert "增持" in result["summary"]


def test_insider_trade_auto_quarter():
    uc = InsiderTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_insider_top10.return_value = _make_top10_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InsiderTradeRequest(include=["top10"], symbol="600519.SH", quarter="auto")
        result = uc.execute(req)
    assert result["quarter"] != "auto"
    eq = result["quarter"]
    assert len(eq) == 8  # YYYYMMDD format


def test_insider_trade_top_n():
    uc = InsiderTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_insider_top10.return_value = _make_top10_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InsiderTradeRequest(include=["top10"], symbol="600519.SH", quarter="20254", top_n=2)
        result = uc.execute(req)
    assert result["top10_count"] == 2


def test_insider_trade_top10_unchanged():
    uc = InsiderTradeUseCase()
    mock_provider = MagicMock()
    mock_provider.get_insider_top10.return_value = _make_top10_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = InsiderTradeRequest(include=["top10"], symbol="600519.SH", quarter="20254")
        result = uc.execute(req)
    # 3rd item has "不变" change
    item3 = result["top10"][2]
    assert item3["change"] == "不变"
    assert item3["change_ratio"] is None  # "NaN" → None

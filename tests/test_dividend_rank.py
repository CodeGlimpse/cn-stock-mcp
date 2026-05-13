"""Tests for dividend_rank usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from openclaw_stock_mcp.app.usecases.dividend_rank import DividendRankUseCase
from openclaw_stock_mcp.server.schemas import DividendRankRequest


def _make_rank_rows():
    return [
        {"代码": "000550", "名称": "江铃汽车", "上市日期": "1993-12-01", "累计股息": 220.1, "年均股息": 6.88, "分红次数": 53, "融资总额": 0, "融资次数": 0},
        {"代码": "000541", "名称": "佛山照明", "上市日期": "1993-11-23", "累计股息": 195.7, "年均股息": 6.12, "分红次数": 58, "融资总额": 10.88, "融资次数": 1},
        {"代码": "000429", "名称": "粤高速A", "上市日期": "1998-02-20", "累计股息": 179.6, "年均股息": 6.41, "分红次数": 52, "融资总额": 16.34, "融资次数": 1},
    ]


def _make_plan_rows():
    return [
        {"代码": "600535", "名称": "天士力", "送转股份-送转比例": None, "送转股份-转股比例": None, "现金分红-现金分红比例": 2.0, "现金分红-股息率": 0.0134, "每股收益": 0.64, "每股净资产": 7.97, "每股公积金": 0.31, "每股未分配利润": 5.46, "净利润同比增长": -10.78, "总股本": 1493950005, "预案公告日": "2025-02-25", "股权登记日": "2025-03-25", "除权除息日": "2025-03-26", "方案进度": "实施分配", "最新公告日期": "2025-03-20"},
        {"代码": "600519", "名称": "贵州茅台", "送转股份-送转比例": None, "送转股份-转股比例": None, "现金分红-现金分红比例": 30.87, "现金分红-股息率": 0.0172, "每股收益": 54.66, "每股净资产": 178.42, "每股公积金": 1.58, "每股未分配利润": 148.37, "净利润同比增长": 5.10, "总股本": 1256197860, "预案公告日": "2025-04-03", "股权登记日": "2025-06-18", "除权除息日": "2025-06-19", "方案进度": "实施分配", "最新公告日期": "2025-06-13"},
    ]


def _make_detail_rows():
    return [
        {"公告日期": "2023-08-21", "送股": 0.0, "转增": 0, "派息": 6.80, "进度": "实施", "除权除息日": "2023-08-25", "股权登记日": "2023-08-24", "红股上市日": "NaT"},
        {"公告日期": "2022-08-18", "送股": 0.0, "转增": 0, "派息": 9.76, "进度": "实施", "除权除息日": "2022-08-25", "股权登记日": "2022-08-24", "红股上市日": "NaT"},
        {"公告日期": "2024-03-29", "送股": 0.0, "转增": 0, "派息": 0.00, "进度": "不分配", "除权除息日": "NaT", "股权登记日": "NaT", "红股上市日": "NaT"},
    ]


def test_dividend_rank():
    uc = DividendRankUseCase()
    mock_provider = MagicMock()
    mock_provider.get_dividend_history_rank.return_value = _make_rank_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DividendRankRequest(include=["rank"], sort_by="avg_annual_dividend", top_n=3)
        result = uc.execute(req)
    assert result["rank_count"] == 3
    item = result["rank"][0]
    assert item["symbol"] == "000550.SZ"
    assert item["avg_annual_dividend"] == 6.88
    assert item["dividend_count"] == 53


def test_dividend_plan():
    uc = DividendRankUseCase()
    mock_provider = MagicMock()
    mock_provider.get_dividend_plan.return_value = _make_plan_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DividendRankRequest(include=["plan"], report_date="20241231", sort_by="dividend_yield")
        result = uc.execute(req)
    assert result["plan_count"] == 2
    # Sorted by dividend_yield desc: 茅台 0.0172 > 天士力 0.0134
    item = result["plan"][0]
    assert item["symbol"] == "600519.SH"
    assert item["dividend_yield"] == 0.0172


def test_dividend_detail():
    uc = DividendRankUseCase()
    mock_provider = MagicMock()
    mock_provider.get_dividend_detail.return_value = _make_detail_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DividendRankRequest(include=["detail"], symbol="000002.SZ", top_n=10)
        result = uc.execute(req)
    assert result["detail_count"] == 3
    item = result["detail"][0]
    assert item["cash_dividend"] == 6.80
    assert item["progress"] == "实施"


def test_dividend_detail_requires_symbol():
    from pydantic import ValidationError
    try:
        DividendRankRequest(include=["detail"])
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "symbol is required" in str(e)


def test_dividend_uses_cache():
    uc = DividendRankUseCase()
    raw = _make_rank_rows()
    uc.rank_cache.set("dividend:history_rank", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DividendRankRequest(include=["rank"], top_n=3)
        result = uc.execute(req)
    mock_provider.get_dividend_history_rank.assert_not_called()
    assert result["rank_count"] == 3


def test_dividend_latest_report_date():
    uc = DividendRankUseCase()
    mock_provider = MagicMock()
    mock_provider.get_dividend_plan.return_value = _make_plan_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DividendRankRequest(include=["plan"], report_date="latest")
        result = uc.execute(req)
    # Should call with YYYY1231 format
    call_args = mock_provider.get_dividend_plan.call_args
    assert call_args[1]["date"].endswith("1231")


def test_dividend_summary():
    uc = DividendRankUseCase()
    mock_provider = MagicMock()
    mock_provider.get_dividend_history_rank.return_value = _make_rank_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = DividendRankRequest(include=["rank"], top_n=3)
        result = uc.execute(req)
    assert "历史分红排名" in result["summary"]

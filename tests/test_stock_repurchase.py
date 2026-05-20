"""Tests for stock_repurchase usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.stock_repurchase import StockRepurchaseUseCase
from cn_stock_mcp.server.schemas import StockRepurchaseRequest


def _make_rows():
    return [
        {"序号": 1, "股票代码": "300347", "股票简称": "泰格医药", "最新价": 49.09, "计划回购价格区间": 60.0, "计划回购数量区间-下限": 8333333.0, "计划回购数量区间-上限": 16666666.0, "占公告前一日总股本比例-下限": 0.97, "占公告前一日总股本比例-上限": 1.94, "计划回购金额区间-下限": 500000000.0, "计划回购金额区间-上限": 1000000000.0, "回购起始时间": "2026-05-13", "实施进度": "董事会预案", "已回购股份价格区间-下限": None, "已回购股份价格区间-上限": None, "已回购股份数量": None, "已回购金额": None, "最新公告日期": "2026-05-14"},
        {"序号": 2, "股票代码": "002959", "股票简称": "小熊电器", "最新价": 40.27, "计划回购价格区间": 65.0, "计划回购数量区间-下限": 1153847.0, "计划回购数量区间-上限": 2307692.0, "占公告前一日总股本比例-下限": 0.74, "占公告前一日总股本比例-上限": 1.48, "计划回购金额区间-下限": 794600.0, "计划回购金额区间-上限": 794600.0, "回购起始时间": "2026-04-24", "实施进度": "实施中", "已回购股份价格区间-下限": 39.69, "已回购股份价格区间-上限": 39.77, "已回购股份数量": 20000.0, "已回购金额": 794600.0, "最新公告日期": "2026-05-14"},
        {"序号": 3, "股票代码": "688108", "股票简称": "赛诺医疗", "最新价": 22.49, "计划回购价格区间": 35.1, "计划回购数量区间-下限": 428000.0, "计划回购数量区间-上限": 854000.0, "占公告前一日总股本比例-下限": 0.10, "占公告前一日总股本比例-上限": 0.20, "计划回购金额区间-下限": 19925390.0, "计划回购金额区间-上限": 19925390.0, "回购起始时间": "2026-02-25", "实施进度": "完成实施", "已回购股份价格区间-下限": 21.58, "已回购股份价格区间-上限": 22.22, "已回购股份数量": 910000.0, "已回购金额": 19925388.88, "最新公告日期": "2026-05-14"},
    ]


def test_repurchase_all():
    uc = StockRepurchaseUseCase()
    mock_provider = MagicMock()
    mock_provider.get_stock_repurchase.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockRepurchaseRequest()
        result = uc.execute(req)
    assert result["total_count"] == 3


def test_repurchase_filter_status():
    uc = StockRepurchaseUseCase()
    mock_provider = MagicMock()
    mock_provider.get_stock_repurchase.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockRepurchaseRequest(status="实施中")
        result = uc.execute(req)
    assert result["total_count"] == 1
    assert result["items"][0]["progress"] == "实施中"


def test_repurchase_filter_completed():
    uc = StockRepurchaseUseCase()
    mock_provider = MagicMock()
    mock_provider.get_stock_repurchase.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockRepurchaseRequest(status="完成实施")
        result = uc.execute(req)
    assert result["total_count"] == 1
    assert result["items"][0]["name"] == "赛诺医疗"


def test_repurchase_sort_by_amount():
    uc = StockRepurchaseUseCase()
    mock_provider = MagicMock()
    mock_provider.get_stock_repurchase.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockRepurchaseRequest(sort_by="done_amount", descending=True)
        result = uc.execute(req)
    # 实施中(794600) > 完成实施(19925388.88) > 董事会预案(None)
    # None goes to -inf when descending, so completed first
    assert result["items"][0]["done_amount"] == 19925388.88


def test_repurchase_top_n():
    uc = StockRepurchaseUseCase()
    mock_provider = MagicMock()
    mock_provider.get_stock_repurchase.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockRepurchaseRequest(top_n=2)
        result = uc.execute(req)
    assert result["total_count"] == 2


def test_repurchase_uses_cache():
    uc = StockRepurchaseUseCase()
    raw = _make_rows()
    uc.cache.set("repurchase:all", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockRepurchaseRequest()
        result = uc.execute(req)
    mock_provider.get_stock_repurchase.assert_not_called()
    assert result["total_count"] == 3


def test_repurchase_summary():
    uc = StockRepurchaseUseCase()
    mock_provider = MagicMock()
    mock_provider.get_stock_repurchase.return_value = _make_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = StockRepurchaseRequest()
        result = uc.execute(req)
    assert "回购明细" in result["summary"]
    assert "已回购总额" in result["summary"]

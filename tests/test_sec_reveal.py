"""Tests for sec_reveal usecase with mocked provider."""
from unittest.mock import MagicMock, patch

import pytest

from cn_stock_mcp.app.usecases.sec_reveal import SecRevealUseCase
from cn_stock_mcp.server.schemas import SecRevealRequest


def _make_buy_rows():
    return [
        {"序号": 1, "交易营业部名称": "华源证券股份有限公司湖北分公司", "买入金额": 17740800.0, "买入金额-占总成交比例": 0.409811, "卖出金额": 0, "卖出金额-占总成交比例": 0.0, "净额": 17740800.0, "类型": "日涨幅达到15%的前5只证券"},
        {"序号": 2, "交易营业部名称": "德邦证券股份有限公司上海乍浦路证券营业部", "买入金额": 13099680.0, "买入金额-占总成交比例": 0.302601, "卖出金额": 0, "卖出金额-占总成交比例": 0.0, "净额": 13099680.0, "类型": "日涨幅达到15%的前5只证券"},
    ]


def _make_sell_rows():
    return [
        {"序号": 1, "交易营业部名称": "国信证券股份有限公司佛山南海大沥证券营业部", "买入金额": 0, "买入金额-占总成交比例": 0, "卖出金额": 2534400, "卖出金额-占总成交比例": 0.058544, "净额": -2534400, "类型": "日涨幅达到15%的前5只证券"},
    ]


def _make_active_broker_rows():
    return [
        {"序号": 1, "营业部名称": "深股通专用", "上榜日": "2026-05-13", "买入个股数": 21, "卖出个股数": 25, "买入总金额": 4.578355e9, "卖出总金额": 4.032348e9, "总买卖净额": 5.460066e8, "买入股票": "韶能股份 晋控电力", "营业部代码": "10634757"},
        {"序号": 2, "营业部名称": "广发证券股份有限公司上海浦东新区东方路证券营业部", "上榜日": "2026-05-13", "买入个股数": 2, "卖出个股数": 0, "买入总金额": 4.991726e8, "卖出总金额": 0, "总买卖净额": 4.991726e8, "买入股票": "天准科技 普冉股份", "营业部代码": "10140582"},
    ]


def _make_inst_detail_rows():
    return [
        {"股票代码": "688766", "股票名称": "普冉股份", "交易日期": "2026-05-13", "机构席位买入额": 37813.50, "机构席位卖出额": 76860.40, "类型": None},
        {"股票代码": "688146", "股票名称": "中船特气", "交易日期": "2026-05-13", "机构席位买入额": 22500.38, "机构席位卖出额": 0.0, "类型": None},
    ]


def _make_inst_trace_rows():
    return [
        {"股票代码": "000066", "股票名称": "中国长城", "累积买入额": 266603.70, "买入次数": 5, "累积卖出额": 168342.53, "卖出次数": 5, "净额": 98261.17},
        {"股票代码": "001309", "股票名称": "德明利", "累积买入额": 173933.70, "买入次数": 3, "累积卖出额": 76138.72, "卖出次数": 3, "净额": 97794.98},
    ]


def test_sec_reveal_stock_seat_detail():
    uc = SecRevealUseCase()
    mock_provider = MagicMock()
    mock_provider.get_lhb_stock_seat_detail.side_effect = [_make_buy_rows(), _make_sell_rows()]
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = SecRevealRequest(include=["stock_seat_detail"], symbol="300965", trade_date="20260513")
        result = uc.execute(req)
    assert result["stock_seat_buy_count"] == 2
    assert result["stock_seat_sell_count"] == 1
    assert result["stock_seat_buy"][0]["broker_name"] == "华源证券股份有限公司湖北分公司"
    assert "分公司" in result["stock_seat_buy"][0]["broker_tags"]
    assert result["stock_seat_sell"][0]["net_amount"] == -2534400
    assert "知名游资" in result["stock_seat_sell"][0]["broker_tags"]
    assert result["broker_tag_summary"]["营业部"] >= 2


def test_sec_reveal_active_broker():
    uc = SecRevealUseCase()
    mock_provider = MagicMock()
    mock_provider.get_lhb_active_broker.return_value = _make_active_broker_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = SecRevealRequest(include=["active_broker"], start_date="20260513", end_date="20260513", top_n=1)
        result = uc.execute(req)
    assert result["active_broker_count"] == 1
    assert result["active_broker"][0]["broker_name"] == "深股通专用"
    assert result["active_broker"][0]["broker_tags"] == ["陆股通"]


def test_sec_reveal_institution_detail_and_trace():
    uc = SecRevealUseCase()
    mock_provider = MagicMock()
    mock_provider.get_lhb_institution_detail_sina.return_value = _make_inst_detail_rows()
    mock_provider.get_lhb_institution_trace_sina.return_value = _make_inst_trace_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = SecRevealRequest(include=["institution_detail", "institution_trace"], sort_by="inst_net_amount", top_n=2)
        result = uc.execute(req)
    assert result["institution_detail_count"] == 2
    assert result["institution_trace_count"] == 2
    assert result["institution_detail"][0]["name"] == "中船特气"
    assert result["institution_detail"][0]["inst_net_amount"] == pytest.approx(22500.38)


def test_sec_reveal_filter_symbol():
    uc = SecRevealUseCase()
    mock_provider = MagicMock()
    mock_provider.get_lhb_institution_detail_sina.return_value = _make_inst_detail_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = SecRevealRequest(include=["institution_detail"], symbol="688766")
        result = uc.execute(req)
    assert result["institution_detail_count"] == 1
    assert result["institution_detail"][0]["code"] == "688766"


def test_sec_reveal_requires_symbol_for_stock_detail():
    with pytest.raises(ValueError, match="symbol is required"):
        SecRevealRequest(include=["stock_seat_detail"])


def test_sec_reveal_uses_cache():
    uc = SecRevealUseCase()
    uc.cache.set("secreveal:seat:300965:20260513", {"buy": _make_buy_rows(), "sell": _make_sell_rows()})
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = SecRevealRequest(include=["stock_seat_detail"], symbol="300965", trade_date="20260513")
        result = uc.execute(req)
    mock_provider.get_lhb_stock_seat_detail.assert_not_called()
    assert result["stock_seat_buy_count"] == 2

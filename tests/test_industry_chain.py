"""Tests for industry_chain usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.industry_chain import IndustryChainUseCase
from cn_stock_mcp.server.schemas import IndustryChainRequest


def _make_industry_rows():
    return [
        {"板块": "白色家电", "涨跌幅": 2.15, "总成交量": 1200000000, "总成交额": 35000000000, "净流入": 1500000000, "上涨家数": 25, "下跌家数": 5, "均价": 42.5, "领涨股": "海尔智家", "领涨股-最新价": 28.5, "领涨股-涨跌幅": 4.32},
        {"板块": "白酒", "涨跌幅": 1.50, "总成交量": 800000000, "总成交额": 95000000000, "净流入": 3200000000, "上涨家数": 15, "下跌家数": 5, "均价": 350.0, "领涨股": "贵州茅台", "领涨股-最新价": 1800.0, "领涨股-涨跌幅": 0.56},
        {"板块": "光伏", "涨跌幅": -1.20, "总成交量": 2000000000, "总成交额": 45000000000, "净流入": -800000000, "上涨家数": 8, "下跌家数": 30, "均价": 18.3, "领涨股": "阳光电源", "领涨股-最新价": 65.2, "领涨股-涨跌幅": 1.80},
    ]


def _make_concept_rows():
    return [
        {"概念名称": "锂电池", "日期": "2026-05-14", "驱动事件": "碳酸锂价格上涨", "龙头股": "宁德时代", "成分股数量": 120},
        {"概念名称": "AI眼镜", "日期": "2026-05-14", "驱动事件": "苹果发布新AR产品", "龙头股": "歌尔股份", "成分股数量": 45},
        {"概念名称": "核聚变", "日期": "2026-05-13", "驱动事件": "ITER项目进展", "龙头股": "东方超环", "成分股数量": 18},
    ]


def test_industry_chain_industry():
    uc = IndustryChainUseCase()
    mock_provider = MagicMock()
    mock_provider.get_industry_summary.return_value = _make_industry_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = IndustryChainRequest(include=["industry_list"], sort_by="change_pct", descending=True)
        result = uc.execute(req)
    assert result["industry_count"] == 3
    item = result["industry_list"][0]
    assert item["name"] == "白色家电"
    assert item["change_pct"] == 2.15
    assert item["leader"] == "海尔智家"


def test_industry_chain_concept():
    uc = IndustryChainUseCase()
    mock_provider = MagicMock()
    mock_provider.get_concept_summary.return_value = _make_concept_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = IndustryChainRequest(include=["concept_list"])
        result = uc.execute(req)
    assert result["concept_count"] == 3
    item = result["concept_list"][0]
    assert item["name"] == "锂电池"
    assert item["driver_event"] == "碳酸锂价格上涨"
    assert item["leader"] == "宁德时代"


def test_industry_chain_both():
    uc = IndustryChainUseCase()
    mock_provider = MagicMock()
    mock_provider.get_industry_summary.return_value = _make_industry_rows()
    mock_provider.get_concept_summary.return_value = _make_concept_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = IndustryChainRequest(include=["industry_list", "concept_list"])
        result = uc.execute(req)
    assert result["industry_count"] == 3
    assert result["concept_count"] == 3


def test_industry_chain_sort_net_inflow():
    uc = IndustryChainUseCase()
    mock_provider = MagicMock()
    mock_provider.get_industry_summary.return_value = _make_industry_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = IndustryChainRequest(include=["industry_list"], sort_by="net_inflow", descending=True)
        result = uc.execute(req)
    assert result["industry_list"][0]["name"] == "白酒"  # 3200000000 net inflow


def test_industry_chain_top_n():
    uc = IndustryChainUseCase()
    mock_provider = MagicMock()
    mock_provider.get_industry_summary.return_value = _make_industry_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = IndustryChainRequest(include=["industry_list"], top_n=2)
        result = uc.execute(req)
    assert result["industry_count"] == 2


def test_industry_chain_uses_cache():
    uc = IndustryChainUseCase()
    raw = _make_industry_rows()
    uc.cache.set("industry:summary", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = IndustryChainRequest(include=["industry_list"])
        result = uc.execute(req)
    mock_provider.get_industry_summary.assert_not_called()
    assert result["industry_count"] == 3


def test_industry_chain_summary():
    uc = IndustryChainUseCase()
    mock_provider = MagicMock()
    mock_provider.get_industry_summary.return_value = _make_industry_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = IndustryChainRequest(include=["industry_list"])
        result = uc.execute(req)
    assert "行业" in result["summary"]

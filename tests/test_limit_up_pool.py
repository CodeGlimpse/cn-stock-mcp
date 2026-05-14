"""Tests for limit_up_pool usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from openclaw_stock_mcp.app.usecases.limit_up_pool import LimitUpPoolUseCase
from openclaw_stock_mcp.server.schemas import LimitUpPoolRequest


def _make_limit_up_rows():
    return [
        {"代码": "001259", "名称": "利仁科技", "涨跌幅": 10.011, "最新价": 50.00, "成交额": 29975000, "流通市值": 2377225000, "总市值": 3679444000, "换手率": 1.2609, "封板资金": 187875000, "首次封板时间": "092500", "最后封板时间": "092500", "炸板次数": 0, "涨停统计": "3/3", "连板数": 3, "所属行业": "小家电"},
        {"代码": "300965", "名称": "恒宇信通", "涨跌幅": 20.0, "最新价": 79.20, "成交额": 43290245, "流通市值": 4284225000, "总市值": 4752000000, "换手率": 1.0104, "封板资金": 240673435, "首次封板时间": "092500", "最后封板时间": "092500", "炸板次数": 0, "涨停统计": "1/1", "连板数": 1, "所属行业": "航空装备"},
        {"代码": "603123", "名称": "示例五板", "涨跌幅": 10.0, "最新价": 21.0, "成交额": 100000000, "流通市值": 3000000000, "总市值": 5000000000, "换手率": 8.0, "封板资金": 10000000, "首次封板时间": "100000", "最后封板时间": "145500", "炸板次数": 1, "涨停统计": "5/5", "连板数": 5, "所属行业": "示例行业"},
    ]


def _make_limit_down_rows():
    return [
        {"代码": "301053", "名称": "远信工业", "涨跌幅": -19.996, "最新价": 49.29, "成交额": 559922432, "流通市值": 4311923000, "总市值": 4643305000, "动态市盈率": 68.77, "换手率": 12.65, "封单资金": 5050302, "最后封板时间": "141439", "板上成交额": 122929253, "连续跌停": 1, "开板次数": 22, "所属行业": "专用设备"},
    ]


def _make_strong_rows():
    return [
        {"代码": "300210", "名称": "森远股份", "涨跌幅": 20.02, "最新价": 12.05, "涨停价": 12.05, "成交额": 1227489408, "流通市值": 5834850000, "总市值": 5834850000, "换手率": 21.75, "涨速": 0.0, "是否新高": "是", "量比": 4.95, "涨停统计": "1/1", "入选理由": "60日新高", "所属行业": "环保设备"},
        {"代码": "300959", "名称": "线上线下", "涨跌幅": 20.00, "最新价": 133.79, "涨停价": 133.79, "成交额": 1463902560, "流通市值": 7000992000, "总市值": 10752410000, "换手率": 21.37, "涨速": 0.0, "是否新高": "是", "量比": 3.42, "涨停统计": "2/2", "入选理由": "60日新高且近期多次涨停", "所属行业": "通信服务"},
    ]


def _make_previous_rows():
    return [
        {"代码": "600488", "名称": "津药药业", "涨跌幅": -0.826, "最新价": 7.20, "涨停价": 7.99, "成交额": 1977141808, "流通市值": 7861584000, "总市值": 7861584000, "换手率": 24.23, "涨速": 0.98, "振幅": 10.74, "昨日封板时间": "130316", "昨日连板数": 2, "涨停统计": "3/2", "所属行业": "化学制药"},
        {"代码": "600999", "名称": "示例续涨", "涨跌幅": 3.2, "最新价": 10.50, "涨停价": 10.99, "成交额": 100000000, "流通市值": 5000000000, "总市值": 7000000000, "换手率": 10.0, "涨速": 0.2, "振幅": 5.0, "昨日封板时间": "101010", "昨日连板数": 1, "涨停统计": "1/1", "所属行业": "示例行业"},
    ]


def _make_sub_new_rows():
    return [
        {"代码": "301531", "名称": "C春光集", "涨跌幅": -3.456, "最新价": 110.61, "涨停价": None, "成交额": 2968160080, "流通市值": 5185801000, "总市值": 24304700000, "转手率": 57.93, "开板几日": 3, "开板日期": "2026-05-11", "上市日期": "2026-05-11", "是否新高": "否", "涨停统计": "0/0", "所属行业": "金属新材"},
    ]


def _make_broken_rows():
    return [
        {"代码": "301538", "名称": "骏鼎达", "涨跌幅": 14.544, "最新价": 99.31, "涨停价": 104.04, "成交额": 731034192, "流通市值": 3100426000, "总市值": 7785904000, "换手率": 23.25, "涨速": 0.0, "首次封板时间": "092500", "炸板次数": 2, "涨停统计": "0/0", "振幅": 8.12, "所属行业": "塑料"},
    ]


def test_limit_up_pool_limit_up():
    uc = LimitUpPoolUseCase()
    mock_provider = MagicMock()
    mock_provider.get_limit_up_pool_raw.return_value = _make_limit_up_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = LimitUpPoolRequest(include=["limit_up"], trade_date="20260513")
        result = uc.execute(req)
    assert result["limit_up_count"] == 3
    item = result["limit_up"][0]
    assert item["code"] == "001259"
    assert item["consecutive_limit"] == 3
    assert item["seal_amount"] == 187875000


def test_limit_up_pool_all_categories():
    uc = LimitUpPoolUseCase()
    mock_provider = MagicMock()
    mock_provider.get_limit_up_pool_raw.return_value = _make_limit_up_rows()
    mock_provider.get_limit_down_pool.return_value = _make_limit_down_rows()
    mock_provider.get_strong_pool.return_value = _make_strong_rows()
    mock_provider.get_previous_limit_pool.return_value = _make_previous_rows()
    mock_provider.get_sub_new_pool.return_value = _make_sub_new_rows()
    mock_provider.get_broken_pool.return_value = _make_broken_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = LimitUpPoolRequest(include=["limit_up", "limit_down", "strong", "previous", "sub_new", "broken"], trade_date="20260513")
        result = uc.execute(req)
    assert result["limit_up_count"] == 3
    assert result["limit_down_count"] == 1
    assert result["strong_count"] == 2
    assert result["previous_count"] == 2
    assert result["sub_new_count"] == 1
    assert result["broken_count"] == 1


def test_limit_up_pool_top_n():
    uc = LimitUpPoolUseCase()
    mock_provider = MagicMock()
    mock_provider.get_strong_pool.return_value = _make_strong_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = LimitUpPoolRequest(include=["strong"], trade_date="20260513", top_n=1)
        result = uc.execute(req)
    assert result["strong_count"] == 1
    assert result["strong"][0]["name"] == "森远股份"
    assert result["sentiment"]["strong_total"] == 2


def test_limit_up_pool_uses_cache():
    uc = LimitUpPoolUseCase()
    raw = _make_limit_up_rows()
    uc.cache.set("limitup:zt:20260513", raw)
    mock_provider = MagicMock()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = LimitUpPoolRequest(include=["limit_up"], trade_date="20260513")
        result = uc.execute(req)
    mock_provider.get_limit_up_pool_raw.assert_not_called()
    assert result["limit_up_count"] == 3


def test_limit_up_pool_summary():
    uc = LimitUpPoolUseCase()
    mock_provider = MagicMock()
    mock_provider.get_limit_up_pool_raw.return_value = _make_limit_up_rows()
    mock_provider.get_limit_down_pool.return_value = _make_limit_down_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = LimitUpPoolRequest(include=["limit_up", "limit_down"], trade_date="20260513")
        result = uc.execute(req)
    assert "涨停" in result["summary"]
    assert "跌停" in result["summary"]


def test_limit_up_pool_sentiment_uses_full_data_not_top_n():
    uc = LimitUpPoolUseCase()
    mock_provider = MagicMock()
    mock_provider.get_limit_up_pool_raw.return_value = _make_limit_up_rows()
    mock_provider.get_previous_limit_pool.return_value = _make_previous_rows()
    mock_provider.get_broken_pool.return_value = _make_broken_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = LimitUpPoolRequest(include=["limit_up", "previous", "broken"], trade_date="20260513", top_n=1)
        result = uc.execute(req)

    assert result["limit_up_count"] == 1
    assert result["previous_count"] == 1
    assert result["broken_count"] == 1
    sentiment = result["sentiment"]
    assert sentiment["limit_up_total"] == 3
    assert sentiment["previous_total"] == 2
    assert sentiment["broken_total"] == 1
    assert sentiment["multi_limit_total"] == 2
    assert sentiment["highest_consecutive_limit"] == 5
    assert sentiment["previous_up_count"] == 1
    assert sentiment["previous_up_ratio"] == 0.5
    assert sentiment["broken_rate"] == 0.25
    assert sentiment["ladder"] == {"1": 1, "3": 1, "5+": 1}

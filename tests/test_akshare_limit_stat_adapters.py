import pytest
from openclaw_stock_mcp.providers.adapters.akshare_limit_stat_adapters import (
    adapt_em_limit_up_item,
    adapt_em_broken_limit_item,
    adapt_em_previous_limit_item,
    build_limit_stat_summary,
    build_limit_stat_summary_text,
)
from openclaw_stock_mcp.app.models.limit_stat import (
    LimitUpItem,
    BrokenLimitItem,
    PreviousDayLimitItem,
    LimitStatSummary,
)


# ---- adapt_em_limit_up_item ----

def test_adapt_limit_up_item_basic():
    row = {
        "序号": 1,
        "代码": "000839",
        "名称": "国安股份",
        "涨跌幅": 10.16,
        "最新价": 3.36,
        "成交额": 171910711,
        "流通市值": 1.317e10,
        "总市值": 1.317e10,
        "换手率": 1.305,
        "封板资金": 160388585,
        "首次封板时间": "092500",
        "最后封板时间": "092500",
        "炸板次数": 0,
        "涨停统计": "1/1",
        "连板数": 1,
        "所属行业": "通信服务",
    }
    item = adapt_em_limit_up_item(row)

    assert isinstance(item, LimitUpItem)
    assert item.symbol == "000839.SZ"
    assert item.name == "国安股份"
    assert item.price == pytest.approx(3.36)
    assert item.change_percent == pytest.approx(10.16)
    assert item.consecutive_boards == 1
    assert item.board_burst_count == 0
    assert item.first_limit_time == "092500"
    assert item.sector == "通信服务"
    assert item.limit_stat == "1/1"


def test_adapt_limit_up_item_sh_code():
    row = {"代码": "601991", "名称": "大唐发电", "连板数": 3, "所属行业": "电力"}
    item = adapt_em_limit_up_item(row)
    assert item.symbol == "601991.SH"
    assert item.consecutive_boards == 3


def test_adapt_limit_up_item_missing_fields():
    row = {"代码": "000001"}
    item = adapt_em_limit_up_item(row)
    assert item.symbol == "000001.SZ"
    assert item.price is None
    assert item.consecutive_boards is None
    assert item.sector is None


# ---- adapt_em_broken_limit_item ----

def test_adapt_broken_limit_item_basic():
    row = {
        "代码": "601512",
        "名称": "中新集团",
        "涨跌幅": 2.604,
        "最新价": 10.64,
        "涨停价": 11.41,
        "成交额": 444263696,
        "流通市值": 1.594e10,
        "总市值": 1.594e10,
        "换手率": 2.728,
        "涨速": 0.094,
        "首次封板时间": "093000",
        "炸板次数": 1,
        "涨停统计": "0/0",
        "振幅": 8.582,
        "所属行业": "房地产开发",
    }
    item = adapt_em_broken_limit_item(row)

    assert isinstance(item, BrokenLimitItem)
    assert item.symbol == "601512.SH"
    assert item.limit_price == pytest.approx(11.41)
    assert item.board_burst_count == 1
    assert item.amplitude == pytest.approx(8.582)
    assert item.sector == "房地产开发"


# ---- adapt_em_previous_limit_item ----

def test_adapt_previous_limit_item_basic():
    row = {
        "代码": "000967",
        "名称": "盈峰环境",
        "涨跌幅": -0.731,
        "最新价": 16.30,
        "涨停价": 18.06,
        "成交额": 4995303424,
        "流通市值": 5.339e10,
        "总市值": 5.289e10,
        "换手率": 9.278,
        "涨速": 1.558,
        "振幅": 7.308,
        "昨日封板时间": "142912",
        "昨日连板数": 1,
        "涨停统计": "2/1",
        "所属行业": "环保设备",
    }
    item = adapt_em_previous_limit_item(row)

    assert isinstance(item, PreviousDayLimitItem)
    assert item.symbol == "000967.SZ"
    assert item.yesterday_consecutive_boards == 1
    assert item.yesterday_limit_time == "142912"
    assert item.limit_price == pytest.approx(18.06)
    assert item.sector == "环保设备"


# ---- build_limit_stat_summary ----

def test_build_summary_full():
    limit_up = [
        LimitUpItem(symbol="000839.SZ", name="A", consecutive_boards=1, sector="通信"),
        LimitUpItem(symbol="601991.SH", name="B", consecutive_boards=3, sector="电力"),
        LimitUpItem(symbol="002929.SZ", name="C", consecutive_boards=2, sector="通信"),
        LimitUpItem(symbol="600519.SH", name="D", consecutive_boards=1, sector="白酒"),
        LimitUpItem(symbol="000001.SZ", name="E", consecutive_boards=5, sector="银行"),
    ]
    broken = [
        BrokenLimitItem(symbol="601512.SH", name="F", sector="房地产"),
        BrokenLimitItem(symbol="603598.SH", name="G", sector="广告"),
    ]
    previous = [
        PreviousDayLimitItem(symbol="000967.SZ", name="H", change_percent=9.8, sector="环保"),  # continues
        PreviousDayLimitItem(symbol="600726.SH", name="I", change_percent=-1.3, sector="电力"),  # doesn't
        PreviousDayLimitItem(symbol="600539.SH", name="J", change_percent=5.2, sector="互联网"),  # doesn't reach 9.5
    ]

    summary = build_limit_stat_summary("2026-05-08", limit_up, broken, previous, limit_down_count=3)

    assert isinstance(summary, LimitStatSummary)
    assert summary.limit_up_count == 5
    assert summary.broken_limit_count == 2
    assert summary.limit_down_count == 3
    assert summary.seal_rate == pytest.approx(5 / 7 * 100)  # 71.4%
    assert summary.max_consecutive_boards == 5
    assert summary.board_distribution[1] == 2
    assert summary.board_distribution[3] == 1
    assert summary.board_distribution[5] == 1
    assert summary.yesterday_limit_count == 3
    assert summary.yesterday_continue_limit_count == 1
    assert summary.yesterday_continue_rate == pytest.approx(1 / 3 * 100)
    assert summary.limit_up_by_sector["通信"] == 2
    assert summary.limit_up_by_sector["电力"] == 1
    assert summary.broken_limit_by_sector["房地产"] == 1


def test_build_summary_empty():
    summary = build_limit_stat_summary("2026-05-08", [], [], [])
    assert summary.limit_up_count == 0
    assert summary.seal_rate is None
    assert summary.max_consecutive_boards == 0
    assert summary.board_distribution == {}


def test_build_summary_no_broken():
    limit_up = [LimitUpItem(symbol="A", name="X", consecutive_boards=1)]
    summary = build_limit_stat_summary("2026-05-08", limit_up, [], [])
    assert summary.seal_rate == 100.0
    assert summary.broken_limit_count == 0


def test_build_summary_consecutive_boards_none_defaults_to_1():
    limit_up = [LimitUpItem(symbol="A", name="X", consecutive_boards=None)]
    summary = build_limit_stat_summary("2026-05-08", limit_up, [], [])
    assert summary.board_distribution[1] == 1
    assert summary.avg_consecutive_boards == pytest.approx(1.0)


# ---- build_limit_stat_summary_text ----

def test_summary_text_basic():
    summary = LimitStatSummary(
        trade_date="2026-05-08",
        limit_up_count=98,
        broken_limit_count=17,
        seal_rate=85.2,
        limit_down_count=5,
        max_consecutive_boards=7,
        avg_consecutive_boards=1.8,
        board_distribution={1: 70, 2: 15, 3: 8, 7: 1},
        yesterday_limit_count=100,
        yesterday_continue_limit_count=35,
        yesterday_continue_rate=35.0,
        limit_up_by_sector={"电力": 12, "通信": 9, "军工": 7},
    )
    text = build_limit_stat_summary_text(summary)
    assert "2026-05-08" in text
    assert "涨停98只" in text
    assert "炸板17只" in text
    assert "封板率85.2%" in text
    assert "跌停5只" in text
    assert "最高7连板" in text
    assert "连板分布" in text
    assert "昨涨停今继续" in text
    assert "电力" in text


def test_summary_text_no_data():
    summary = LimitStatSummary(trade_date="2026-05-08")
    text = build_limit_stat_summary_text(summary)
    assert "无涨停数据" in text


# ---- Schema validation ----

def test_limit_stat_request_defaults():
    from openclaw_stock_mcp.server.schemas import LimitStatRequest

    req = LimitStatRequest()
    assert req.include == ["summary", "limit_up", "broken_limit", "previous_day"]
    assert req.trade_date is None
    assert req.min_consecutive_boards is None


def test_limit_stat_request_with_date():
    from openclaw_stock_mcp.server.schemas import LimitStatRequest

    req = LimitStatRequest(trade_date="2026-05-08")
    assert req.trade_date == "2026-05-08"


def test_limit_stat_request_invalid_date():
    from openclaw_stock_mcp.server.schemas import LimitStatRequest

    with pytest.raises(ValueError):
        LimitStatRequest(trade_date="not-a-date")


def test_limit_stat_request_empty_include_fails():
    from openclaw_stock_mcp.server.schemas import LimitStatRequest

    with pytest.raises(ValueError, match="at least one"):
        LimitStatRequest(include=[])


def test_limit_stat_request_dedup_include():
    from openclaw_stock_mcp.server.schemas import LimitStatRequest

    req = LimitStatRequest(include=["summary", "summary", "limit_up"])
    assert req.include == ["summary", "limit_up"]

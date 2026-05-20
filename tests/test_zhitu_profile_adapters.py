from cn_stock_mcp.providers.adapters.zhitu_profile_adapters import (
    adapt_zhitu_profile,
    adapt_zhitu_dividend,
    adapt_zhitu_unlock,
    adapt_zhitu_quarter_profit,
    build_dividend_summary,
    build_unlock_risk,
)


def test_adapt_zhitu_profile():
    raw = {
        "name": "平安银行股份有限公司",
        "ename": "Ping An Bank Co.,Ltd.",
        "market": "深圳证券交易所",
        "ldate": "1991-04-03",
        "sprice": "40.00",
        "rprice": "1940590万元(CNY)",
        "instype": "股份制商业银行",
        "organ": "民营企业",
        "bscope": "人民币、外币存贷款;国际、国内结算;票据贴现;外汇买卖;提供担保及信用证服务;提供保管箱服务等。",
        "desc": "本行系在对深圳经济特区原六家信用社改组的同时...",
        "idea": "本月解禁,外资背景,证金汇金,区块链,融资融券,券商重仓,保险重仓,深圳本地,大盘,MSCI中国,基金重仓,社保重仓",
        "addr": "广东省深圳市罗湖区深南东路5047号",
        "site": "http://www.bank.pingan.com",
        "email": "PAB_db@pingan.com.cn",
        "phone": "0755-82080387",
        "secre": "周强",
    }
    profile = adapt_zhitu_profile(raw, "000001.SZ")

    assert profile.symbol == "000001.SZ"
    assert profile.name == "平安银行股份有限公司"
    assert profile.ename == "Ping An Bank Co.,Ltd."
    assert profile.list_date == "1991-04-03"
    assert len(profile.concepts) > 0
    assert "区块链" in profile.concepts
    assert profile.source == "zhitu"


def test_adapt_zhitu_dividend():
    raw = {
        "sdate": "2024-09-26",
        "give": "0",
        "change": "0",
        "send": "2.46",
        "line": "实施",
        "cdate": "2024-10-10",
        "edate": "2024-10-09",
        "hdate": "--",
    }
    dividend = adapt_zhitu_dividend(raw)

    assert dividend.announce_date == "2024-09-26"
    assert dividend.bonus_per_10 == 0.0
    assert dividend.transfer_per_10 == 0.0
    assert dividend.dividend_per_10 == 2.46
    assert dividend.progress == "实施"
    assert dividend.ex_dividend_date == "2024-10-10"
    assert dividend.record_date == "2024-10-09"


def test_adapt_zhitu_dividend_with_none_dates():
    raw = {
        "sdate": "2011-02-25",
        "give": "",
        "change": "",
        "send": "",
        "line": "不分配",
        "cdate": "--",
        "edate": "--",
    }
    dividend = adapt_zhitu_dividend(raw)

    assert dividend.announce_date == "2011-02-25"
    assert dividend.dividend_per_10 is None
    assert dividend.progress == "不分配"
    assert dividend.ex_dividend_date is None
    assert dividend.record_date is None


def test_adapt_zhitu_unlock():
    raw = {
        "rdate": "2018-05-21",
        "ramount": 25224.8,
        "rprice": 27.2932,
        "batch": 15,
        "pdate": "2015-05-20",
    }
    unlock = adapt_zhitu_unlock(raw)

    assert unlock.unlock_date == "2018-05-21"
    assert unlock.unlock_amount == 25224.8
    assert unlock.unlock_value == 27.2932
    assert unlock.batch == 15
    assert unlock.announce_date == "2015-05-20"


def test_adapt_zhitu_quarter_profit():
    raw = {
        "date": "2024-09-30",
        "reven": 1000000000.0,
        "nprof": 200000000.0,
        "eps": 1.0,
    }
    profit = adapt_zhitu_quarter_profit(raw)

    assert profit.period == "2024-09-30"
    assert profit.revenue == 1000000000.0
    assert profit.net_profit == 200000000.0
    assert profit.eps == 1.0


def test_build_dividend_summary():
    dividends = [
        adapt_zhitu_dividend({"sdate": "2024-09-26", "send": "2.46", "line": "实施"}),
        adapt_zhitu_dividend({"sdate": "2024-06-06", "send": "7.19", "line": "实施"}),
        adapt_zhitu_dividend({"sdate": "2023-06-07", "send": "2.85", "line": "实施"}),
    ]
    summary = build_dividend_summary(dividends)

    assert summary["total_years"] == 2  # 2024, 2023
    assert summary["avg_dividend_per_10"] is not None
    assert "2024" in summary["dividend_years"]
    assert "2023" in summary["dividend_years"]


def test_build_dividend_summary_empty():
    summary = build_dividend_summary([])

    assert summary["total_years"] == 0
    assert summary["avg_dividend_per_10"] is None
    assert summary["dividend_years"] == []


def test_build_unlock_risk():
    unlocks = [
        adapt_zhitu_unlock({"rdate": "2025-06-01", "ramount": 1000, "rprice": 50000}),
        adapt_zhitu_unlock({"rdate": "2025-12-01", "ramount": 2000, "rprice": 100000}),
    ]
    risk = build_unlock_risk(unlocks)

    assert risk["has_future_unlock"] is True
    assert risk["total_unlock_value"] == 150000
    assert risk["upcoming_count"] == 2
    assert len(risk["upcoming_unlocks"]) == 2


def test_build_unlock_risk_empty():
    risk = build_unlock_risk([])

    assert risk["has_future_unlock"] is False
    assert risk["total_unlock_value"] is None


def test_stock_profile_valuation_snapshot_fields():
    from cn_stock_mcp.providers.zhitu_provider import ZhituProvider

    provider = ZhituProvider.__new__(ZhituProvider)
    # monkeypatch minimal internals for deterministic valuation mapping
    def fake_get_quote(symbol, sec_type):
        from types import SimpleNamespace
        return SimpleNamespace(price=12.3, pe=15.6, pb=2.1, market_cap=123456.0, float_market_cap=65432.0, source='zhitu')
    provider.get_quote = fake_get_quote
    provider._get_json = lambda path, params=None: [{'name': '测试公司'}] if 'gsjj' in path else []
    profile = provider.get_profile('000001.SZ', include=['valuation'])
    assert profile.valuation is not None
    assert profile.valuation.price == 12.3
    assert profile.valuation.pe == 15.6
    assert profile.valuation.source == 'zhitu'

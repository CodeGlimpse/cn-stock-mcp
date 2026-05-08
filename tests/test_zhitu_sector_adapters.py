import pytest
from openclaw_stock_mcp.providers.adapters.zhitu_sector_adapters import adapt_zhitu_sector_quote


def test_adapt_zhitu_sector_quote():
    raw = {
        "p": "101.23",
        "o": "100.00",
        "h": "102.50",
        "l": "99.80",
        "yc": "100.50",
        "ud": "0.73",
        "pc": "0.73",
        "zf": "2.70",
        "v": "1234567",
        "tv": "1234567",
        "cje": "125000000",
        "hs": "1.23",
        "mc": "测试板块指数",
        "t": "2026-05-08 15:30:00",
    }
    quote = adapt_zhitu_sector_quote(raw, "101076.BKZS", "concept")

    assert quote.symbol == "101076.BKZS"
    assert quote.name == "测试板块指数"
    assert quote.sector_type == "concept"
    assert quote.price == 101.23
    assert quote.open == 100.00
    assert quote.high == 102.50
    assert quote.low == 99.80
    assert quote.prev_close == 100.50
    assert quote.change == 0.73
    assert quote.change_percent == 0.73
    assert quote.amplitude == 2.70
    assert quote.volume == 1234567
    assert quote.turnover == 125000000
    assert quote.turnover_rate == 1.23
    assert quote.currency == "CNY"
    assert quote.timestamp == "2026-05-08T15:30:00+08:00"  # normalize_time_string converts to ISO format
    assert quote.source == "zhitu"


def test_adapt_zhitu_sector_quote_with_none_values():
    raw = {
        "p": "",
        "o": None,
        "h": "",
        "l": "",
        "yc": "",
        "ud": "",
        "pc": "",
        "zf": "",
        "v": "",
        "tv": "",
        "cje": "",
        "hs": "",
        "mc": "空值板块",
        "t": None,
    }
    quote = adapt_zhitu_sector_quote(raw, "101077.BKZS", "primary")

    assert quote.symbol == "101077.BKZS"
    assert quote.name == "空值板块"
    assert quote.sector_type == "primary"
    assert quote.price is None
    assert quote.open is None
    assert quote.high is None
    assert quote.low is None
    assert quote.prev_close is None
    assert quote.change is None
    assert quote.change_percent is None
    assert quote.amplitude is None
    assert quote.volume is None
    assert quote.turnover is None
    assert quote.turnover_rate is None
    assert quote.currency == "CNY"
    assert quote.timestamp is None
    assert quote.source == "zhitu"
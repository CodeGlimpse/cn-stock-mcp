from openclaw_stock_mcp.providers.adapters.zhitu_market_adapters import adapt_zhitu_batch_quote


def test_adapt_zhitu_batch_quote():
    raw = {
        "dm": "sh600519",
        "mc": "贵州茅台",
        "p": 1384.79,
        "pc": -1.17,
        "h": 1401.17,
        "l": 1380.0,
        "o": 1400.0,
        "v": 5.28,
        "cje": 7316111748.0,
        "zf": 1.51,
        "hs": 0.42,
        "pe": 15.91,
        "sz": 1734131271030.0,
        "lt": 1734131271030.0,
        "sjl": 6.4,
    }
    quote = adapt_zhitu_batch_quote(raw, "600519", "SH")

    assert quote.symbol == "600519.SH"
    assert quote.name == "贵州茅台"
    assert quote.price == 1384.79
    assert quote.open == 1400.0
    assert quote.high == 1401.17
    assert quote.low == 1380.0
    assert quote.change_percent == -1.17
    assert quote.prev_close is None
    assert quote.change is None
    assert quote.timestamp is None
    assert quote.source == "zhitu"
    assert quote.exchange == "SH"
    assert quote.sec_type == "stock"


def test_adapt_zhitu_batch_quote_sz_exchange():
    raw = {
        "dm": "sz000001",
        "mc": "平安银行",
        "p": 10.5,
        "pc": 1.2,
        "h": 10.8,
        "l": 10.3,
        "o": 10.4,
        "v": 100.0,
        "cje": 1050.0,
        "zf": 4.76,
        "hs": 0.5,
        "pe": 6.0,
        "sz": 2000000000.0,
        "lt": 1800000000.0,
        "sjl": 0.8,
    }
    quote = adapt_zhitu_batch_quote(raw, "000001", "SZ")

    assert quote.symbol == "000001.SZ"
    assert quote.name == "平安银行"
    assert quote.exchange == "SZ"
    assert quote.price == 10.5

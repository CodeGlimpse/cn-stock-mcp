from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        pass

    def _get_json(self, path: str, params=None):
        self.last_path = path
        if path == "/hs/real/ssjy/600519":
            return {
                "t": "2026-04-30 15:05:05",
                "p": 1384.79,
                "pc": -1.17,
                "ud": -16.38,
                "v": 5.28,
                "cje": 7316111748.0,
                "zf": 1.51,
                "hs": 0.42,
                "pe": 15.91,
                "h": 1401.17,
                "l": 1380.0,
                "o": 1400.0,
                "yc": 1401.17,
                "sz": 1734131271030.0,
                "lt": 1734131271030.0,
                "sjl": 6.4,
            }
        raise AssertionError(f"unexpected path: {path}")


def test_zhitu_stock_main_quote_route_uses_hs_real_ssjy():
    provider = _Zhitu()

    quote = provider.get_quote("600519.SH", "stock")

    assert provider.last_path == "/hs/real/ssjy/600519"
    assert quote.symbol == "600519.SH"
    assert quote.sec_type == "stock"
    assert quote.exchange == "SH"
    assert quote.board == "main"
    assert quote.price == 1384.79
    assert quote.source == "zhitu"

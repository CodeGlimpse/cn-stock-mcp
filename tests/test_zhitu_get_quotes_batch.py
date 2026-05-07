from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


class _MockZhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}
        self.paths = []
        self.batch_calls = []

    def _get_json(self, path: str, params=None):
        self.paths.append(path)
        if path == "/hs/public/ssjymore":
            codes = params.get("stock_codes", "").split(",") if params else []
            self.batch_calls.append(codes)
            items = []
            for code in codes:
                clean_code = code.lstrip("sh").lstrip("sz")
                if clean_code == "600519":
                    items.append({
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
                    })
                elif clean_code == "000001":
                    items.append({
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
                    })
            return items
        if path == "/bj/stock/real/ssjy/899050":
            return {
                "t": "2026-04-30 15:05:05",
                "p": 100.0,
                "pc": 2.0,
                "ud": 2.0,
                "v": 10.0,
                "cje": 1000.0,
                "zf": 5.0,
                "hs": 1.0,
                "pe": 10.0,
                "h": 102.0,
                "l": 98.0,
                "o": 99.0,
                "yc": 98.0,
                "sz": 500000000.0,
                "lt": 450000000.0,
            }
        raise AssertionError(f"unexpected path: {path}")


def test_zhitu_get_quotes_uses_batch_for_main_board():
    provider = _MockZhitu()
    symbols = ["600519.SH", "000001.SZ"]

    quotes = provider.get_quotes(symbols, "stock")

    assert len(quotes) == 2
    assert quotes[0].symbol == "600519.SH"
    assert quotes[0].name == "贵州茅台"
    assert quotes[1].symbol == "000001.SZ"
    assert quotes[1].name == "平安银行"

    assert "/hs/public/ssjymore" in provider.paths
    assert len(provider.batch_calls) == 1
    assert set(provider.batch_calls[0]) == {"600519", "000001"}


def test_zhitu_get_quotes_falls_back_to_single_for_bj():
    provider = _MockZhitu()
    symbols = ["600519.SH", "899050.BJ"]

    quotes = provider.get_quotes(symbols, "stock")

    assert len(quotes) == 2
    assert quotes[0].symbol == "600519.SH"
    assert quotes[1].symbol == "899050.BJ"
    assert "/hs/public/ssjymore" in provider.paths
    assert "/bj/stock/real/ssjy/899050" in provider.paths

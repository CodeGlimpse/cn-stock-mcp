from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}
        self.paths = []

    def _get_json(self, path: str, params=None):
        self.paths.append(path)
        if path == "/hs/real/five/600519":
            return {
                "t": "2026-05-07 14:35:19",
                "pb1": 1500.01,
                "vb1": 120,
                "pb2": 1500.0,
                "vb2": 340,
                "pb3": 1499.98,
                "vb3": 560,
                "pb4": 1499.95,
                "vb4": 780,
                "pb5": 1499.9,
                "vb5": 900,
                "ps1": 1500.05,
                "vs1": 210,
                "ps2": 1500.08,
                "vs2": 430,
                "ps3": 1500.1,
                "vs3": 650,
                "ps4": 1500.12,
                "vs4": 870,
                "ps5": 1500.15,
                "vs5": 1090,
            }
        if path == "/tech/real/mmwp/688001":
            return {
                "t": "2026-05-07 14:35:19",
                "pb1": 21.01,
                "vb1": 11,
                "ps1": 21.05,
                "vs1": 12,
            }
        if path == "/bj/stock/real/mmwp/430017":
            return {
                "t": "2026-05-07 14:35:19",
                "pb1": 9.81,
                "vb1": 101,
                "ps1": 9.83,
                "vs1": 102,
            }
        raise AssertionError(f"unexpected path: {path}")


def test_zhitu_orderbook_main_stock_route_uses_hs_real_five():
    provider = _Zhitu()

    orderbook = provider.get_orderbook("600519.SH", "stock")

    assert "/hs/real/five/600519" in provider.paths
    assert orderbook.symbol == "600519.SH"
    assert orderbook.source == "zhitu"
    assert len(orderbook.bids) == 5
    assert len(orderbook.asks) == 5
    assert orderbook.bids[0].price == 1500.01
    assert orderbook.asks[0].price == 1500.05


def test_zhitu_orderbook_star_route_keeps_tech_mmwp():
    provider = _Zhitu()

    orderbook = provider.get_orderbook("688001.SH", "stock")

    assert "/tech/real/mmwp/688001" in provider.paths
    assert orderbook.symbol == "688001.SH"
    assert orderbook.bids[0].price == 21.01


def test_zhitu_orderbook_bj_route_keeps_bj_mmwp():
    provider = _Zhitu()

    orderbook = provider.get_orderbook("430017.BJ", "stock")

    assert "/bj/stock/real/mmwp/430017" in provider.paths
    assert orderbook.symbol == "430017.BJ"
    assert orderbook.asks[0].price == 9.83

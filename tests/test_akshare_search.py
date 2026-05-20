from cn_stock_mcp.providers.akshare_provider import AKShareProvider


class _DF:
    def __init__(self, rows):
        self._rows = rows

    def to_dict(self, orient="records"):
        assert orient == "records"
        return list(self._rows)


class _Lib:
    def stock_info_a_code_name(self):
        return _DF(
            [
                {"code": "000001", "name": "平安银行"},
                {"code": "300750", "name": "宁德时代"},
            ]
        )

    def index_stock_info(self):
        return _DF(
            [
                {"index_code": "399006", "display_name": "创业板指"},
                {"index_code": "000001", "display_name": "上证指数"},
            ]
        )

    def fund_name_em(self):
        return _DF(
            [
                {"基金代码": "000001", "基金简称": "华夏成长混合"},
                {"基金代码": "159001", "基金简称": "货币ETF易方达"},
                {"基金代码": "001879", "基金简称": "长城创业板指数增强A"},
            ]
        )


class _Provider(AKShareProvider):
    def _require_ak(self):
        return _Lib()


def test_search_instruments_can_match_index_display_name():
    p = _Provider()

    items = p.search_instruments("创业板指", sec_types=["index", "fund"], limit=5)

    assert items[0].sec_type == "index"
    assert items[0].name == "创业板指"
    assert items[0].symbol == "399006.SZ"


def test_search_instruments_prefers_exact_symbol_match_and_keeps_related_results():
    p = _Provider()

    items = p.search_instruments("000001", sec_types=["stock", "index", "fund"], limit=5)

    assert items[0].sec_type == "stock"
    assert items[0].raw_symbol == "000001"
    assert items[0].name == "平安银行"
    assert any(item.sec_type == "index" and item.raw_symbol == "000001" for item in items)
    assert any(item.sec_type == "fund" and item.raw_symbol == "000001" for item in items)


def test_search_instruments_normalizes_fund_symbol_exchange():
    p = _Provider()

    items = p.search_instruments("159001", sec_types=["fund"], limit=5)

    assert items[0].symbol == "159001.SZ"

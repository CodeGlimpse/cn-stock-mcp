from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}

    def _get_json(self, path: str, params=None):
        if path == '/hz/list/hszs':
            return [
                {'dm': '000001.SH', 'mc': '上证指数', 'jys': 'sh'},
            ]
        if path == '/hz/real/ssjy/000001.SH':
            return {
                't': '2026-04-30 15:00:09',
                'p': 4112.159,
                'o': 4107.297,
                'h': 4118.755,
                'l': 4100.966,
                'yc': 4107.514,
                'ud': 4.645,
                'pc': 0.1131,
                'zf': 0.4331,
                'v': 656912728.0,
                'cje': 1276194739100.0,
            }
        raise AssertionError(f'unexpected path: {path}')


def test_zhitu_quote_fills_name_from_cache():
    provider = _Zhitu()
    provider._instrument_name_cache[('index', '000001.SH')] = '上证指数'

    quote = provider.get_quote('000001.SH', 'index')

    assert quote.symbol == '000001.SH'
    assert quote.name == '上证指数'


def test_zhitu_quote_can_lazy_load_name_when_cache_is_empty():
    provider = _Zhitu()

    quote = provider.get_quote('000001.SH', 'index')

    assert quote.symbol == '000001.SH'
    assert quote.name == '上证指数'

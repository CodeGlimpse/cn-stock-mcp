from cn_stock_mcp.providers.zhitu_provider import ZhituProvider


class _Zhitu(ZhituProvider):
    def __init__(self):
        self._instrument_name_cache = {}

    def _get_json(self, path: str, params=None):
        if path == '/hz/list/hszs':
            return [
                {'dm': '000001.SH', 'mc': '上证指数', 'jys': 'sh'},
                {'dm': '399001.SZ', 'mc': '深证成指', 'jys': 'sz'},
                {'dm': '399006.SZ', 'mc': '创业板指', 'jys': 'sz'},
            ]
        if path == '/hz/real/ssjy/000001.SH':
            return {'t': '2026-04-30 15:00:09', 'p': 4112.159, 'o': 4107.297, 'h': 4118.755, 'l': 4100.966, 'yc': 4107.514, 'ud': 4.645, 'pc': 0.1131, 'zf': 0.4331, 'v': 656912728.0, 'cje': 1276194739100.0}
        if path == '/hz/real/ssjy/399001.SZ':
            return {'t': '2026-04-30 15:00:03', 'p': 15107.553, 'o': 15157.068, 'h': 15186.12, 'l': 15044.855, 'yc': 15120.923, 'ud': -13.37, 'pc': -0.0884, 'zf': 0.9342, 'v': 737703743.0, 'cje': 1464716733100.0}
        if path == '/hz/real/ssjy/399006.SZ':
            return {'t': '2026-04-30 15:00:03', 'p': 3677.148, 'o': 3704.109, 'h': 3718.399, 'l': 3660.219, 'yc': 3687.168, 'ud': -10.02, 'pc': -0.2718, 'zf': 1.5779, 'v': 207981816.0, 'cje': 641724142100.0}
        raise AssertionError(f'unexpected path: {path}')


def test_market_overview_quotes_include_names():
    provider = _Zhitu()

    result = provider.get_market_overview('CN')

    assert result['indices'][0].name == '上证指数'
    assert result['indices'][1].name == '深证成指'
    assert result['indices'][2].name == '创业板指'

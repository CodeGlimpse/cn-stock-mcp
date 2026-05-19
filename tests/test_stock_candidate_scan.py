from types import SimpleNamespace

from openclaw_stock_mcp.app.usecases.stock_candidate_scan import StockCandidateScanUseCase


class _Member:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name


class _SectorLookup:
    def execute(self, request):
        if request.sector_name == "1000信息":
            return {
                "items": [_Member("000001.SZ", "平安银行"), _Member("300750.SZ", "宁德时代")],
                "total": 2,
                "source": "zhitu",
                "meta": {"used_fallback": False},
            }
        if request.sector_name == "1000工业":
            return {
                "items": [_Member("002594.SZ", "比亚迪")],
                "total": 1,
                "source": "zhitu",
                "meta": {"used_fallback": False},
            }
        raise Exception("sector failed")


class _MarketPool:
    def execute(self, request):
        return {
            "pool_type": request.pool_type,
            "trade_date": request.trade_date or "2026-05-06",
            "requested_trade_date": request.trade_date or "2026-05-06",
            "items": [
                {"symbol": "300750.SZ", "name": "宁德时代"},
                {"symbol": "600519.SH", "name": "贵州茅台"},
            ],
            "count": 2,
            "source": "zhitu",
            "meta": {},
        }


class _BatchReview:
    def execute(self, request):
        assert set(request.symbols).issubset({"600519.SH", "000001.SZ", "300750.SZ", "002594.SZ"})
        return {
            "mode": "trade_date_review",
            "requested_trade_date": "2026-05-06",
            "requested_start_date": None,
            "requested_end_date": None,
            "sort_by": "relative_strength",
            "descending": True,
            "items": [
                {
                    "symbol": "300750.SZ",
                    "mode": "trade_date_review",
                    "trade_date": "2026-05-06",
                    "close": 100.0,
                    "relative_strength": 8.0,
                    "return": 12.0,
                    "max_drawdown": 3.0,
                    "volume_ratio": 1.8,
                    "tags": ["stronger_than_benchmark", "positive_return", "high_volume", "up_streak"],
                    "benchmark": {"symbol": "399006.SZ", "name": "创业板指", "return_pct": 2.0},
                    "stats": {"up_streak": 3, "down_streak": 0},
                    "summary": "A",
                    "source": "akshare",
                },
                {
                    "symbol": "002594.SZ",
                    "mode": "trade_date_review",
                    "trade_date": "2026-05-06",
                    "close": 90.0,
                    "relative_strength": 3.0,
                    "return": 5.0,
                    "max_drawdown": 4.0,
                    "volume_ratio": 1.3,
                    "tags": ["stronger_than_benchmark", "positive_return", "high_volume"],
                    "benchmark": {"symbol": "399001.SZ", "name": "深证成指", "return_pct": 1.0},
                    "stats": {"up_streak": 1, "down_streak": 0},
                    "summary": "B",
                    "source": "akshare",
                },
                {
                    "symbol": "600519.SH",
                    "mode": "trade_date_review",
                    "trade_date": "2026-05-06",
                    "close": 80.0,
                    "relative_strength": -1.0,
                    "return": 1.0,
                    "max_drawdown": 2.0,
                    "volume_ratio": 0.9,
                    "tags": [],
                    "benchmark": {"symbol": "000001.SH", "name": "上证指数", "return_pct": 1.5},
                    "stats": {"up_streak": 0, "down_streak": 0},
                    "summary": "C",
                    "source": "akshare",
                },
            ],
            "count": 3,
            "filtered_from": 4,
            "total_symbols": 4,
            "partial_failure": True,
            "errors": [
                {"symbol": "000001.SZ", "error_code": "PROVIDER_UNAVAILABLE", "message": "x", "retryable": True, "provider": None}
            ],
            "summary": "batch done",
        }


def _build_usecase() -> StockCandidateScanUseCase:
    uc = StockCandidateScanUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.market_pool = _MarketPool()
    uc.batch_review = _BatchReview()
    return uc


def _req(**overrides):
    base = dict(
        symbols=["600519.SH"],
        sector_names=["1000信息", "1000工业"],
        sector_type="primary",
        pool_type="strong",
        trade_date="2026-05-06",
        start_date=None,
        end_date=None,
        adjust="none",
        provider="mixed",
        sort_by="candidate_score",
        descending=True,
        top_n=10,
        limit=10,
        min_candidate_score=None,
        min_relative_strength=None,
        min_return=None,
        max_drawdown_limit=None,
        min_volume_ratio=None,
        min_up_streak=None,
        max_down_streak=None,
        require_source_tags=None,
        exclude_risk_flags=None,
        must_have_reason_tags=None,
        exclude_reason_tags=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_stock_candidate_scan_baseline_and_metadata():
    result = _build_usecase().execute(_req(top_n=2, limit=5))

    assert result["subject_type"] == "candidate_scan"
    assert result["member_count"] == 4
    assert result["reviewed_count"] == 3
    assert result["partial_failure"] is True
    assert result["items"][0]["symbol"] == "300750.SZ"
    assert result["items"][0]["candidate_label"] == "candidate"
    assert result["errors"][0]["scope"] == "stock_review"
    assert result["meta"]["candidate_score_schema"]["schema"] == "candidate_score_v1"
    assert result["meta"]["review_envelope_schema"]["schema"] == "review_envelope_v1"


def test_stock_candidate_scan_numeric_filters():
    result = _build_usecase().execute(
        _req(
            sector_names=["1000信息"],
            pool_type=None,
            min_candidate_score=8.0,
            min_relative_strength=5.0,
            min_return=8.0,
            max_drawdown_limit=5.0,
            min_volume_ratio=1.2,
            top_n=5,
            limit=5,
        )
    )
    assert [x["symbol"] for x in result["items"]] == ["300750.SZ"]


def test_stock_candidate_scan_tag_filters():
    result = _build_usecase().execute(
        _req(
            min_up_streak=2,
            max_down_streak=1,
            require_source_tags=["pool:strong"],
            exclude_risk_flags=["weak_relative_strength"],
        )
    )
    assert [x["symbol"] for x in result["items"]] == ["300750.SZ"]



def test_stock_candidate_scan_reason_tag_filters():
    result = _build_usecase().execute(
        _req(
            must_have_reason_tags=["strong_return", "active_volume"],
            exclude_reason_tags=["slight_positive_return"],
        )
    )
    assert [x["symbol"] for x in result["items"]] == ["300750.SZ"]



def test_candidate_scan_return_mode_ranked_only():
    class _Batch:
        def execute(self, req):
            return {
                "mode": "trade_date_review",
                "requested_trade_date": "2026-05-08",
                "requested_start_date": None,
                "requested_end_date": None,
                "items": [
                    {"symbol": "A", "relative_strength": 8, "return": 9, "max_drawdown": 2, "volume_ratio": 1.3, "tags": [], "stats": {}, "benchmark": {}},
                    {"symbol": "B", "relative_strength": 2, "return": 2, "max_drawdown": 3, "volume_ratio": 1.0, "tags": [], "stats": {}, "benchmark": {}},
                ],
                "partial_failure": False,
                "errors": [],
                "sort_by": "relative_strength",
                "descending": True,
                "filtered_from": 2,
                "total_symbols": 2,
            }

    uc = StockCandidateScanUseCase()
    uc.batch_review = _Batch()
    uc._build_universe = lambda req: {
        "symbols": ["A", "B"],
        "errors": [],
        "source_tags": {"A": [], "B": []},
        "source_breakdown": {},
        "sector_details": [],
        "pool": None,
        "truncated": False,
    }

    result = uc.execute(
        _req(
            symbols=["A", "B"],
            sector_names=None,
            pool_type=None,
            trade_date="2026-05-08",
            top_n=1,
            limit=20,
            return_mode="ranked_only",
        )
    )

    assert len(result["items"]) == 1
    assert result["meta"]["filters"]["return_mode"] == "ranked_only"

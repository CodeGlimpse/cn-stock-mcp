from openclaw_stock_mcp.app.usecases.stock_candidate_scan import StockCandidateScanUseCase


class _Member:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name


class _SectorLookup:
    def execute(self, request):
        if request.sector_name == "1000信息":
            return {
                "items": [
                    _Member("000001.SZ", "平安银行"),
                    _Member("300750.SZ", "宁德时代"),
                ],
                "total": 2,
                "source": "zhitu",
                "meta": {"used_fallback": False},
            }
        if request.sector_name == "1000工业":
            return {
                "items": [
                    _Member("002594.SZ", "比亚迪"),
                ],
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
        expected = set(["600519.SH", "000001.SZ", "300750.SZ", "002594.SZ"])
        assert set(request.symbols).issubset(expected)
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
                {"symbol": "000001.SZ", "error_code": "PROVIDER_UNAVAILABLE", "message": "x", "retryable": True, "provider": None},
            ],
            "summary": "batch done",
        }


def test_stock_candidate_scan_builds_universe_scores_and_buckets():
    uc = StockCandidateScanUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.market_pool = _MarketPool()
    uc.batch_review = _BatchReview()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH"],
            "sector_names": ["1000信息", "1000工业"],
            "sector_type": "primary",
            "pool_type": "strong",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "mixed",
            "sort_by": "candidate_score",
            "descending": True,
            "top_n": 2,
            "limit": 5,
            "min_candidate_score": None,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
            "min_up_streak": None,
            "max_down_streak": None,
            "require_source_tags": None,
            "exclude_risk_flags": None,
        },
    )()

    result = uc.execute(req)

    assert result["subject_type"] == "candidate_scan"
    assert result["subject_name"] == "manual+sector+pool:strong"
    assert result["member_count"] == 4
    assert result["reviewed_count"] == 3
    assert result["partial_failure"] is True
    assert result["items"][0]["symbol"] == "300750.SZ"
    assert result["items"][0]["candidate_label"] == "candidate"
    assert "strong_return" in result["items"][0]["reason_tags"]
    assert "pool:strong" in result["items"][0]["source_tags"]
    assert result["breadth"]["candidate_count"] >= 1
    assert result["buckets"]["candidates"][0]["symbol"] == "300750.SZ"
    assert result["rankings"]["leaders_by_candidate_score"][0]["symbol"] == "300750.SZ"
    assert result["errors"][0]["scope"] == "stock_review"
    assert result["meta"]["candidate_score_schema"]["schema"] == "candidate_score_v1"
    assert result["meta"]["review_envelope_schema"]["schema"] == "review_envelope_v1"
    assert "candidate_score_breakdown" in result["items"][0]
    assert "total" in result["items"][0]["candidate_score_breakdown"]


def test_stock_candidate_scan_applies_filters():
    uc = StockCandidateScanUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.market_pool = _MarketPool()
    uc.batch_review = _BatchReview()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH"],
            "sector_names": ["1000信息"],
            "sector_type": "primary",
            "pool_type": None,
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "mixed",
            "sort_by": "candidate_score",
            "descending": True,
            "top_n": 5,
            "limit": 5,
            "min_candidate_score": 8.0,
            "min_relative_strength": 5.0,
            "min_return": 8.0,
            "max_drawdown_limit": 5.0,
            "min_volume_ratio": 1.2,
            "min_up_streak": None,
            "max_down_streak": None,
            "require_source_tags": None,
            "exclude_risk_flags": None,
        },
    )()

    result = uc.execute(req)

    assert len(result["items"]) == 1
    assert result["items"][0]["symbol"] == "300750.SZ"


def test_stock_candidate_scan_new_filters():
    uc = StockCandidateScanUseCase()
    uc.sector_lookup = _SectorLookup()
    uc.market_pool = _MarketPool()
    uc.batch_review = _BatchReview()

    req = type(
        "Req",
        (),
        {
            "symbols": ["600519.SH"],
            "sector_names": ["1000信息", "1000工业"],
            "sector_type": "primary",
            "pool_type": "strong",
            "trade_date": "2026-05-06",
            "start_date": None,
            "end_date": None,
            "adjust": "none",
            "provider": "mixed",
            "sort_by": "candidate_score",
            "descending": True,
            "top_n": 10,
            "limit": 10,
            "min_candidate_score": None,
            "min_relative_strength": None,
            "min_return": None,
            "max_drawdown_limit": None,
            "min_volume_ratio": None,
            "min_up_streak": 2,
            "max_down_streak": 1,
            "require_source_tags": ["pool:strong"],
            "exclude_risk_flags": ["weak_relative_strength"],
        },
    )()

    result = uc.execute(req)

    assert len(result["items"]) == 1
    assert result["items"][0]["symbol"] == "300750.SZ"

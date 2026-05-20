from types import SimpleNamespace
from unittest.mock import MagicMock

from cn_stock_mcp.app.models.index_compose import IndexComposeSummary, IndexConstituentItem
from cn_stock_mcp.app.models.profile import StockProfile, StockProfileDetail
from cn_stock_mcp.app.models.quote import Quote
from cn_stock_mcp.app.usecases.index_enhance import IndexEnhanceUseCase
from cn_stock_mcp.server.schemas import IndexEnhanceRequest


class _Compose:
    def execute(self, request):
        return {
            "summary": IndexComposeSummary(index_code=request.index_code, index_name="沪深300", constituent_count=3).model_dump(),
            "items": [
                IndexConstituentItem(symbol="600519", name="贵州茅台", exchange="SH", weight=6.0).model_dump(),
                IndexConstituentItem(symbol="300750", name="宁德时代", exchange="SZ", weight=4.0).model_dump(),
                IndexConstituentItem(symbol="000858", name="五粮液", exchange="SZ", weight=2.0).model_dump(),
            ],
            "used_fallback_endpoint": False,
        }


class _History:
    def execute(self, request):
        assert request.symbol == "000300.SH"
        assert request.sec_type == "index"
        return {"items": [SimpleNamespace(close=101.0, prev_close=100.0)]}


def _quotes():
    return {
        "600519.SH": Quote(symbol="600519.SH", name="贵州茅台", sec_type="stock", price=1600, change_percent=2.0, source="mock"),
        "300750.SZ": Quote(symbol="300750.SZ", name="宁德时代", sec_type="stock", price=250, change_percent=-1.0, source="mock"),
        "000858.SZ": Quote(symbol="000858.SZ", name="五粮液", sec_type="stock", price=150, change_percent=3.0, source="mock"),
    }


def _industry_detail(symbol, industry):
    return StockProfileDetail(profile=StockProfile(symbol=symbol, industry=industry, source="mock"), source="mock")


def test_index_enhance_weighted_compare():
    uc = IndexEnhanceUseCase()
    uc.index_compose = _Compose()
    uc.stock_history = _History()
    uc._get_quotes = MagicMock(return_value=_quotes())
    uc._get_industries = MagicMock(return_value={
        "600519.SH": "白酒",
        "300750.SZ": "电池",
        "000858.SZ": "白酒",
    })

    result = uc.execute(IndexEnhanceRequest(index_code="000300", top_n=3, weighting="weight"))

    assert result["summary"]["benchmark_return"] == 1.0
    assert round(result["summary"]["enhanced_return"], 4) == 1.1667
    assert round(result["summary"]["excess_return"], 4) == 0.1667
    assert result["summary"]["outperform_count"] == 2
    assert result["summary"]["underperform_count"] == 1
    assert result["members"][0]["industry"] == "白酒"
    assert result["weight_exposure"]["top1_weight_percent"] == 50.0
    assert result["weight_exposure"]["top3_weight_percent"] == 100.0
    assert result["industry_coverage"]["known_count"] == 3
    assert result["industry_coverage"]["unknown_count"] == 0
    industries = {x["industry"]: x for x in result["industry_exposure"]}
    assert industries["白酒"]["member_count"] == 2
    assert industries["白酒"]["weight_sum"] == 8.0
    assert round(industries["白酒"]["contribution_sum"], 4) == 0.18
    assert "跑赢" in result["summary_text"]


def test_index_enhance_equal_weight():
    uc = IndexEnhanceUseCase()
    uc.index_compose = _Compose()
    uc.stock_history = _History()
    uc._get_quotes = MagicMock(return_value=_quotes())
    uc._get_industries = MagicMock(return_value={})

    result = uc.execute(IndexEnhanceRequest(index_code="000300.SH", top_n=3, weighting="equal"))

    assert round(result["summary"]["enhanced_return"], 4) == 1.3333
    assert result["summary"]["total_weight"] is None
    assert result["summary"]["method"] == "top_weight_equal_quote"
    assert result["industry_coverage"]["known_count"] == 0
    assert result["industry_coverage"]["unknown_count"] == 3


def test_index_enhance_schema_rejects_empty_index_code():
    try:
        IndexEnhanceRequest(index_code="  ")
    except ValueError as exc:
        assert "index_code is required" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_index_enhance_get_industries_uses_cache():
    uc = IndexEnhanceUseCase()
    uc.profile_cache.set("index_enhance:industry:600519.SH", "白酒")
    provider = MagicMock()
    provider.get_profile.return_value = _industry_detail("300750.SZ", "电池")
    uc.router.choose_provider = MagicMock(return_value=SimpleNamespace(primary="zhitu", fallback=[]))
    uc.router.get_provider = MagicMock(return_value=provider)

    industries = uc._get_industries(["600519.SH", "300750.SZ"])

    assert industries == {"600519.SH": "白酒", "300750.SZ": "电池"}
    provider.get_profile.assert_called_once_with("300750.SZ", include=["profile"])

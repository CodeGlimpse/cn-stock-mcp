from types import SimpleNamespace
from unittest.mock import MagicMock, call

from openclaw_stock_mcp.app.models.index_compose import IndexComposeSummary, IndexConstituentItem
from openclaw_stock_mcp.app.models.quote import Quote
from openclaw_stock_mcp.app.usecases.index_enhance import IndexEnhanceUseCase
from openclaw_stock_mcp.server.schemas import IndexEnhanceRequest


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
        return {"items": [SimpleNamespace(change_percent=1.0)]}


def _quotes():
    return [
        Quote(symbol="600519.SH", name="贵州茅台", sec_type="stock", price=1600, change_percent=2.0, source="mock"),
        Quote(symbol="300750.SZ", name="宁德时代", sec_type="stock", price=250, change_percent=-1.0, source="mock"),
        Quote(symbol="000858.SZ", name="五粮液", sec_type="stock", price=150, change_percent=3.0, source="mock"),
    ]


def test_index_enhance_weighted_compare():
    uc = IndexEnhanceUseCase()
    uc.index_compose = _Compose()
    uc.stock_history = _History()
    provider = MagicMock()
    provider.get_quote.side_effect = _quotes()
    uc.router.choose_provider = MagicMock(return_value=SimpleNamespace(primary="zhitu", fallback=["akshare"]))
    uc.router.get_provider = MagicMock(return_value=provider)

    result = uc.execute(IndexEnhanceRequest(index_code="000300", top_n=3, weighting="weight"))

    assert result["summary"]["benchmark_return"] == 1.0
    # weighted: (6*2 + 4*(-1) + 2*3) / 12 = 1.166666...
    assert round(result["summary"]["enhanced_return"], 4) == 1.1667
    assert round(result["summary"]["excess_return"], 4) == 0.1667
    assert result["summary"]["outperform_count"] == 2
    assert result["summary"]["underperform_count"] == 1
    assert result["members"][0]["weighted_contribution"] == 0.12
    assert "跑赢" in result["summary_text"]


def test_index_enhance_equal_weight():
    uc = IndexEnhanceUseCase()
    uc.index_compose = _Compose()
    uc.stock_history = _History()
    provider = MagicMock()
    provider.get_quote.side_effect = _quotes()
    uc.router.choose_provider = MagicMock(return_value=SimpleNamespace(primary="zhitu", fallback=[]))
    uc.router.get_provider = MagicMock(return_value=provider)

    result = uc.execute(IndexEnhanceRequest(index_code="000300.SH", top_n=3, weighting="equal"))

    assert round(result["summary"]["enhanced_return"], 4) == 1.3333
    assert result["summary"]["total_weight"] is None
    assert result["summary"]["method"] == "top_weight_equal_quote"


def test_index_enhance_schema_rejects_empty_index_code():
    try:
        IndexEnhanceRequest(index_code="  ")
    except ValueError as exc:
        assert "index_code is required" in str(exc)
    else:
        raise AssertionError("expected ValueError")

from cn_stock_mcp.app.usecases.stock_snapshot import StockSnapshotUseCase
from cn_stock_mcp.server.schemas import StockSnapshotRequest


class _Resolver:
    def resolve(self, symbol, sec_type):
        return type("Resolved", (), {"symbol": symbol, "sec_type": sec_type})()


class _Quotes:
    def execute(self, request):
        return {
            "items": [{"symbol": request.symbols[0], "price": 100.0, "source": "fake"}],
            "errors": [],
        }


class _History:
    def execute(self, request):
        return {"items": [{"time": "2026-08-14", "close": 99.0}], "count": 1, "source": "fake", "meta": {}}


class _Financial:
    def execute(self, request):
        return {"snapshot": {"report_date": "2026-06-30", "net_profit": 10.0}, "history": [], "summary": "ok", "source": "fake"}


class _Profile:
    def execute(self, request):
        return {
            "valuation": {"price": 100.0, "pe": 12.0, "source": "fake"},
            "dividends": [{"announce_date": "2026-04-01"}],
            "unlocks": [],
            "quarter_profits": [{"period": "2026-06-30"}],
            "unlock_risk": {"has_future_unlock": False},
        }


def test_stock_snapshot_composes_bounded_sections():
    uc = StockSnapshotUseCase()
    uc.resolver = _Resolver()
    uc.quote = _Quotes()
    uc.history = _History()
    uc.financial = _Financial()
    uc.profile = _Profile()

    result = uc.execute(StockSnapshotRequest(symbols=["600519.SH"], max_total_timeout_seconds=5))

    assert result["partial_failure"] is False
    assert result["reviewed_count"] == 1
    assert result["items"][0]["quote"]["price"] == 100.0
    assert result["items"][0]["history"]["count"] == 1
    assert result["items"][0]["financial"]["snapshot"]["net_profit"] == 10.0
    assert result["items"][0]["valuation"]["pe"] == 12.0
    assert result["items"][0]["events"]["quarter_profits"]
    assert result["items"][0]["risk"]["risk_tags"] == []
    assert result["meta"]["transaction_support"] is False


def test_stock_snapshot_exposes_section_failure_without_dropping_other_sections():
    class _BrokenFinancial(_Financial):
        def execute(self, request):
            raise RuntimeError("financial unavailable")

    uc = StockSnapshotUseCase()
    uc.resolver = _Resolver()
    uc.quote = _Quotes()
    uc.history = _History()
    uc.financial = _BrokenFinancial()
    uc.profile = _Profile()

    result = uc.execute(StockSnapshotRequest(symbols=["600519.SH"], include=["quote", "financial"], max_total_timeout_seconds=5))

    assert result["partial_failure"] is True
    assert result["items"][0]["quote"]["price"] == 100.0
    assert result["items"][0]["financial"] is None
    assert result["errors"][0]["section"] == "financial"
    assert "600519.SH.financial" in result["meta"]["missing_fields"]

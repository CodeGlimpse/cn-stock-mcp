from __future__ import annotations

import logging
from typing import Any, Callable

from pydantic import BaseModel, Field, ValidationError

from openclaw_stock_mcp.app.services.error_mapper import serialize_exception
from openclaw_stock_mcp.app.usecases.hot_theme_tracker import HotThemeTrackerUseCase
from openclaw_stock_mcp.app.usecases.market_brief import MarketBriefUseCase
from openclaw_stock_mcp.app.usecases.market_overview import MarketOverviewUseCase
from openclaw_stock_mcp.app.usecases.event_calendar import EventCalendarUseCase
from openclaw_stock_mcp.app.usecases.market_pool import MarketPoolUseCase
from openclaw_stock_mcp.app.usecases.orderbook import OrderbookUseCase
from openclaw_stock_mcp.app.usecases.provider_health import ProviderHealthUseCase
from openclaw_stock_mcp.app.usecases.multi_timeframe_review import MultiTimeframeReviewUseCase
from openclaw_stock_mcp.app.usecases.watchlist_review import WatchlistReviewUseCase
from openclaw_stock_mcp.app.usecases.stock_candidate_scan import StockCandidateScanUseCase
from openclaw_stock_mcp.app.usecases.stock_profile import StockProfileUseCase
from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
from openclaw_stock_mcp.app.usecases.sector_quote import SectorQuoteUseCase
from openclaw_stock_mcp.app.usecases.sector_review import SectorReviewUseCase
from openclaw_stock_mcp.app.usecases.sector_rotation_review import SectorRotationReviewUseCase
from openclaw_stock_mcp.app.usecases.sector_leaders import SectorLeadersUseCase
from openclaw_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from openclaw_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase
from openclaw_stock_mcp.app.usecases.stock_review import StockReviewUseCase
from openclaw_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase
from openclaw_stock_mcp.app.usecases.stock_search import StockSearchUseCase
from openclaw_stock_mcp.app.usecases.technical_indicator import TechnicalIndicatorUseCase
from openclaw_stock_mcp.app.usecases.trading_calendar import TradingCalendarUseCase
from openclaw_stock_mcp.infra.logging import log_event
from openclaw_stock_mcp.server.response_envelope import error_response, new_request_id, ok_response
from openclaw_stock_mcp.server.schemas import (
    HotThemeTrackerRequest,
    MarketBriefRequest,
    MarketOverviewRequest,
    MarketPoolRequest,
    MultiTimeframeReviewRequest,
    SectorLookupRequest,
    SectorQuoteRequest,
    SectorReviewRequest,
    SectorRotationReviewRequest,
    SectorLeadersRequest,
    EventCalendarRequest,
    StockHistoryRequest,
    StockOrderbookRequest,
    StockCandidateScanRequest,
    StockProfileRequest,
    StockQuoteRequest,
    StockReviewBatchRequest,
    StockReviewRequest,
    StockSearchRequest,
    TechnicalIndicatorRequest,
    TradingCalendarRequest,
    WatchlistReviewRequest,
)

logger = logging.getLogger(__name__)


class EmptyRequest(BaseModel):
    pass


class MCPTool(BaseModel):
    name: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[[BaseModel], Any] = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}


class MCPServerStub(BaseModel):
    name: str
    version: str
    tools: dict[str, MCPTool] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    def register_tool(self, tool: MCPTool) -> None:
        self.tools[tool.name] = tool

    def call_tool(self, name: str, payload: dict[str, Any]) -> Any:
        request_id = new_request_id()
        tool = self.tools.get(name)
        if not tool:
            log_event(logger, "tool_not_found", request_id=request_id, tool=name)
            return error_response(
                {
                    "error_code": "TOOL_NOT_FOUND",
                    "message": f"Tool not found: {name}",
                    "retryable": False,
                    "provider": None,
                },
                meta={"tool": name},
                request_id=request_id,
            )

        try:
            request = tool.input_model(**payload)
        except ValidationError as exc:
            log_event(logger, "tool_validation_error", request_id=request_id, tool=name, errors=exc.errors())
            return error_response(
                {
                    "error_code": "INVALID_ARGUMENT",
                    "message": "Invalid request payload",
                    "retryable": False,
                    "provider": None,
                    "details": exc.errors(),
                },
                meta={"tool": name},
                request_id=request_id,
            )

        try:
            log_event(logger, "tool_call_start", request_id=request_id, tool=name)
            data = tool.handler(request)
            log_event(logger, "tool_call_success", request_id=request_id, tool=name)
            return ok_response(data, meta={"tool": name}, request_id=request_id)
        except Exception as exc:
            err = serialize_exception(exc)
            log_event(logger, "tool_call_error", request_id=request_id, tool=name, error=err)
            return error_response(err, meta={"tool": name}, request_id=request_id)


def create_server() -> MCPServerStub:
    server = MCPServerStub(name="openclaw-stock-mcp", version="0.1.0")

    stock_search = StockSearchUseCase()
    stock_quote = StockQuoteUseCase()
    stock_history = StockHistoryUseCase()
    stock_review = StockReviewUseCase()
    stock_review_batch = StockReviewBatchUseCase()
    watchlist_review = WatchlistReviewUseCase()
    trading_calendar = TradingCalendarUseCase()
    market_overview = MarketOverviewUseCase()
    market_brief = MarketBriefUseCase()
    technical_indicator = TechnicalIndicatorUseCase()
    multi_timeframe_review = MultiTimeframeReviewUseCase()
    market_pool = MarketPoolUseCase()
    stock_orderbook = OrderbookUseCase()
    stock_candidate_scan = StockCandidateScanUseCase()
    sector_lookup = SectorLookupUseCase()
    sector_quote = SectorQuoteUseCase()
    sector_review = SectorReviewUseCase()
    sector_rotation_review = SectorRotationReviewUseCase()
    sector_leaders = SectorLeadersUseCase()
    hot_theme_tracker = HotThemeTrackerUseCase()
    provider_health = ProviderHealthUseCase()
    stock_profile = StockProfileUseCase()
    event_calendar = EventCalendarUseCase()

    server.register_tool(MCPTool(name="stock_search", description="Search stocks, indices, funds, or sectors by keyword or code.", input_model=StockSearchRequest, handler=stock_search.execute))
    server.register_tool(MCPTool(name="stock_quote", description="Get real-time quotes for one or more instruments.", input_model=StockQuoteRequest, handler=stock_quote.execute))
    server.register_tool(MCPTool(name="stock_history", description="Get historical price bars for an instrument.", input_model=StockHistoryRequest, handler=stock_history.execute))
    server.register_tool(MCPTool(name="stock_review", description="Generate a review summary for a stock on a trade date or over a date range.", input_model=StockReviewRequest, handler=stock_review.execute))
    server.register_tool(MCPTool(name="stock_review_batch", description="Batch review multiple stocks and rank the results for replay workflows.", input_model=StockReviewBatchRequest, handler=stock_review_batch.execute))
    server.register_tool(MCPTool(name="watchlist_review", description="Review and prioritize a watchlist of symbols.", input_model=WatchlistReviewRequest, handler=watchlist_review.execute))
    server.register_tool(MCPTool(name="trading_calendar", description="Query China trading-day calendar for review and backtesting workflows.", input_model=TradingCalendarRequest, handler=trading_calendar.execute))
    server.register_tool(MCPTool(name="market_overview", description="Get high-level overview of China market major indices.", input_model=MarketOverviewRequest, handler=market_overview.execute))
    server.register_tool(MCPTool(name="market_brief", description="Generate a compact market brief by combining overview and pool data.", input_model=MarketBriefRequest, handler=market_brief.execute))
    server.register_tool(MCPTool(name="technical_indicator", description="Get technical indicator series such as MACD, MA, BOLL, KDJ.", input_model=TechnicalIndicatorRequest, handler=technical_indicator.execute))
    server.register_tool(MCPTool(name="multi_timeframe_review", description="Review a symbol across multiple timeframes and summarize alignment/conflicts.", input_model=MultiTimeframeReviewRequest, handler=multi_timeframe_review.execute))
    server.register_tool(MCPTool(name="market_pool", description="Get market pools such as limit-up, limit-down, strong, sub-new, and broken-limit stocks.", input_model=MarketPoolRequest, handler=market_pool.execute))
    server.register_tool(MCPTool(name="stock_orderbook", description="Get order book data for supported instruments.", input_model=StockOrderbookRequest, handler=stock_orderbook.execute))
    server.register_tool(MCPTool(name="stock_candidate_scan", description="Scan a stock universe and rank candidate setups.", input_model=StockCandidateScanRequest, handler=stock_candidate_scan.execute))
    server.register_tool(MCPTool(name="sector_lookup", description="Lookup sector lists and members.", input_model=SectorLookupRequest, handler=sector_lookup.execute))
    server.register_tool(MCPTool(name="sector_quote", description="Get real-time quotes for sector indices.", input_model=SectorQuoteRequest, handler=sector_quote.execute))
    server.register_tool(MCPTool(name="sector_review", description="Generate a review summary for a sector by aggregating its member stocks.", input_model=SectorReviewRequest, handler=sector_review.execute))
    server.register_tool(MCPTool(name="sector_rotation_review", description="Compare multiple sectors and summarize cross-sector rotation signals.", input_model=SectorRotationReviewRequest, handler=sector_rotation_review.execute))
    server.register_tool(MCPTool(name="sector_leaders", description="Get leaders/followers/draggers snapshot for a sector.", input_model=SectorLeadersRequest, handler=sector_leaders.execute))
    server.register_tool(MCPTool(name="hot_theme_tracker", description="Track hot themes by combining sector rotation and pool snapshots.", input_model=HotThemeTrackerRequest, handler=hot_theme_tracker.execute))
    server.register_tool(MCPTool(name="provider_health", description="Run provider self checks for zhitu and akshare.", input_model=EmptyRequest, handler=provider_health.execute))
    server.register_tool(MCPTool(name="event_calendar", description="Build event timeline (dividend/unlock/profit) for one or more stocks.", input_model=EventCalendarRequest, handler=event_calendar.execute))
    server.register_tool(MCPTool(name="stock_profile", description="Get company profile including basic info, dividends, unlocks, and quarterly profits.", input_model=StockProfileRequest, handler=stock_profile.execute))

    return server

from __future__ import annotations

import json
import logging
from typing import Any, Callable

from pydantic import BaseModel, Field, ValidationError

from cn_stock_mcp.app.services.data_freshness import build_data_freshness
from cn_stock_mcp.app.services.data_quality import build_data_quality
from cn_stock_mcp.app.services.error_mapper import serialize_exception
from cn_stock_mcp.app.usecases.hot_theme_tracker import HotThemeTrackerUseCase
from cn_stock_mcp.app.usecases.market_brief import MarketBriefUseCase
from cn_stock_mcp.app.usecases.market_overview import MarketOverviewUseCase
from cn_stock_mcp.app.usecases.event_calendar import EventCalendarUseCase
from cn_stock_mcp.app.usecases.capital_flow import CapitalFlowUseCase
from cn_stock_mcp.app.usecases.stock_financial import StockFinancialUseCase
from cn_stock_mcp.app.usecases.limit_stat import LimitStatUseCase
from cn_stock_mcp.app.usecases.northbound import NorthboundUseCase
from cn_stock_mcp.app.usecases.valuation_rank import ValuationRankUseCase
from cn_stock_mcp.app.usecases.index_compose import IndexComposeUseCase
from cn_stock_mcp.app.usecases.index_enhance import IndexEnhanceUseCase
from cn_stock_mcp.app.usecases.industry_valuation_rank import IndustryValuationRankUseCase
from cn_stock_mcp.app.usecases.earnings_quality import EarningsQualityUseCase
from cn_stock_mcp.app.usecases.macro_indicator import MacroIndicatorUseCase
from cn_stock_mcp.app.usecases.dragon_tiger import DragonTigerUseCase
from cn_stock_mcp.app.usecases.etf_snapshot import ETFSnapshotUseCase
from cn_stock_mcp.app.usecases.convertible_bond import ConvertibleBondUseCase
from cn_stock_mcp.app.usecases.derivatives_data import DerivativesDataUseCase
from cn_stock_mcp.app.usecases.margin_trading import MarginTradingUseCase
from cn_stock_mcp.app.usecases.block_trade import BlockTradeUseCase
from cn_stock_mcp.app.usecases.institute_hold import InstituteHoldUseCase
from cn_stock_mcp.app.usecases.money_rate import MoneyRateUseCase
from cn_stock_mcp.app.usecases.stock_screen import StockScreenUseCase
from cn_stock_mcp.app.usecases.insider_trade import InsiderTradeUseCase
from cn_stock_mcp.app.usecases.dividend_rank import DividendRankUseCase
from cn_stock_mcp.app.usecases.shareholder_change import ShareholderChangeUseCase
from cn_stock_mcp.app.usecases.disclosure_calendar import DisclosureCalendarUseCase
from cn_stock_mcp.app.usecases.stock_repurchase import StockRepurchaseUseCase
from cn_stock_mcp.app.usecases.stock_compare import StockCompareUseCase
from cn_stock_mcp.app.usecases.industry_chain import IndustryChainUseCase
from cn_stock_mcp.app.usecases.stock_warrant import StockWarrantUseCase
from cn_stock_mcp.app.usecases.fund_flow import FundFlowUseCase
from cn_stock_mcp.app.usecases.limit_up_pool import LimitUpPoolUseCase
from cn_stock_mcp.app.usecases.sec_reveal import SecRevealUseCase
from cn_stock_mcp.app.usecases.market_pool import MarketPoolUseCase
from cn_stock_mcp.app.usecases.stock_orderbook import OrderbookUseCase
from cn_stock_mcp.app.usecases.provider_health import ProviderHealthUseCase
from cn_stock_mcp.app.usecases.multi_timeframe_review import MultiTimeframeReviewUseCase
from cn_stock_mcp.app.usecases.watchlist_review import WatchlistReviewUseCase
from cn_stock_mcp.app.usecases.stock_candidate_scan import StockCandidateScanUseCase
from cn_stock_mcp.app.usecases.stock_profile import StockProfileUseCase
from cn_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
from cn_stock_mcp.app.usecases.sector_review import SectorReviewUseCase
from cn_stock_mcp.app.usecases.sector_rotation_review import SectorRotationReviewUseCase
from cn_stock_mcp.app.usecases.sector_leaders import SectorLeadersUseCase
from cn_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from cn_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase
from cn_stock_mcp.app.usecases.stock_snapshot import StockSnapshotUseCase
from cn_stock_mcp.app.usecases.stock_review import StockReviewUseCase
from cn_stock_mcp.app.usecases.stock_review_batch import StockReviewBatchUseCase
from cn_stock_mcp.app.usecases.stock_search import StockSearchUseCase
from cn_stock_mcp.app.usecases.technical_indicator import TechnicalIndicatorUseCase
from cn_stock_mcp.app.usecases.trading_calendar import TradingCalendarUseCase
from cn_stock_mcp.infra.logging import log_event
from cn_stock_mcp.server.response_envelope import error_response, new_request_id, ok_response
from cn_stock_mcp.server.schemas import (
    HotThemeTrackerRequest,
    MarketBriefRequest,
    MarketOverviewRequest,
    MarketPoolRequest,
    MultiTimeframeReviewRequest,
    CapitalFlowRequest,
    StockFinancialRequest,
    LimitStatRequest,
    NorthboundRequest,
    ValuationRankRequest,
    IndexComposeRequest,
    IndexEnhanceRequest,
    IndustryValuationRankRequest,
    EarningsQualityRequest,
    MacroIndicatorRequest,
    DragonTigerRequest,
    ETFSnapshotRequest,
    ConvertibleBondRequest,
    DerivativesDataRequest,
    MarginTradingRequest,
    BlockTradeRequest,
    InstituteHoldRequest,
    MoneyRateRequest,
    StockScreenRequest,
    InsiderTradeRequest,
    DividendRankRequest,
    ShareholderChangeRequest,
    DisclosureCalendarRequest,
    StockRepurchaseRequest,
    StockCompareRequest,
    IndustryChainRequest,
    StockWarrantRequest,
    SecRevealRequest,
    FundFlowRequest,
    LimitUpPoolRequest,
    SectorLookupRequest,
    SectorReviewRequest,
    SectorRotationReviewRequest,
    SectorLeadersRequest,
    EventCalendarRequest,
    StockHistoryRequest,
    StockOrderbookRequest,
    StockCandidateScanRequest,
    StockProfileRequest,
    StockQuoteRequest,
    StockSnapshotRequest,
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


def _validation_error_details(exc: ValidationError) -> list[dict[str, Any]]:
    """Return JSON-safe validation error details for envelopes/stdio."""
    return json.loads(exc.json())


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
            details = _validation_error_details(exc)
            log_event(logger, "tool_validation_error", request_id=request_id, tool=name, errors=details)
            return error_response(
                {
                    "error_code": "INVALID_ARGUMENT",
                    "message": "Invalid request payload",
                    "retryable": False,
                    "provider": None,
                    "details": details,
                },
                meta={"tool": name},
                request_id=request_id,
            )

        try:
            log_event(logger, "tool_call_start", request_id=request_id, tool=name)
            data = tool.handler(request)
            log_event(logger, "tool_call_success", request_id=request_id, tool=name)
            freshness = build_data_freshness(data)
            return ok_response(
                data,
                meta={"tool": name, "freshness": freshness, "data_quality": build_data_quality(data, freshness)},
                request_id=request_id,
            )
        except Exception as exc:
            err = serialize_exception(exc)
            log_event(logger, "tool_call_error", request_id=request_id, tool=name, error=err)
            return error_response(err, meta={"tool": name}, request_id=request_id)


def create_server() -> MCPServerStub:
    server = MCPServerStub(name="cn-stock-mcp", version="0.1.0")

    stock_search = StockSearchUseCase()
    stock_quote = StockQuoteUseCase()
    stock_snapshot = StockSnapshotUseCase()
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
    sector_review = SectorReviewUseCase()
    sector_rotation_review = SectorRotationReviewUseCase()
    sector_leaders = SectorLeadersUseCase()
    hot_theme_tracker = HotThemeTrackerUseCase()
    provider_health = ProviderHealthUseCase()
    stock_profile = StockProfileUseCase()
    event_calendar = EventCalendarUseCase()
    capital_flow = CapitalFlowUseCase()
    stock_financial = StockFinancialUseCase()
    limit_stat = LimitStatUseCase()
    northbound = NorthboundUseCase()
    valuation_rank = ValuationRankUseCase()
    index_compose = IndexComposeUseCase()
    index_enhance = IndexEnhanceUseCase()
    industry_valuation_rank = IndustryValuationRankUseCase()
    earnings_quality = EarningsQualityUseCase()
    macro_indicator = MacroIndicatorUseCase()
    dragon_tiger = DragonTigerUseCase()
    etf_snapshot = ETFSnapshotUseCase()
    convertible_bond = ConvertibleBondUseCase()
    derivatives_data = DerivativesDataUseCase()
    margin_trading = MarginTradingUseCase()
    block_trade = BlockTradeUseCase()
    institute_hold = InstituteHoldUseCase()
    money_rate = MoneyRateUseCase()
    stock_screen = StockScreenUseCase()
    insider_trade = InsiderTradeUseCase()
    dividend_rank = DividendRankUseCase()
    shareholder_change = ShareholderChangeUseCase()
    disclosure_calendar = DisclosureCalendarUseCase()
    stock_repurchase = StockRepurchaseUseCase()
    stock_compare = StockCompareUseCase()
    industry_chain = IndustryChainUseCase()
    stock_warrant = StockWarrantUseCase()
    fund_flow = FundFlowUseCase()
    limit_up_pool = LimitUpPoolUseCase()
    sec_reveal = SecRevealUseCase()

    server.register_tool(MCPTool(name="stock_search", description="Search stocks, indices, funds, or sectors by keyword or code.", input_model=StockSearchRequest, handler=stock_search.execute))
    server.register_tool(MCPTool(name="stock_quote", description="Get real-time quotes for one or more instruments.", input_model=StockQuoteRequest, handler=stock_quote.execute))
    server.register_tool(MCPTool(name="stock_snapshot", description="Get a bounded multi-source stock snapshot combining quote, recent history, financial summary, valuation, events, and risk tags; no trading actions.", input_model=StockSnapshotRequest, handler=stock_snapshot.execute))
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
    server.register_tool(MCPTool(name="sector_review", description="Generate a review summary for a sector by aggregating its member stocks.", input_model=SectorReviewRequest, handler=sector_review.execute))
    server.register_tool(MCPTool(name="sector_rotation_review", description="Compare multiple sectors and summarize cross-sector rotation signals.", input_model=SectorRotationReviewRequest, handler=sector_rotation_review.execute))
    server.register_tool(MCPTool(name="sector_leaders", description="Get leaders/followers/draggers snapshot for a sector.", input_model=SectorLeadersRequest, handler=sector_leaders.execute))
    server.register_tool(MCPTool(name="hot_theme_tracker", description="Track hot themes by combining sector rotation and pool snapshots.", input_model=HotThemeTrackerRequest, handler=hot_theme_tracker.execute))
    server.register_tool(MCPTool(name="provider_health", description="Run provider self checks for zhitu and akshare.", input_model=EmptyRequest, handler=provider_health.execute))
    server.register_tool(MCPTool(name="event_calendar", description="Build event timeline (dividend/unlock/profit) for one or more stocks.", input_model=EventCalendarRequest, handler=event_calendar.execute))
    server.register_tool(MCPTool(name="stock_profile", description="Get company profile including basic info, dividends, unlocks, and quarterly profits.", input_model=StockProfileRequest, handler=stock_profile.execute))
    server.register_tool(MCPTool(name="capital_flow", description="Get capital flow data: market-level, individual stock, or sector (industry/concept) fund flow ranking.", input_model=CapitalFlowRequest, handler=capital_flow.execute))
    server.register_tool(MCPTool(name="stock_financial", description="Get financial statement data for a stock: core metrics snapshot, history trend, and detailed income/balance/cashflow statements.", input_model=StockFinancialRequest, handler=stock_financial.execute))
    server.register_tool(MCPTool(name="limit_stat", description="Get limit statistics for a trading day: seal rate, consecutive board distribution, broken limit count, yesterday-continue rate, sector breakdown.", input_model=LimitStatRequest, handler=limit_stat.execute))
    server.register_tool(MCPTool(name="northbound", description="Get northbound capital data: daily flow summary and historical trend.", input_model=NorthboundRequest, handler=northbound.execute))
    server.register_tool(MCPTool(name="valuation_rank", description="Rank stock valuation using PE/PB and combine with market valuation temperature (PE/PB quantiles, dividend yield).", input_model=ValuationRankRequest, handler=valuation_rank.execute))
    server.register_tool(MCPTool(name="index_compose", description="Get index constituents and weights for index benchmarking/enhanced strategy construction.", input_model=IndexComposeRequest, handler=index_compose.execute))
    server.register_tool(MCPTool(name="index_enhance", description="Compare an enhanced top-constituent portfolio against its benchmark index: benchmark return, weighted/equal enhanced return, excess return, member contribution and outperform/underperform counts.", input_model=IndexEnhanceRequest, handler=index_enhance.execute))
    server.register_tool(MCPTool(name="industry_valuation_rank", description="Rank primary sectors by valuation percentile using member stock PE/PB aggregation.", input_model=IndustryValuationRankRequest, handler=industry_valuation_rank.execute))
    server.register_tool(MCPTool(name="earnings_quality", description="Evaluate earnings quality from financial snapshot (deduct ratio, growth consistency, cash conversion, ROE, leverage).", input_model=EarningsQualityRequest, handler=earnings_quality.execute))
    server.register_tool(MCPTool(name="macro_indicator", description="Get macro economic indicators (CPI/PPI/PMI/GDP/LPR/M2/etc.) for CN/USA/Euro/Global regions. Supports latest value, history, calendar, and overview modes.", input_model=MacroIndicatorRequest, handler=macro_indicator.execute))
    server.register_tool(MCPTool(name="dragon_tiger", description="Get dragon-tiger board (龙虎榜) data: daily listed stocks with buy/sell detail, institution participation, active broker tracking, broker success-rate ranking, and stock board statistics.", input_model=DragonTigerRequest, handler=dragon_tiger.execute))
    server.register_tool(MCPTool(name="etf_snapshot", description="Get ETF market snapshot: real-time quotes with IOPV/discount rate/main net inflow, ETF share/scale, and NAV history. Supports full-market sorting and discount-rate filtering.", input_model=ETFSnapshotRequest, handler=etf_snapshot.execute))
    server.register_tool(MCPTool(name="convertible_bond", description="Get convertible bond (可转债) data: real-time snapshot with double-low/premium/YTM, call/redeem monitoring, and bond index history. Supports double-low strategy screening and call-status filtering.", input_model=ConvertibleBondRequest, handler=convertible_bond.execute))
    server.register_tool(MCPTool(name="derivatives_data", description="Get derivatives data: futures real-time quotes and history, option contract lists (SSE/SZSE), and QVIX implied volatility index. Supports multiple futures symbols and QVIX underlyings.", input_model=DerivativesDataRequest, handler=derivatives_data.execute))
    server.register_tool(MCPTool(name="margin_trading", description="Get margin trading (融资融券) data: market-level summary with financing/securities balance, and stock-level detail with financing buy/sell and securities volume. Supports SSE/SZSE exchanges.", input_model=MarginTradingRequest, handler=margin_trading.execute))
    server.register_tool(MCPTool(name="block_trade", description="Get block trade (大宗交易) data: daily trade detail with buyer/seller broker, daily stock summary with discount rate, industry aggregation, broker success-rate ranking, and active stock tracking. Supports date range and period-based queries.", input_model=BlockTradeRequest, handler=block_trade.execute))
    server.register_tool(MCPTool(name="institute_hold", description="Get institute holding (机构持仓) data: quarterly market-wide summary with institution count and holding ratio changes, and per-stock detail with individual institution breakdown. Supports auto-quarter detection.", input_model=InstituteHoldRequest, handler=institute_hold.execute))
    server.register_tool(MCPTool(name="money_rate", description="Get money market rates (货币市场利率): SHIBOR full-term curve (O/N~1Y), interbank rate by tenor, repo fixing rates (FR/FDR). Supports latest and historical modes.", input_model=MoneyRateRequest, handler=money_rate.execute))
    server.register_tool(MCPTool(name="stock_screen", description="Screen/filter A-share stocks by market, price range, change percent, volume, turnover, amplitude. Returns sorted results from real-time Sina source. Like a basic stock screener.", input_model=StockScreenRequest, handler=stock_screen.execute))
    server.register_tool(MCPTool(name="insider_trade", description="Get insider/shareholder trade data (高管增减持): top 10 free-float shareholders with holding changes, and historical insider trade records (buy/sell by executives/controlling shareholders). Single-stock query.", input_model=InsiderTradeRequest, handler=insider_trade.execute))
    server.register_tool(MCPTool(name="dividend_rank", description="Get dividend data (股息率/分红排名): market-wide historical dividend ranking by cumulative/average yield, per-report-period dividend plan with yield/EPS/BVPS, and per-stock historical dividend detail. Supports sorting and filtering.", input_model=DividendRankRequest, handler=dividend_rank.execute))
    server.register_tool(MCPTool(name="shareholder_change", description="Get shareholder change data (股东变动): top 10 shareholders with holding changes per stock, and market-wide shareholder holding change summary (by shareholder type: fund/SSF/QFII/etc). Quarterly data.", input_model=ShareholderChangeRequest, handler=shareholder_change.execute))
    server.register_tool(MCPTool(name="disclosure_calendar", description="Get disclosure calendar (披露日历): financial report disclosure schedule with first-scheduled date, change history, and actual disclosure date. Filter by market, period, status (disclosed/pending/changed).", input_model=DisclosureCalendarRequest, handler=disclosure_calendar.execute))
    server.register_tool(MCPTool(name="stock_repurchase", description="Get stock repurchase data (回购明细): company buyback plans with price range, quantity, progress, and actual repurchase amount. Filter by progress status (董事会预案/股东大会通过/实施中/完成实施).", input_model=StockRepurchaseRequest, handler=stock_repurchase.execute))
    server.register_tool(MCPTool(name="stock_compare", description="Compare multiple stocks side-by-side (多股横向对比): real-time quote, PE/PB/market_cap valuation, financial indicators (ROE/margin/debt), dividend yield. 2-10 symbols, layered data loading minimizes API calls.", input_model=StockCompareRequest, handler=stock_compare.execute))
    server.register_tool(MCPTool(name="industry_chain", description="Get industry chain data (产业链上下游): THS industry board summary with change/inflow/leaders, concept board summary with driver events/leaders. For understanding sector relationships and theme tracking.", input_model=IndustryChainRequest, handler=industry_chain.execute))
    server.register_tool(MCPTool(name="stock_warrant", description="Get option/warrant data (权证/期权): ETF options (50ETF/300ETF/etc), commodity options (4 exchanges), CFFEX index options. Real-time quotes with price/volume/open_interest/strike.", input_model=StockWarrantRequest, handler=stock_warrant.execute))
    server.register_tool(MCPTool(name="fund_flow", description="Get fund flow data (主力资金流向): market-level 120-day trend (主力/超大单/大单/中单/小单), industry 90-sector ranking with net inflow, individual stock 120-day history. Sina source.", input_model=FundFlowRequest, handler=fund_flow.execute))
    server.register_tool(MCPTool(name="limit_up_pool", description="Get limit-up/limit-down pool analysis (涨停/跌停股池历史分析): limit-up, limit-down, strong/continuous, previous-day limit performance, sub-new, and broken-limit pools by trade date. EastMoney source.", input_model=LimitUpPoolRequest, handler=limit_up_pool.execute))
    server.register_tool(MCPTool(name="sec_reveal", description="Deep dragon-tiger seat reveal (龙虎榜机构席位深度): stock buy/sell seat detail, active broker seats, institution detail, and institution trace/ranking. EastMoney + Sina sources.", input_model=SecRevealRequest, handler=sec_reveal.execute))

    return server

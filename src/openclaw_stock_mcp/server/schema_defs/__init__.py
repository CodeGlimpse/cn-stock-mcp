"""Schema definitions split into domain modules.

This package replaces the former monolithic schemas.py.
All classes are re-exported via ``openclaw_stock_mcp.server.schemas`` for backward compatibility.
"""

from ._analytics import (
    EventCalendarRequest,
    HotThemeTrackerRequest,
    IndexComposeRequest,
    MultiTimeframeReviewRequest,
    StockCandidateScanRequest,
    WatchlistReviewRequest,
)
from ._macro import (
    BlockTradeRequest,
    ConvertibleBondRequest,
    DerivativesDataRequest,
    DragonTigerRequest,
    ETFSnapshotRequest,
    InstituteHoldRequest,
    MacroIndicatorRequest,
    MoneyRateRequest,
)
from ._market import (
    CapitalFlowRequest,
    LimitStatRequest,
    MarginTradingRequest,
    MarketBriefRequest,
    MarketOverviewRequest,
    MarketPoolRequest,
    NorthboundRequest,
    StockScreenRequest,
    TechnicalIndicatorRequest,
    TradingCalendarRequest,
)
from ._sector import (
    IndustryValuationRankRequest,
    SectorLeadersRequest,
    SectorLookupRequest,
    SectorQuoteRequest,
    SectorReviewRequest,
    SectorRotationReviewRequest,
)
from ._stock import (
    EarningsQualityRequest,
    StockFinancialRequest,
    StockHistoryRequest,
    StockOrderbookRequest,
    StockProfileRequest,
    StockQuoteRequest,
    StockReviewBatchRequest,
    StockReviewRequest,
    StockSearchRequest,
    ValuationRankRequest,
)
from ._types import (
    AdjustType,
    IndicatorType,
    Interval,
    PoolType,
    ProviderName,
    SecType,
    SectorLookupMode,
    SectorType,
)

__all__ = [
    # Types
    "SecType", "ProviderName", "Interval", "AdjustType",
    "IndicatorType", "PoolType", "SectorLookupMode", "SectorType",
    # Stock
    "StockSearchRequest", "StockQuoteRequest", "StockHistoryRequest",
    "StockReviewRequest", "StockReviewBatchRequest", "StockOrderbookRequest",
    "StockProfileRequest", "StockFinancialRequest", "ValuationRankRequest",
    "EarningsQualityRequest",
    # Market
    "TradingCalendarRequest", "MarketOverviewRequest", "MarketBriefRequest",
    "TechnicalIndicatorRequest", "MarketPoolRequest", "CapitalFlowRequest",
    "LimitStatRequest", "NorthboundRequest", "MarginTradingRequest", "StockScreenRequest",
    # Sector
    "SectorReviewRequest", "SectorRotationReviewRequest", "SectorLookupRequest",
    "SectorQuoteRequest", "SectorLeadersRequest", "IndustryValuationRankRequest",
    # Analytics
    "StockCandidateScanRequest", "WatchlistReviewRequest",
    "MultiTimeframeReviewRequest", "HotThemeTrackerRequest",
    "EventCalendarRequest", "IndexComposeRequest",
    # Macro
    "MacroIndicatorRequest", "DragonTigerRequest", "ETFSnapshotRequest",
    "ConvertibleBondRequest", "DerivativesDataRequest", "BlockTradeRequest",
    "InstituteHoldRequest", "MoneyRateRequest",
]

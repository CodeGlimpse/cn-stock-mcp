from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from cn_stock_mcp.server.mcp_server import create_server
from cn_stock_mcp.server.schemas import (
    HotThemeTrackerRequest,
    EventCalendarRequest,
    MarketBriefRequest,
    MarketOverviewRequest,
    MarketPoolRequest,
    MultiTimeframeReviewRequest,
    SectorLookupRequest,
    SectorReviewRequest,
    SectorRotationReviewRequest,
    SectorLeadersRequest,
    StockHistoryRequest,
    StockOrderbookRequest,
    StockCandidateScanRequest,
    StockQuoteRequest,
    StockReviewBatchRequest,
    StockReviewRequest,
    StockSearchRequest,
    TechnicalIndicatorRequest,
    TradingCalendarRequest,
    WatchlistReviewRequest,
)


def build_fastmcp_server() -> FastMCP:
    registry = create_server()
    mcp = FastMCP(registry.name)

    @mcp.tool(name="stock_search", description="Search stocks, indices, funds, or sectors by keyword or code.")
    async def stock_search(
        query: str,
        sec_types: list[str] | None = None,
        market: str = "CN",
        limit: int = 10,
        provider: str | None = None,
    ):
        req = StockSearchRequest(
            query=query,
            sec_types=sec_types,
            market=market,
            limit=limit,
            provider=provider,
        )
        return registry.call_tool("stock_search", req.model_dump(exclude_none=True))

    @mcp.tool(name="stock_quote", description="Get real-time quotes for one or more instruments.")
    async def stock_quote(
        symbols: list[str],
        sec_type: str | None = None,
        fields: list[str] | None = None,
        provider: str | None = None,
        provider_preference: list[str] | None = None,
    ):
        req = StockQuoteRequest(
            symbols=symbols,
            sec_type=sec_type,
            fields=fields,
            provider=provider,
            provider_preference=provider_preference,
        )
        return registry.call_tool("stock_quote", req.model_dump(exclude_none=True))

    @mcp.tool(name="stock_history", description="Get historical price bars for an instrument.")
    async def stock_history(
        symbol: str,
        interval: str,
        sec_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 200,
        adjust: str = "none",
        provider: str | None = None,
        provider_preference: list[str] | None = None,
    ):
        req = StockHistoryRequest(
            symbol=symbol,
            interval=interval,
            sec_type=sec_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            adjust=adjust,
            provider=provider,
            provider_preference=provider_preference,
        )
        return registry.call_tool("stock_history", req.model_dump(exclude_none=True))

    @mcp.tool(name="stock_review", description="Generate a review summary for a stock on a trade date or over a date range.")
    async def stock_review(
        symbol: str,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "akshare",
    ):
        req = StockReviewRequest(
            symbol=symbol,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
        )
        return registry.call_tool("stock_review", req.model_dump(exclude_none=True))

    @mcp.tool(name="stock_review_batch", description="Batch review multiple stocks and rank the results for replay workflows.")
    async def stock_review_batch(
        symbols: list[str],
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "akshare",
        sort_by: str = "relative_strength",
        descending: bool = True,
        top_n: int = 20,
    ):
        req = StockReviewBatchRequest(
            symbols=symbols,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
            sort_by=sort_by,
            descending=descending,
            top_n=top_n,
        )
        return registry.call_tool("stock_review_batch", req.model_dump(exclude_none=True))

    @mcp.tool(name="watchlist_review", description="Review and prioritize a watchlist of symbols.")
    async def watchlist_review(
        symbols: list[str],
        watchlist_name: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "akshare",
        sort_by: str = "watchlist_score",
        descending: bool = True,
        top_n: int = 20,
        min_watchlist_score: float | None = None,
        min_relative_strength: float | None = None,
        min_return: float | None = None,
        max_drawdown_limit: float | None = None,
        min_volume_ratio: float | None = None,
        return_mode: str = "full",
    ):
        req = WatchlistReviewRequest(
            symbols=symbols,
            watchlist_name=watchlist_name,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
            sort_by=sort_by,
            descending=descending,
            top_n=top_n,
            min_watchlist_score=min_watchlist_score,
            min_relative_strength=min_relative_strength,
            min_return=min_return,
            max_drawdown_limit=max_drawdown_limit,
            min_volume_ratio=min_volume_ratio,
            return_mode=return_mode,
        )
        return registry.call_tool("watchlist_review", req.model_dump(exclude_none=True))

    @mcp.tool(name="trading_calendar", description="Query China trading-day calendar for review and backtesting workflows.")
    async def trading_calendar(
        market: str = "CN",
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        recent_limit: int = 5,
        provider: str | None = "akshare",
    ):
        req = TradingCalendarRequest(
            market=market,
            date=date,
            start_date=start_date,
            end_date=end_date,
            recent_limit=recent_limit,
            provider=provider,
        )
        return registry.call_tool("trading_calendar", req.model_dump(exclude_none=True))

    @mcp.tool(name="market_overview", description="Get high-level overview of China market major indices.")
    async def market_overview(
        market: str = "CN",
        include: list[str] | None = None,
        provider: str | None = "mixed",
    ):
        req = MarketOverviewRequest(
            market=market,
            include=include,
            provider=provider,
        )
        return registry.call_tool("market_overview", req.model_dump(exclude_none=True))

    @mcp.tool(name="market_brief", description="Generate a compact market brief by combining overview and pool data.")
    async def market_brief(
        brief_type: str = "close",
        market: str = "CN",
        trade_date: str | None = None,
        include_pools: bool = True,
        top_n: int = 5,
        provider: str | None = "mixed",
    ):
        req = MarketBriefRequest(
            brief_type=brief_type,
            market=market,
            trade_date=trade_date,
            include_pools=include_pools,
            top_n=top_n,
            provider=provider,
        )
        return registry.call_tool("market_brief", req.model_dump(exclude_none=True))

    @mcp.tool(name="multi_timeframe_review", description="Review a symbol across multiple timeframes and summarize alignment/conflicts.")
    async def multi_timeframe_review(
        symbol: str,
        intervals: list[str],
        indicators: list[str] | None = None,
        sec_type: str = "stock",
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 120,
        provider: str | None = "mixed",
    ):
        req = MultiTimeframeReviewRequest(
            symbol=symbol,
            intervals=intervals,
            indicators=indicators,
            sec_type=sec_type,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            provider=provider,
        )
        return registry.call_tool("multi_timeframe_review", req.model_dump(exclude_none=True))

    @mcp.tool(name="technical_indicator", description="Get technical indicator series such as MACD, MA, BOLL, KDJ.")
    async def technical_indicator(
        symbol: str,
        interval: str,
        indicator: str,
        sec_type: str = "index",
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 200,
        provider: str | None = None,
    ):
        req = TechnicalIndicatorRequest(
            symbol=symbol,
            interval=interval,
            indicator=indicator,
            sec_type=sec_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            provider=provider,
        )
        return registry.call_tool("technical_indicator", req.model_dump(exclude_none=True))

    @mcp.tool(name="market_pool", description="Get market pools such as limit-up, limit-down, strong, sub-new, and broken-limit stocks.")
    async def market_pool(
        pool_type: str,
        trade_date: str | None = None,
        limit: int = 100,
        provider: str | None = "zhitu",
    ):
        req = MarketPoolRequest(
            pool_type=pool_type,
            trade_date=trade_date,
            limit=limit,
            provider=provider,
        )
        return registry.call_tool("market_pool", req.model_dump(exclude_none=True))

    @mcp.tool(name="stock_candidate_scan", description="Scan a stock universe and rank candidate setups.")
    async def stock_candidate_scan(
        symbols: list[str] | None = None,
        sector_names: list[str] | None = None,
        sector_type: str = "primary",
        pool_type: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "mixed",
        sort_by: str = "candidate_score",
        descending: bool = True,
        top_n: int = 20,
        limit: int = 20,
        min_candidate_score: float | None = None,
        min_relative_strength: float | None = None,
        min_return: float | None = None,
        max_drawdown_limit: float | None = None,
        min_volume_ratio: float | None = None,
    ):
        req = StockCandidateScanRequest(
            symbols=symbols,
            sector_names=sector_names,
            sector_type=sector_type,
            pool_type=pool_type,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
            sort_by=sort_by,
            descending=descending,
            top_n=top_n,
            limit=limit,
            min_candidate_score=min_candidate_score,
            min_relative_strength=min_relative_strength,
            min_return=min_return,
            max_drawdown_limit=max_drawdown_limit,
            min_volume_ratio=min_volume_ratio,
        )
        return registry.call_tool("stock_candidate_scan", req.model_dump(exclude_none=True))

    @mcp.tool(name="stock_orderbook", description="Get order book data for supported instruments.")
    async def stock_orderbook(
        symbol: str,
        sec_type: str = "stock",
        provider: str | None = "zhitu",
    ):
        req = StockOrderbookRequest(
            symbol=symbol,
            sec_type=sec_type,
            provider=provider,
        )
        return registry.call_tool("stock_orderbook", req.model_dump(exclude_none=True))

    @mcp.tool(name="sector_lookup", description="Lookup sector lists and members.")
    async def sector_lookup(
        mode: str,
        sector_type: str | None = None,
        sector_name: str | None = None,
        limit: int = 100,
        provider: str | None = "zhitu",
    ):
        req = SectorLookupRequest(
            mode=mode,
            sector_type=sector_type,
            sector_name=sector_name,
            limit=limit,
            provider=provider,
        )
        return registry.call_tool("sector_lookup", req.model_dump(exclude_none=True))

    @mcp.tool(name="sector_review", description="Generate a review summary for a sector by aggregating its member stocks.")
    async def sector_review(
        sector_name: str,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "zhitu",
        sort_by: str = "relative_strength",
        descending: bool = True,
        top_n: int = 5,
        limit: int = 100,
        min_relative_strength: float | None = None,
        min_return: float | None = None,
        max_drawdown_limit: float | None = None,
        min_volume_ratio: float | None = None,
        return_mode: str = "full",
    ):
        req = SectorReviewRequest(
            sector_name=sector_name,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
            sort_by=sort_by,
            descending=descending,
            top_n=top_n,
            limit=limit,
            min_relative_strength=min_relative_strength,
            min_return=min_return,
            max_drawdown_limit=max_drawdown_limit,
            min_volume_ratio=min_volume_ratio,
        )
        return registry.call_tool("sector_review", req.model_dump(exclude_none=True))



    @mcp.tool(name="sector_leaders", description="Get leaders/followers/draggers snapshot for a sector.")
    async def sector_leaders(
        sector_name: str,
        sector_type: str = "primary",
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "zhitu",
        sort_by: str = "relative_strength",
        descending: bool = True,
        top_n: int = 3,
        limit: int = 100,
        min_relative_strength: float | None = None,
        min_return: float | None = None,
        max_drawdown_limit: float | None = None,
        min_volume_ratio: float | None = None,
    ):
        req = SectorLeadersRequest(
            sector_name=sector_name,
            sector_type=sector_type,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
            sort_by=sort_by,
            descending=descending,
            top_n=top_n,
            limit=limit,
            min_relative_strength=min_relative_strength,
            min_return=min_return,
            max_drawdown_limit=max_drawdown_limit,
            min_volume_ratio=min_volume_ratio,
            return_mode=return_mode,
        )
        return registry.call_tool("sector_leaders", req.model_dump(exclude_none=True))

    @mcp.tool(name="sector_rotation_review", description="Compare multiple sectors and summarize cross-sector rotation signals.")
    async def sector_rotation_review(
        sector_names: list[str],
        sector_type: str = "primary",
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "zhitu",
        sort_by: str = "avg_relative_strength",
        descending: bool = True,
        top_n: int = 5,
        limit: int = 100,
        member_top_n: int = 3,
        min_relative_strength: float | None = None,
        min_return: float | None = None,
        max_drawdown_limit: float | None = None,
        min_volume_ratio: float | None = None,
        return_mode: str = "full",
    ):
        req = SectorRotationReviewRequest(
            sector_names=sector_names,
            sector_type=sector_type,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
            sort_by=sort_by,
            descending=descending,
            top_n=top_n,
            limit=limit,
            member_top_n=member_top_n,
            min_relative_strength=min_relative_strength,
            min_return=min_return,
            max_drawdown_limit=max_drawdown_limit,
            min_volume_ratio=min_volume_ratio,
        )
        return registry.call_tool("sector_rotation_review", req.model_dump(exclude_none=True))

    @mcp.tool(name="hot_theme_tracker", description="Track hot themes by combining sector rotation and pool snapshots.")
    async def hot_theme_tracker(
        sector_names: list[str] | None = None,
        sector_type: str = "primary",
        watch_name: str | None = None,
        trade_date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "none",
        provider: str | None = "zhitu",
        sort_by: str = "avg_relative_strength",
        descending: bool = True,
        top_n: int = 5,
        sector_limit: int = 10,
        member_limit: int = 20,
        member_top_n: int = 3,
        pool_top_n: int = 5,
        include_pool_snapshot: bool = True,
        min_relative_strength: float | None = None,
        min_return: float | None = None,
        max_drawdown_limit: float | None = None,
        min_volume_ratio: float | None = None,
    ):
        req = HotThemeTrackerRequest(
            sector_names=sector_names,
            sector_type=sector_type,
            watch_name=watch_name,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            provider=provider,
            sort_by=sort_by,
            descending=descending,
            top_n=top_n,
            sector_limit=sector_limit,
            member_limit=member_limit,
            member_top_n=member_top_n,
            pool_top_n=pool_top_n,
            include_pool_snapshot=include_pool_snapshot,
            min_relative_strength=min_relative_strength,
            min_return=min_return,
            max_drawdown_limit=max_drawdown_limit,
            min_volume_ratio=min_volume_ratio,
        )
        return registry.call_tool("hot_theme_tracker", req.model_dump(exclude_none=True))



    @mcp.tool(name="event_calendar", description="Build event timeline (dividend/unlock/profit) for one or more stocks.")
    async def event_calendar(
        symbols: list[str],
        event_types: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        next_event_only: bool = False,
        event_priority: list[str] | None = None,
        provider: str | None = "zhitu",
    ):
        req = EventCalendarRequest(
            symbols=symbols,
            event_types=event_types,
            start_date=start_date,
            end_date=end_date,
            next_event_only=next_event_only,
            event_priority=event_priority,
            provider=provider,
        )
        return registry.call_tool("event_calendar", req.model_dump(exclude_none=True))

    @mcp.tool(name="provider_health", description="Run provider self checks for zhitu and akshare.")
    async def provider_health():
        return registry.call_tool("provider_health", {})

    return mcp

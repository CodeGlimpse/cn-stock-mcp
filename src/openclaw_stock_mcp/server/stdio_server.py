from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from openclaw_stock_mcp.server.mcp_server import create_server
from openclaw_stock_mcp.server.schemas import (
    MarketOverviewRequest,
    MarketPoolRequest,
    SectorLookupRequest,
    StockHistoryRequest,
    StockOrderbookRequest,
    StockQuoteRequest,
    StockSearchRequest,
    TechnicalIndicatorRequest,
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

    @mcp.tool(name="market_pool", description="Get market pools such as limit-up, limit-down, and strong stocks.")
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

    @mcp.tool(name="provider_health", description="Run provider self checks for zhitu and akshare.")
    async def provider_health():
        return registry.call_tool("provider_health", {})

    return mcp

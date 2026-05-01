from __future__ import annotations

from typing import Any, Callable

from pydantic import BaseModel, Field

from openclaw_stock_mcp.app.usecases.market_overview import MarketOverviewUseCase
from openclaw_stock_mcp.app.usecases.market_pool import MarketPoolUseCase
from openclaw_stock_mcp.app.usecases.orderbook import OrderbookUseCase
from openclaw_stock_mcp.app.usecases.provider_health import ProviderHealthUseCase
from openclaw_stock_mcp.app.usecases.sector_lookup import SectorLookupUseCase
from openclaw_stock_mcp.app.usecases.stock_history import StockHistoryUseCase
from openclaw_stock_mcp.app.usecases.stock_quote import StockQuoteUseCase
from openclaw_stock_mcp.app.usecases.stock_search import StockSearchUseCase
from openclaw_stock_mcp.app.usecases.technical_indicator import TechnicalIndicatorUseCase
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
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        request = tool.input_model(**payload)
        return tool.handler(request)


def create_server() -> MCPServerStub:
    server = MCPServerStub(name="openclaw-stock-mcp", version="0.1.0")

    stock_search = StockSearchUseCase()
    stock_quote = StockQuoteUseCase()
    stock_history = StockHistoryUseCase()
    market_overview = MarketOverviewUseCase()
    technical_indicator = TechnicalIndicatorUseCase()
    market_pool = MarketPoolUseCase()
    stock_orderbook = OrderbookUseCase()
    sector_lookup = SectorLookupUseCase()
    provider_health = ProviderHealthUseCase()

    server.register_tool(MCPTool(name="stock_search", description="Search stocks, indices, funds, or sectors by keyword or code.", input_model=StockSearchRequest, handler=stock_search.execute))
    server.register_tool(MCPTool(name="stock_quote", description="Get real-time quotes for one or more instruments.", input_model=StockQuoteRequest, handler=stock_quote.execute))
    server.register_tool(MCPTool(name="stock_history", description="Get historical price bars for an instrument.", input_model=StockHistoryRequest, handler=stock_history.execute))
    server.register_tool(MCPTool(name="market_overview", description="Get high-level overview of China market major indices.", input_model=MarketOverviewRequest, handler=market_overview.execute))
    server.register_tool(MCPTool(name="technical_indicator", description="Get technical indicator series such as MACD, MA, BOLL, KDJ.", input_model=TechnicalIndicatorRequest, handler=technical_indicator.execute))
    server.register_tool(MCPTool(name="market_pool", description="Get market pools such as limit-up, limit-down, and strong stocks.", input_model=MarketPoolRequest, handler=market_pool.execute))
    server.register_tool(MCPTool(name="stock_orderbook", description="Get order book data for supported instruments.", input_model=StockOrderbookRequest, handler=stock_orderbook.execute))
    server.register_tool(MCPTool(name="sector_lookup", description="Lookup sector lists and members.", input_model=SectorLookupRequest, handler=sector_lookup.execute))
    server.register_tool(MCPTool(name="provider_health", description="Run provider self checks for zhitu and akshare.", input_model=EmptyRequest, handler=provider_health.execute))

    return server

from __future__ import annotations

import asyncio
import json

from mcp import types

from cn_stock_mcp.server.stdio_server import build_fastmcp_server


def _run(coro):
    return asyncio.run(coro)


def test_mcp_server_lists_every_registered_tool():
    server = build_fastmcp_server()
    handler = server.get_request_handler("tools/list")
    assert handler is not None

    result = _run(handler.handler(None, None))

    assert len(result.tools) == 52
    assert {tool.name for tool in result.tools} == {
        "stock_search",
        "stock_quote",
        "stock_history",
        "stock_review",
        "stock_review_batch",
        "watchlist_review",
        "trading_calendar",
        "market_overview",
        "market_brief",
        "technical_indicator",
        "multi_timeframe_review",
        "market_pool",
        "stock_orderbook",
        "stock_candidate_scan",
        "sector_lookup",
        "sector_review",
        "sector_rotation_review",
        "sector_leaders",
        "hot_theme_tracker",
        "provider_health",
        "event_calendar",
        "stock_profile",
        "capital_flow",
        "stock_financial",
        "limit_stat",
        "northbound",
        "valuation_rank",
        "index_compose",
        "index_enhance",
        "industry_valuation_rank",
        "earnings_quality",
        "macro_indicator",
        "dragon_tiger",
        "etf_snapshot",
        "convertible_bond",
        "derivatives_data",
        "margin_trading",
        "block_trade",
        "institute_hold",
        "money_rate",
        "stock_screen",
        "insider_trade",
        "dividend_rank",
        "shareholder_change",
        "disclosure_calendar",
        "stock_repurchase",
        "stock_compare",
        "industry_chain",
        "stock_warrant",
        "fund_flow",
        "limit_up_pool",
        "sec_reveal",
    }

    provider_health = next(tool for tool in result.tools if tool.name == "provider_health")
    assert provider_health.input_schema["type"] == "object"


def test_mcp_server_routes_invalid_arguments_without_upstream_call():
    server = build_fastmcp_server()
    handler = server.get_request_handler("tools/call")
    assert handler is not None

    result = _run(
        handler.handler(
            None,
            types.CallToolRequestParams(
                name="stock_quote",
                arguments={"symbols": []},
            ),
        )
    )

    assert result.is_error is True
    payload = json.loads(result.content[0].text)
    assert payload["success"] is False
    assert payload["error"]["error_code"] == "INVALID_ARGUMENT"


def test_mcp_server_returns_unknown_tool_as_mcp_error():
    server = build_fastmcp_server()
    handler = server.get_request_handler("tools/call")
    assert handler is not None

    result = _run(
        handler.handler(
            None,
            types.CallToolRequestParams(name="does_not_exist", arguments={}),
        )
    )

    assert result.is_error is True
    payload = json.loads(result.content[0].text)
    assert payload["error"]["error_code"] == "TOOL_NOT_FOUND"

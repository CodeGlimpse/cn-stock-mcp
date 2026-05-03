from __future__ import annotations

import json
import traceback

from openclaw_stock_mcp.infra.config import get_settings
from openclaw_stock_mcp.server.transport import TransportApp
from openclaw_stock_mcp.providers.zhitu_provider import ZhituProvider


TEST_CASES = [
    {
        "name": "list_tools",
        "kind": "meta",
    },
    {
        "name": "provider_health",
        "tool": "provider_health",
        "payload": {},
    },
    {
        "name": "stock_search_min",
        "tool": "stock_search",
        "payload": {"query": "平安银行", "limit": 5},
    },
    {
        "name": "stock_quote_stock_main",
        "tool": "stock_quote",
        "payload": {"symbols": ["600519.SH"], "sec_type": "stock"},
        "requires_zhitu": True,
    },
    {
        "name": "stock_quote_index",
        "tool": "stock_quote",
        "payload": {"symbols": ["000001.SH"], "sec_type": "index"},
        "requires_zhitu": True,
    },
    {
        "name": "market_overview",
        "tool": "market_overview",
        "payload": {"market": "CN"},
        "requires_zhitu": True,
    },
    {
        "name": "sector_lookup_list_primary",
        "tool": "sector_lookup",
        "payload": {"mode": "list", "sector_type": "primary", "limit": 5},
        "requires_zhitu": True,
    },
    {
        "name": "sector_lookup_children_members",
        "tool": "sector_lookup",
        "payload": {"mode": "children", "sector_name": "TFG板块趋势", "limit": 5},
        "requires_zhitu": True,
    },
    {
        "name": "stock_history_stock_daily",
        "tool": "stock_history",
        "payload": {"symbol": "600519", "sec_type": "stock", "interval": "1d", "limit": 5},
    },
    {
        "name": "stock_review_trade_date",
        "tool": "stock_review",
        "payload": {"symbol": "600519.SH", "trade_date": "2026-05-01"},
    },
    {
        "name": "technical_indicator_macd",
        "tool": "technical_indicator",
        "payload": {"symbol": "000001.SH", "sec_type": "index", "interval": "1d", "indicator": "macd", "limit": 5},
        "requires_zhitu": True,
    },
    {
        "name": "market_pool_limit_up",
        "kind": "direct_provider",
        "requires_zhitu": True,
        "provider_method": "get_market_pool",
        "kwargs": {"pool_type": "limit_up", "trade_date": "2026-04-30"}
    },
    {
        "name": "stock_orderbook_star",
        "kind": "direct_provider",
        "requires_zhitu": True,
        "provider_method": "get_orderbook",
        "kwargs": {"symbol": "688001.SH", "sec_type": "stock"}
    }
]


def _to_jsonable(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    return value


def main() -> None:
    app = TransportApp()
    settings = get_settings()
    has_zhitu = bool(settings.resolve_zhitu_token())
    zhitu = ZhituProvider() if has_zhitu else None

    for case in TEST_CASES:
        print(f"\n=== CASE: {case['name']} ===")
        if case.get("requires_zhitu") and not has_zhitu:
            print(json.dumps({
                "skipped": True,
                "reason": "ZHITU token is unavailable",
            }, ensure_ascii=False, indent=2))
            continue
        try:
            if case.get("kind") == "meta":
                result = app.list_tools()
            elif case.get("kind") == "direct_provider":
                result = getattr(zhitu, case["provider_method"])(**case["kwargs"])
            else:
                result = app.call_tool(case["tool"], case["payload"])
            print(json.dumps(_to_jsonable(result), ensure_ascii=False, indent=2))
        except Exception as exc:
            print(json.dumps({
                "error": str(exc),
                "type": type(exc).__name__,
            }, ensure_ascii=False, indent=2))
            traceback.print_exc()


if __name__ == "__main__":
    main()

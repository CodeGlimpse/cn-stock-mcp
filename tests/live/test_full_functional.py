from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from typing import Any, Callable

import pytest

from cn_stock_mcp.infra.config import get_settings

from conftest import assert_success


PayloadBuilder = Callable[[dict[str, str | None]], dict[str, Any]]


@dataclass(frozen=True)
class FunctionalCase:
    tool: str
    payload: PayloadBuilder
    expected_fields: tuple[str, ...]
    requires_zhitu: bool = False
    context_key: str | None = None


def _stock_payload(ctx: dict[str, str | None]) -> dict[str, Any]:
    return {"symbols": [ctx["stock"], ctx["stock_2"]], "sec_type": "stock"}


FUNCTIONAL_CASES: tuple[FunctionalCase, ...] = (
    FunctionalCase("stock_search", lambda _: {"query": "平安银行", "limit": 5}, ("items", "total", "source")),
    FunctionalCase("stock_quote", lambda c: {"symbols": [c["stock"]], "sec_type": "stock"}, ("items", "errors", "partial_failure"), True),
    FunctionalCase("stock_snapshot", lambda c: {"symbols": [c["stock"]], "include": ["quote", "history"], "history_limit": 5}, ("items", "reviewed_count", "partial_failure"), True),
    FunctionalCase("stock_history", lambda c: {"symbol": c["stock"], "sec_type": "stock", "interval": "1d", "limit": 5, "provider": "akshare"}, ("symbol", "items", "count")),
    FunctionalCase("stock_review", lambda c: {"symbol": c["stock"], "trade_date": c["recent_date"]}, ("symbol", "latest_bar", "summary")),
    FunctionalCase("stock_review_batch", lambda c: {"symbols": [c["stock"], c["stock_2"]], "trade_date": c["recent_date"], "top_n": 2, "sort_by": "relative_strength"}, ("items", "total_symbols", "summary")),
    FunctionalCase("watchlist_review", lambda c: {"symbols": [c["stock"], c["stock_2"]], "trade_date": c["recent_date"], "top_n": 2, "sort_by": "watchlist_score"}, ("items", "member_count", "summary")),
    FunctionalCase("trading_calendar", lambda c: {"market": "CN", "date": c["recent_date"], "recent_limit": 5}, ("date", "is_trading_day", "recent_trading_days")),
    FunctionalCase("market_overview", lambda _: {"market": "CN", "provider": "mixed"}, ("indices", "market", "source")),
    FunctionalCase("market_brief", lambda _: {"brief_type": "close", "include_pools": False, "top_n": 3, "provider": "mixed"}, ("overview", "index_ranking", "summary")),
    FunctionalCase("technical_indicator", lambda c: {"symbol": c["index"], "sec_type": "index", "interval": "1d", "indicator": "macd", "limit": 5}, ("items", "count"), True),
    FunctionalCase("multi_timeframe_review", lambda c: {"symbol": c["stock"], "sec_type": "stock", "intervals": ["1d", "1w"], "indicators": ["macd"], "limit": 20}, ("items", "summary"), True),
    FunctionalCase("market_pool", lambda c: {"pool_type": "limit_up", "trade_date": c["recent_date"], "limit": 5}, ("items", "count", "trade_date"), True),
    FunctionalCase("stock_orderbook", lambda c: {"symbol": c["stock"], "sec_type": "stock"}, ("symbol", "bids", "asks"), True),
    FunctionalCase("stock_candidate_scan", lambda c: {"symbols": [c["stock"], c["stock_2"]], "trade_date": c["recent_date"], "top_n": 2, "limit": 2, "sort_by": "candidate_score"}, ("items", "member_count", "summary")),
    FunctionalCase("sector_lookup", lambda _: {"mode": "list", "sector_type": "primary", "limit": 5}, ("items", "total", "sector_type"), True),
    FunctionalCase("sector_review", lambda c: {"sector_name": c["primary_sector"], "sector_type": "primary", "trade_date": c["recent_date"], "top_n": 3, "limit": 5}, ("items", "member_count", "summary"), True, "primary_sector"),
    FunctionalCase("sector_rotation_review", lambda c: {"sector_names": [c["primary_sector"], c["primary_sector_2"]], "sector_type": "primary", "trade_date": c["recent_date"], "top_n": 1, "member_top_n": 2, "limit": 5}, ("items", "member_count", "summary"), True, "primary_sector_2"),
    FunctionalCase("sector_leaders", lambda c: {"sector_name": c["primary_sector"], "sector_type": "primary", "trade_date": c["recent_date"], "top_n": 3, "limit": 5}, ("leaders", "followers", "draggers"), True, "primary_sector"),
    FunctionalCase("hot_theme_tracker", lambda c: {"sector_names": [c["primary_sector"], c["primary_sector_2"]], "sector_type": "primary", "trade_date": c["recent_date"], "top_n": 1, "sector_limit": 3, "member_limit": 5, "include_pool_snapshot": False}, ("themes", "summary"), True, "primary_sector"),
    FunctionalCase("provider_health", lambda _: {}, ("overall", "checks")),
    FunctionalCase("event_calendar", lambda c: {"symbols": [c["stock"]], "event_types": ["dividend", "unlock", "profit"], "next_event_only": True}, ("items", "count"), True),
    FunctionalCase("stock_profile", lambda c: {"symbol": c["stock"], "include": ["profile", "valuation"]}, ("resolved_symbol", "profile", "valuation"), True),
    FunctionalCase("capital_flow", lambda _: {"flow_type": "market", "limit": 5}, ("flow_type", "records", "count")),
    FunctionalCase("stock_financial", lambda c: {"symbol": c["stock"], "include": ["snapshot", "history"], "history_n": 4}, ("symbol", "snapshot", "history")),
    FunctionalCase("limit_stat", lambda c: {"trade_date": c["recent_date"], "include": ["summary", "limit_up", "broken_limit", "previous_day"]}, ("trade_date", "stat", "summary_text")),
    FunctionalCase("northbound", lambda _: {"include": ["daily_summary", "history"], "history_n": 5}, ("daily_summary", "history", "source")),
    FunctionalCase("valuation_rank", lambda c: {"symbols": [c["stock"], c["stock_2"]], "top_n": 2}, ("market", "items", "summary", "source"), True),
    FunctionalCase("index_compose", lambda c: {"index_code": c["index_code"], "top_n": 5}, ("summary", "items", "source")),
    FunctionalCase("index_enhance", lambda c: {"index_code": c["index_code"], "top_n": 5, "start_date": c["start_date"], "end_date": c["recent_date"]}, ("summary", "members", "summary_text"), True),
    FunctionalCase("industry_valuation_rank", lambda c: {"sector_names": [c["primary_sector"]], "sector_type": "primary", "top_n": 1, "member_limit": 10}, ("items", "summary", "source"), True, "primary_sector"),
    FunctionalCase("earnings_quality", lambda c: {"symbol": c["stock"]}, ("symbol", "score", "metrics", "summary")),
    FunctionalCase("macro_indicator", lambda _: {"indicator": "cpi", "region": "cn", "include": ["latest", "history"], "history_n": 3}, ("indicator", "latest", "history", "summary")),
    FunctionalCase("dragon_tiger", lambda c: {"include": ["daily_detail", "institution"], "trade_date": c["previous_date"], "top_n": 5}, ("daily_detail", "institution", "summary")),
    FunctionalCase("etf_snapshot", lambda _: {"include": ["spot"], "top_n": 5}, ("spot", "spot_count", "summary")),
    FunctionalCase("convertible_bond", lambda _: {"include": ["spot"], "top_n": 5}, ("spot", "spot_count", "summary")),
    FunctionalCase("derivatives_data", lambda _: {"include": ["futures_spot", "qvix"], "history_n": 5}, ("futures_spot", "qvix", "summary")),
    FunctionalCase("margin_trading", lambda _: {"include": ["summary", "detail"], "exchange": "both", "top_n": 5}, ("summary", "detail", "summary_text")),
    FunctionalCase("block_trade", lambda c: {"include": ["daily_detail", "daily_stat"], "trade_date": c["previous_date"], "top_n": 5}, ("daily_detail", "daily_stat", "summary")),
    FunctionalCase("institute_hold", lambda _: {"include": ["summary"], "quarter": "auto", "top_n": 5}, ("summary", "quarter", "summary_text")),
    FunctionalCase("money_rate", lambda _: {"include": ["shibor", "repo"], "shibor_days": 5}, ("shibor", "repo", "summary")),
    FunctionalCase("stock_screen", lambda _: {"market": "main", "top_n": 5, "sort_by": "change_pct"}, ("items", "total_before_filter", "total_after_filter")),
    FunctionalCase("insider_trade", lambda c: {"symbol": c["stock"], "include": ["top10", "change"], "quarter": "auto"}, ("top10", "change", "summary")),
    FunctionalCase("dividend_rank", lambda _: {"include": ["rank", "plan"], "report_date": "latest", "top_n": 5}, ("rank", "plan", "summary")),
    FunctionalCase("shareholder_change", lambda c: {"symbol": c["stock"], "include": ["top10", "change"], "quarter": "auto"}, ("top10", "change", "summary")),
    FunctionalCase("disclosure_calendar", lambda _: {"market": "沪深京", "period": "auto", "status": "all", "top_n": 5}, ("items", "total_count", "summary")),
    FunctionalCase("stock_repurchase", lambda _: {"status": "all", "top_n": 5}, ("items", "total_count", "summary")),
    FunctionalCase("stock_compare", _stock_payload, ("items", "total_count", "symbols_compared", "summary"), True),
    FunctionalCase("industry_chain", lambda _: {"include": ["industry_list", "concept_list"], "top_n": 5}, ("industry_list", "concept_list", "summary")),
    FunctionalCase("stock_warrant", lambda _: {"include": ["etf_option"], "top_n": 5}, ("etf_option", "summary")),
    FunctionalCase("fund_flow", lambda _: {"include": ["market", "industry"], "period": "即时", "top_n": 5}, ("market", "industry", "summary")),
    FunctionalCase("limit_up_pool", lambda c: {"include": ["limit_up", "limit_down", "strong"], "trade_date": c["recent_date"], "top_n": 5}, ("limit_up", "limit_down", "strong", "summary")),
    FunctionalCase("sec_reveal", lambda _: {"include": ["institution_detail", "institution_trace"], "period": "5", "top_n": 5}, ("institution_detail", "institution_trace", "summary")),
)


# These are the minimum data-bearing sections for the selected requests.  A
# successful envelope with an empty section is not a functional pass: it must
# surface as a test failure so upstream drift or a broken adapter is visible.
REQUIRED_NON_EMPTY_FIELDS: dict[str, tuple[str, ...]] = {
    "stock_search": ("items",),
    "stock_quote": ("items",),
    "stock_snapshot": ("items",),
    "stock_history": ("items",),
    "stock_review": ("latest_bar", "summary"),
    "stock_review_batch": ("items",),
    "watchlist_review": ("items",),
    "trading_calendar": ("recent_trading_days",),
    "market_overview": ("indices",),
    "market_brief": ("index_ranking",),
    "technical_indicator": ("items",),
    "multi_timeframe_review": ("items",),
    # Pools and event calendars can legitimately be empty for a valid date;
    # their count/date/meta fields are still checked below.
    "stock_orderbook": ("bids", "asks"),
    "stock_candidate_scan": ("items",),
    "sector_lookup": ("items",),
    "sector_review": ("items",),
    "sector_rotation_review": ("items",),
    "sector_leaders": ("leaders",),
    "hot_theme_tracker": ("themes",),
    "provider_health": ("checks",),
    "stock_profile": ("profile",),
    "capital_flow": ("records",),
    "stock_financial": ("snapshot", "history"),
    "limit_stat": ("stat",),
    "northbound": ("history",),
    "valuation_rank": ("items",),
    "index_compose": ("items",),
    "index_enhance": ("members",),
    "industry_valuation_rank": ("items",),
    "earnings_quality": ("metrics",),
    "macro_indicator": ("latest", "history"),
    # Daily LHB/block-trade sections may have no rows on a valid trading day;
    # the response must retain the requested section and quality flag.
    "etf_snapshot": ("spot",),
    "convertible_bond": ("spot",),
    "derivatives_data": ("futures_spot",),
    # These two datasets can be legitimately unavailable or empty for the
    # current upstream date/quarter; completeness is enforced by count,
    # partial-failure, and quality metadata rather than a false non-empty gate.
    "margin_trading": (),

    "institute_hold": (),
    "money_rate": ("shibor",),
    "stock_screen": ("items",),
    "insider_trade": ("top10",),
    "dividend_rank": ("rank",),
    "shareholder_change": ("top10",),
    "disclosure_calendar": ("items",),
    "stock_repurchase": ("items",),
    "stock_compare": ("items",),
    "industry_chain": ("industry_list",),
    "stock_warrant": ("etf_option",),
    "fund_flow": ("market", "industry"),

    "sec_reveal": ("institution_detail",),
}


def _has_zhitu() -> bool:
    return bool(get_settings().resolve_zhitu_token())


def _mappings(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _mappings(child)


def _numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value))


def _assert_no_anomalous_numbers(data: Any) -> None:
    for mapping in _mappings(data):
        for key, value in mapping.items():
            if isinstance(value, float):
                assert isfinite(value), f"non-finite value at {key}"
            if isinstance(value, str):
                assert value.strip().lower() not in {"nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}, f"anomalous value at {key}"


def _assert_ohlc_and_change_invariants(data: Any) -> None:
    for row in _mappings(data):
        high, low, close, opening = (row.get(name) for name in ("high", "low", "close", "open"))
        if _numeric(high) and _numeric(low):
            assert high >= low, f"high < low in {row}"
        if _numeric(high) and _numeric(close):
            assert high >= close, f"high < close in {row}"
        if _numeric(low) and _numeric(close):
            assert low <= close, f"low > close in {row}"
        if _numeric(high) and _numeric(opening):
            assert high >= opening, f"high < open in {row}"
        if _numeric(low) and _numeric(opening):
            assert low <= opening, f"low > open in {row}"

        price = row.get("price", row.get("close"))
        previous = row.get("prev_close", row.get("previous_close"))
        change = row.get("change")
        change_percent = row.get("change_percent")
        if _numeric(price) and _numeric(previous) and previous != 0:
            expected_change = price - previous
            if _numeric(change):
                assert abs(change - expected_change) <= max(0.05, abs(expected_change) * 0.02), f"change disagrees with price/prev_close in {row}"
            if _numeric(change_percent):
                expected_percent = expected_change / previous * 100
                assert abs(change_percent - expected_percent) <= max(0.2, abs(expected_percent) * 0.03), f"change_percent disagrees with price/prev_close in {row}"


def _parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    text = value.strip().replace("/", "-")
    if len(text) == 8 and text.isdigit():
        text = f"{text[:4]}-{text[4:6]}-{text[6:]}"
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _assert_date_series_are_coherent(data: Any) -> None:
    for mapping in _mappings(data):
        for field in ("date", "trade_date", "time", "timestamp", "report_date"):
            if field not in mapping:
                continue
            if field == "time" and isinstance(mapping[field], str) and len(mapping[field].strip()) <= 8:
                # Intraday order-book rows commonly expose HH:MM:SS.
                continue
            if field == "report_date" and isinstance(mapping[field], str) and mapping[field].strip().upper().startswith("Q"):
                # Some financial adapters expose a fiscal quarter label (Q1/Q2…)
                # alongside a separate report date.
                continue
            parsed = _parse_date(mapping[field])
            if mapping[field] not in (None, ""):
                assert parsed is not None, f"unparseable {field}: {mapping[field]!r}"


def _assert_count_fields(data: Any) -> None:
    if not isinstance(data, dict):
        return
    pairs = (
        ("count", "items"),
        ("count", "records"),
        ("total", "items"),
        ("total_count", "items"),
        ("spot_count", "spot"),
        ("history_count", "history"),
        ("rank_count", "rank"),
        ("plan_count", "plan"),
        ("detail_count", "detail"),
    )
    for count_key, container_key in pairs:
        count = data.get(count_key)
        rows = data.get(container_key)
        if isinstance(count, int) and isinstance(rows, list):
            assert count == len(rows), f"{count_key} does not match {container_key} length"

    for count_key, count in data.items():
        if not count_key.endswith("_count") or not isinstance(count, int):
            continue
        container_key = count_key[: -len("_count")]
        rows = data.get(container_key)
        if isinstance(rows, list):
            assert count == len(rows), f"{count_key} does not match {container_key} length"


def _assert_required_data_fields(data: dict[str, Any], tool: str) -> None:
    for field in REQUIRED_NON_EMPTY_FIELDS.get(tool, ()):
        value = data.get(field)
        if isinstance(value, (list, dict, str)):
            assert len(value) > 0, f"{tool} returned an empty required section: {field}"
        else:
            assert value is not None, f"{tool} returned null required section: {field}"


def _assert_empty_sections_are_explicit(data: dict[str, Any], result: dict[str, Any], tool: str) -> None:
    """Empty optional upstream sections must be represented, not silently lost."""
    quality = result.get("meta", {}).get("data_quality", {})
    for field in ("items", "events", "daily_detail", "institution", "limit_up", "limit_down", "strong", "broken"):
        if field not in data:
            continue
        value = data[field]
        if isinstance(value, list) and not value:
            flags = quality.get("flags", [])
            assert "empty_result" in flags or data.get("partial_failure"), (
                f"{tool} returned an empty {field!r} section without an explicit quality/partial-failure signal"
            )


def _assert_requested_symbol_coverage(data: dict[str, Any], tool: str, payload: dict[str, Any]) -> None:
    requested = payload.get("symbols")
    if not isinstance(requested, list):
        return
    requested_set = {str(symbol).upper() for symbol in requested}
    rows = data.get("items")
    if not isinstance(rows, list) or not rows:
        return
    returned = {str(row.get("symbol", "")).upper() for row in rows if isinstance(row, dict)}
    assert returned <= requested_set, f"{tool} returned symbols outside the request: {returned - requested_set}"
    if not data.get("partial_failure") and tool in {"stock_quote", "stock_compare", "stock_review_batch", "watchlist_review"}:
        assert returned == requested_set, f"{tool} silently dropped requested symbols: {requested_set - returned}"


def _assert_sorted_by_request(data: dict[str, Any], payload: dict[str, Any]) -> None:
    sort_by = payload.get("sort_by")
    if not sort_by:
        return
    descending = bool(payload.get("descending", True))
    for container_key in ("items", "records", "rank", "spot", "industry", "market"):
        rows = data.get(container_key)
        if not isinstance(rows, list) or len(rows) < 2 or not all(isinstance(row, dict) and sort_by in row for row in rows):
            continue
        values = [row[sort_by] for row in rows]
        if all(_numeric(value) for value in values):
            assert values == sorted(values, reverse=descending), f"{container_key} is not sorted by {sort_by}"


def _assert_history_shape(data: dict[str, Any], payload: dict[str, Any]) -> None:
    if "items" not in data or "interval" not in data:
        return
    rows = data.get("items")
    assert isinstance(rows, list)
    limit = payload.get("limit")
    if isinstance(limit, int):
        assert len(rows) <= limit
    dates = []
    for row in rows:
        assert isinstance(row, dict)
        value = row.get("time") or row.get("date") or row.get("trade_date")
        parsed = _parse_date(value)
        if parsed is not None:
            dates.append(parsed)
    if dates:
        assert len(dates) == len(set(dates)), "history contains duplicate dates"
        assert dates == sorted(dates), "history is not in ascending date order"


def _assert_response_quality(result: dict[str, Any], case: FunctionalCase, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    assert result.get("success") is True, f"{case.tool} failed: {result.get('error')}"
    assert result.get("error") is None
    meta = result.get("meta")
    assert isinstance(meta, dict)
    assert isinstance(meta.get("request_id"), str) and meta["request_id"].startswith("req_")
    assert meta.get("schema_version") == "v1"
    freshness = meta.get("freshness")
    assert isinstance(freshness, dict)
    assert freshness.get("status") in {"realtime", "dated", "unknown"}
    quality = meta.get("data_quality")
    assert isinstance(quality, dict)
    assert quality.get("schema") == "data_quality_v1"
    assert quality.get("label") in {"high", "medium", "low"}
    assert isinstance(quality.get("score"), (int, float)) and 0 <= quality["score"] <= 100
    assert isinstance(quality.get("flags"), list)

    data = assert_success(result)
    assert isinstance(data, dict), f"{case.tool} returned non-object data"
    for field in case.expected_fields:
        assert field in data, f"{case.tool} omitted required response field {field!r}"
    _assert_required_data_fields(data, case.tool)
    _assert_empty_sections_are_explicit(data, result, case.tool)
    _assert_requested_symbol_coverage(data, case.tool, payload or {})
    _assert_sorted_by_request(data, payload or {})
    _assert_history_shape(data, payload or {})
    if data.get("partial_failure"):
        assert "partial_failure" in quality["flags"], f"{case.tool} hid a partial failure"
    _assert_no_anomalous_numbers(data)
    _assert_ohlc_and_change_invariants(data)
    _assert_date_series_are_coherent(data)
    _assert_count_fields(data)
    return data


def test_full_registry_matches_functional_manifest(full_app):
    registry_names = {item["name"] for item in full_app.list_tools()}
    manifest_names = {case.tool for case in FUNCTIONAL_CASES}
    assert len(registry_names) == 53
    assert len(manifest_names) == 53
    assert registry_names == manifest_names


@pytest.mark.live
@pytest.mark.functional
@pytest.mark.slow
@pytest.mark.transport
@pytest.mark.parametrize("case", FUNCTIONAL_CASES, ids=lambda item: item.tool)
def test_every_tool_returns_a_complete_quality_annotated_response(full_app, live_context, case: FunctionalCase):
    if case.requires_zhitu and not _has_zhitu():
        pytest.skip("ZHITU token is not available")
    if case.context_key and not live_context.get(case.context_key):
        pytest.skip(f"live context did not resolve {case.context_key}")
    if case.tool == "hot_theme_tracker" and not live_context.get("primary_sector_2"):
        pytest.skip("live context did not resolve a second primary sector")

    payload = case.payload(live_context)
    result = full_app.call_tool(case.tool, payload)
    _assert_response_quality(result, case, payload)


@pytest.mark.live
@pytest.mark.functional
@pytest.mark.transport
def test_quote_and_history_are_consistent_when_the_source_date_matches(full_app, live_context):
    if not _has_zhitu():
        pytest.skip("ZHITU token is not available")

    quote_result = full_app.call_tool("stock_quote", {"symbols": [live_context["stock"]], "sec_type": "stock"})
    history_result = full_app.call_tool("stock_history", {"symbol": live_context["stock"], "sec_type": "stock", "interval": "1d", "limit": 5})
    quote_data = _assert_response_quality(quote_result, FunctionalCase("stock_quote", lambda _: {}, ("items",)))
    history_data = _assert_response_quality(history_result, FunctionalCase("stock_history", lambda _: {}, ("items", "count")), {"limit": 5})
    quote = (quote_data.get("items") or [None])[0]
    bars = history_data.get("items") or []
    if not isinstance(quote, dict) or not bars or not isinstance(bars[-1], dict):
        pytest.skip("quote/history did not return comparable rows")

    quote_date = _parse_date(quote.get("timestamp") or quote.get("trade_date") or quote.get("date"))
    bar_date = _parse_date(bars[-1].get("time") or bars[-1].get("trade_date") or bars[-1].get("date"))
    quote_price = quote.get("price")
    bar_close = bars[-1].get("close")
    if quote_date and bar_date and quote_date == bar_date and _numeric(quote_price) and _numeric(bar_close):
        assert abs(quote_price - bar_close) <= max(0.05, abs(bar_close) * 0.02)

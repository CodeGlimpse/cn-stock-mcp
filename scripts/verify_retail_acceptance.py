"""Bounded retail acceptance over MCP stdio, with allowlisted evidence only.

Without --run-live the CLI only prints its plan: it does not start the server,
read the credential file, or access providers. A live report is MCP client
evidence, not evidence that the Codex application itself has been accepted.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from functools import partial
import json
import logging
import math
import os
from pathlib import Path
import platform
import re
import tempfile
import time
from typing import Any


TOOLS = (
    "trading_calendar", "stock_search", "stock_quote", "stock_history",
    "stock_snapshot", "stock_review", "watchlist_review", "market_brief",
    "hot_theme_tracker", "sector_review",
)
REQUIRED = {
    "trading_calendar": ("recent_trading_days", "session_context"),
    "stock_search": ("items",),
    "stock_quote": ("items",),
    "stock_history": ("items",),
    "stock_snapshot": ("items",),
    "stock_review": ("latest_bar", "summary"),
    "watchlist_review": ("items", "summary"),
    "market_brief": ("overview", "index_ranking", "summary"),
    "hot_theme_tracker": ("themes", "summary"),
    "sector_review": ("items", "summary"),
}
ERRORS = {
    "INVALID_ARGUMENT", "TOOL_NOT_FOUND", "EMPTY_RESULT", "INTERNAL_ERROR",
    "PROVIDER_AUTH_FAILED", "PROVIDER_TIMEOUT", "PROVIDER_UNAVAILABLE",
    "PROVIDER_RATE_LIMITED", "PROVIDER_QUOTA_EXCEEDED", "PROVIDER_CIRCUIT_OPEN",
    "PROVIDER_BAD_RESPONSE", "NOT_SUPPORTED",
}
BLOCKING_ERRORS = {code for code in ERRORS if code.startswith("PROVIDER_")}
QUALITY_FLAGS = {
    "provider_fallback", "partial_failure", "stale_cache", "empty_result",
    "empty_records", "missing_fields", "anomalous_values", "semantic_anomalies",
    "aged_data", "freshness_unknown",
}
SESSIONS = {
    "pre_open", "morning_session", "lunch_break", "afternoon_session",
    "post_close", "non_trading_day", "historical",
}
PROVIDERS = {"akshare", "zhitu", "mixed", "eastmoney", "sina"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _date_text(value: Any) -> str | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        return None


def _time_text(value: Any) -> str | None:
    if _date_text(value):
        return value
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T[0-9:.+Z-]+", value):
        return None
    try:
        return datetime.fromisoformat(value).isoformat(timespec="seconds")
    except ValueError:
        return None


def _error_code(value: Any) -> str:
    return value if isinstance(value, str) and value in ERRORS else "UNKNOWN_ERROR"


def request_for(tool: str, context: dict[str, str]) -> dict[str, Any]:
    """Small fixed samples; theme discovery uses only the retail tool surface."""
    symbol = "000001.SZ"
    trade_date = context.get("trade_date")
    requests = {
        "trading_calendar": {"market": "CN", "recent_limit": 5},
        "stock_search": {"query": "平安银行", "limit": 5},
        "stock_quote": {"symbols": [symbol], "sec_type": "stock"},
        "stock_history": {"symbol": symbol, "sec_type": "stock", "interval": "1d", "limit": 5, "provider": "akshare"},
        "stock_snapshot": {"symbols": [symbol], "include": ["quote", "history"], "history_limit": 5, "max_total_timeout_seconds": 30},
        "stock_review": {"symbol": symbol, "trade_date": trade_date},
        "watchlist_review": {"symbols": [symbol], "trade_date": trade_date, "top_n": 1, "sort_by": "watchlist_score"},
        "market_brief": {"brief_type": "close", "include_pools": False, "top_n": 3, "provider": "mixed"},
        "hot_theme_tracker": {"sector_type": "primary", "trade_date": trade_date, "top_n": 1, "sector_limit": 2, "member_limit": 2, "member_top_n": 1, "include_pool_snapshot": False},
        "sector_review": {"sector_name": context.get("sector_name"), "sector_type": "primary", "trade_date": trade_date, "top_n": 1, "limit": 2},
    }
    return requests[tool]


def assess(tool: str, payload: Any, *, elapsed_ms: int, mcp_error: bool = False) -> dict[str, Any]:
    """Never retain arbitrary payloads, error messages, paths, URLs or scores."""
    result: dict[str, Any] = {"tool": tool, "status": "FAIL", "latency_ms": elapsed_ms, "reason": "INVALID_ENVELOPE"}
    if not isinstance(payload, dict) or not isinstance(payload.get("success"), bool):
        return result
    if payload["success"] is False:
        error = payload.get("error")
        code = _error_code(error.get("error_code")) if isinstance(error, dict) else "UNKNOWN_ERROR"
        result.update(status="BLOCKED" if code in BLOCKING_ERRORS else "FAIL", reason=code)
        return result
    data, meta = payload.get("data"), payload.get("meta")
    if mcp_error or not isinstance(data, dict) or not isinstance(meta, dict):
        return result
    freshness, quality = meta.get("freshness"), meta.get("data_quality")
    if not isinstance(freshness, dict) or not isinstance(quality, dict) or not isinstance(meta.get("disclaimer"), str) or not meta["disclaimer"].strip():
        result["reason"] = "MISSING_RESPONSE_METADATA"
        return result
    if quality.get("schema") != "data_quality_v1" or freshness.get("status") not in ("realtime", "dated", "unknown"):
        result["reason"] = "INVALID_RESPONSE_METADATA"
        return result
    list_fields = {"items", "recent_trading_days", "index_ranking", "themes"}
    for key in REQUIRED[tool]:
        if key in list_fields and not isinstance(data.get(key), list):
            result["reason"] = "INVALID_DATA_SHAPE"
            return result
    if tool == "stock_snapshot" and any(not isinstance(item, dict) for item in data["items"]):
        result["reason"] = "INVALID_DATA_SHAPE"
        return result
    flags = quality.get("flags")
    if not isinstance(flags, list) or any(not isinstance(flag, str) or flag not in QUALITY_FLAGS for flag in flags):
        result["reason"] = "INVALID_QUALITY_FLAGS"
        return result
    sources: set[str] = set()
    nested_errors: set[str] = set()
    partial_failure = False
    for value in _walk(data):
        if isinstance(value, float) and not math.isfinite(value):
            result["reason"] = "NON_FINITE_DATA"
            return result
        if isinstance(value, dict):
            partial_failure |= bool(value.get("partial_failure") or value.get("errors"))
            if value.get("error_code"):
                nested_errors.add(_error_code(value["error_code"]))
            for key in ("source", "provider", "provider_used", "final_provider"):
                source = value.get(key)
                if isinstance(source, str) and source.lower() in PROVIDERS:
                    sources.add(source.lower())
    for key in ("provider_used", "final_provider"):
        if isinstance(meta.get(key), str) and meta[key].lower() in PROVIDERS:
            sources.add(meta[key].lower())
    status = freshness.get("status")
    result.update(
        status="PASS", reason="COMPLETE_SAMPLE", sources=sorted(sources) or ["unknown"],
        observed_at=_time_text(freshness.get("observed_at")),
        as_of=_time_text(freshness.get("as_of")),
        freshness=status if status in {"realtime", "dated", "unknown"} else "unknown",
        quality_flags=sorted(set(flags)), error_codes=sorted(nested_errors),
        record_counts={key: len(data[key]) for key in REQUIRED[tool] if isinstance(data.get(key), list)},
    )
    if tool == "trading_calendar":
        session = data.get("session_context")
        session = session if isinstance(session, dict) else {}
        result["session_status"] = session.get("session_status") if session.get("session_status") in SESSIONS else "unknown"
    missing = [key for key in REQUIRED[tool] if not data.get(key)]
    if tool == "stock_snapshot" and not missing:
        for item in data["items"]:
            if not isinstance(item, dict) or not item.get("quote") or not isinstance(item.get("history"), dict) or not item["history"].get("items"):
                missing.append("requested_snapshot_sections")
                break
    if {"anomalous_values", "semantic_anomalies"} & set(flags) or freshness.get("warnings"):
        result.update(status="FAIL", reason="DATA_ANOMALY")
    elif missing or partial_failure or {"partial_failure", "stale_cache", "empty_result", "empty_records", "missing_fields", "aged_data"} & set(flags):
        result.update(status="PARTIAL", reason="INCOMPLETE_OR_AGED_DATA")
    elif not result["observed_at"] or not sources or (tool != "stock_search" and not result["as_of"]):
        result.update(status="PARTIAL", reason="UNVERIFIED_SOURCE_OR_TIME")
    return result


def new_report(version: str, timeout: int, quota: int) -> dict[str, Any]:
    return {
        "schema": "retail_acceptance_v1", "status": "BLOCKED", "mode": "plan_only",
        "expected_version": version, "started_at": _now(),
        "platform": platform.system(), "python": platform.python_version(),
        "host_acceptance": "NOT_RUN", "profile": "retail_v1_preview",
        "limits": {"max_tool_calls": 10, "call_timeout_seconds": timeout, "zhitu_process_quota_per_token": quota, "upstream_request_count": "not_measured"},
        "checks": [], "remaining_tools": list(TOOLS),
    }


async def run_cases(session: Any, report: dict[str, Any], save=lambda: None) -> None:
    import anyio

    context: dict[str, str] = {}
    for tool in TOOLS:
        started = time.monotonic()
        try:
            with anyio.fail_after(report["limits"]["call_timeout_seconds"]):
                response = await session.call_tool(tool, request_for(tool, context))
            payload = getattr(response, "structured_content", None)
            if payload is None:
                content = "\n".join(getattr(item, "text", "") for item in response.content)
                payload = json.loads(content)
            entry = assess(tool, payload, elapsed_ms=round((time.monotonic() - started) * 1000), mcp_error=bool(response.is_error))
            if entry["status"] == "PASS" and context.get("trade_date") and tool != "stock_search":
                as_of_date = _date_text((entry.get("as_of") or "")[:10])
                if as_of_date and as_of_date < context["trade_date"]:
                    entry.update(status="PARTIAL", reason="SOURCE_PRECEDES_SELECTED_TRADE_DATE")
            if entry["status"] == "PASS" and tool == "trading_calendar":
                recent = payload["data"]["recent_trading_days"]
                dates = [_date_text(value) for value in recent]
                if not dates or any(value is None for value in dates) or dates != sorted(set(dates)) or dates[-1] > date.today().isoformat():
                    entry.update(status="FAIL", reason="INVALID_CALENDAR_DATES")
                else:
                    context["trade_date"] = dates[-1]
                    report["trade_date"] = dates[-1]
            if entry["status"] == "PASS" and tool == "hot_theme_tracker":
                names = [item.get("sector_name") for item in payload["data"]["themes"] if isinstance(item, dict)]
                names = [name for name in names if isinstance(name, str) and re.fullmatch(r"[\w\u3400-\u9fff ()（）-]{1,64}", name)]
                if len(set(names)) < 2:
                    entry.update(status="PARTIAL", reason="INSUFFICIENT_THEME_CONTEXT")
                else:
                    context["sector_name"] = names[0]
        except TimeoutError:
            entry = {"tool": tool, "status": "BLOCKED", "reason": "MCP_CALL_TIMEOUT", "latency_ms": round((time.monotonic() - started) * 1000)}
        except Exception:
            # Provider / SDK exceptions may include credential-bearing URLs.
            entry = {"tool": tool, "status": "FAIL", "reason": "INVALID_MCP_RESPONSE", "latency_ms": round((time.monotonic() - started) * 1000)}
        report["checks"].append(entry)
        report["remaining_tools"].remove(tool)
        report["status"] = entry["status"] if entry["status"] != "PASS" else "BLOCKED"
        save()
        if entry["status"] != "PASS":
            return
    report["status"] = "PASS"


async def run_live(command: str, config: Path, report: dict[str, Any], save, scratch: Path) -> None:
    import anyio
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    report["mode"] = "mcp_stdio_live"
    # An empty cwd prevents implicit .env loading; the SDK only inherits its
    # OS allowlist, so legacy Token / proxy / PYTHONPATH variables do not leak in.
    env = {
        "CN_STOCK_MCP_CONFIG": str(config), "TOOL_PROFILE": "retail_v1_preview",
        "ZHITU_DAILY_QUOTA_PER_TOKEN": str(report["limits"]["zhitu_process_quota_per_token"]),
        "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
    }
    previous_logging = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        with tempfile.TemporaryDirectory(prefix="retail-acceptance-", dir=scratch) as cwd, open(os.devnull, "w") as sink:
            params = StdioServerParameters(command=command, args=["--stdio"], env=env, cwd=cwd)
            async with stdio_client(params, errlog=sink) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    with anyio.fail_after(30):
                        initialized = await session.initialize()
                        listed = await session.list_tools()
                    actual = [tool.name for tool in listed.tools]
                    if initialized.server_info.version != report["expected_version"] or len(actual) != len(TOOLS) or set(actual) != set(TOOLS):
                        report["checks"].append({"tool": "initialize", "status": "FAIL", "reason": "VERSION_OR_TOOL_SET_MISMATCH"})
                        report["status"] = "FAIL"
                    else:
                        report["checks"].append({"tool": "initialize", "status": "PASS", "reason": "VERSION_AND_RETAIL_TOOLS_MATCH"})
                        await run_cases(session, report, save)
    except Exception:
        report["checks"].append({"tool": "transport", "status": "BLOCKED", "reason": "STDIO_CONNECTION_FAILED"})
        if report["status"] not in {"FAIL", "PARTIAL"}:
            report["status"] = "BLOCKED"
    finally:
        logging.disable(previous_logging)
        report["finished_at"] = _now()
        save()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path, help="Path only; only the server reads it after --run-live")
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--timeout", type=int, default=60, choices=range(10, 121), metavar="10..120")
    parser.add_argument("--zhitu-budget", type=int, default=60, choices=range(1, 101), metavar="1..100")
    parser.add_argument("--run-live", action="store_true", help="Start the server and consume provider requests after user authorization")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.expected_version):
        parser.error("--expected-version must be a stable version number")
    if not args.command.is_absolute() or not args.config.is_absolute():
        parser.error("--command and --config must be absolute paths")
    report = new_report(args.expected_version, args.timeout, args.zhitu_budget)
    if not args.run_live:
        report["plan"] = [{"tool": tool, "arguments": request_for(tool, {"trade_date": "<calendar result>", "sector_name": "<theme result>"})} for tool in TOOLS]
        print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    if args.report is None or not args.report.is_absolute() or not args.report.parent.is_dir():
        parser.error("--run-live requires an absolute --report path with an existing parent directory")
    # Exclusive creation avoids accidentally overwriting previous evidence or
    # a config/credential file supplied as the report destination.
    try:
        handle = args.report.open("x", encoding="utf-8")
    except OSError:
        parser.error("report must be a new writable file")
    with handle:
        def save():
            handle.seek(0)
            json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.truncate()
            handle.flush()

        if not args.config.is_file() or not args.command.is_file():
            report["checks"].append({"tool": "preflight", "status": "BLOCKED", "reason": "EXECUTABLE_OR_CONFIG_MISSING"})
            save()
        else:
            import anyio
            anyio.run(partial(run_live, str(args.command), args.config, report, save, args.report.parent))
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return {"PASS": 0, "PARTIAL": 2, "FAIL": 1, "BLOCKED": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())

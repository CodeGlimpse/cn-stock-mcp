from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from cn_stock_mcp.app.services.provider_router import ProviderRouter


_COMMON_ERRORS = [
    {"error_code": "INVALID_ARGUMENT", "when": "请求参数未通过 schema 校验或缺少必要字段"},
    {"error_code": "PROVIDER_TIMEOUT", "when": "上游请求超时，可短次数重试"},
    {"error_code": "PROVIDER_UNAVAILABLE", "when": "上游接口、依赖或网络暂时不可用"},
    {"error_code": "PROVIDER_AUTH_FAILED", "when": "provider token 缺失或鉴权失败"},
    {"error_code": "UNSUPPORTED_MARKET", "when": "当前 provider 不支持指定市场/代码路由"},
]

_FRESHNESS = {
    "observed_at": "服务端完成获取/组装响应的 UTC 时间",
    "as_of": "源数据可识别的最新时间或日期；未知时为 null",
    "basis": "provider_timestamp、source_date 或 unknown",
    "status": "realtime、dated 或 unknown；realtime 不等同于正在交易",
    "age_seconds": "observed_at 与 as_of 的非负秒差；未知时为 null",
}

_EXAMPLE_OVERRIDES: dict[str, dict[str, Any]] = {
    "stock_search": {"query": "贵州茅台"},
    "stock_quote": {"symbols": ["600519.SH"]},
    "stock_snapshot": {"symbols": ["600519.SH"]},
    "stock_history": {"symbol": "600519.SH", "interval": "1d"},
    "stock_review": {"symbol": "600519.SH"},
    "stock_profile": {"symbol": "600519.SH"},
    "stock_financial": {"symbol": "600519.SH"},
    "technical_indicator": {"symbol": "600519.SH", "interval": "1d", "indicator": "ma"},
    "multi_timeframe_review": {"symbol": "600519.SH", "intervals": ["1d", "1w"]},
    "event_calendar": {"symbols": ["600519.SH"]},
    "capital_flow": {"flow_type": "market", "limit": 20},
    "sector_lookup": {"mode": "list", "sector_type": "primary", "limit": 5},
    "sector_review": {"sector_name": "银行", "sector_type": "primary", "limit": 5},
    "sector_rotation_review": {"sector_names": ["银行", "证券"], "sector_type": "primary"},
    "market_pool": {"pool_type": "limit_up", "limit": 5},
    "trading_calendar": {},
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_safe(child) for child in value]
    if isinstance(value, tuple):
        return [_json_safe(child) for child in value]
    return value


def _hint_value(name: str, field) -> Any:
    if name in {"symbols", "sector_names"}:
        return ["600519.SH"] if name == "symbols" else ["银行", "证券"]
    if name in {"symbol", "benchmark_symbol"}:
        return "600519.SH"
    if name in {"query", "sector_name"}:
        return "贵州茅台" if name == "query" else "银行"
    if name in {"interval", "history_interval"}:
        return "1d"
    if name == "intervals":
        return ["1d", "1w"]
    if name == "indicator":
        return "ma"
    if name == "market":
        return "CN"
    if name == "sec_type":
        return "stock"
    if name == "provider":
        return "akshare"
    if name == "flow_type":
        return "market"
    if name == "pool_type":
        return "limit_up"
    if name == "mode":
        return "list"
    if name == "sector_type":
        return "primary"
    if name == "brief_type":
        return "close"
    if name == "include":
        return ["quote"]
    annotation = str(field.annotation)
    if "bool" in annotation:
        return False
    if "int" in annotation or "float" in annotation:
        return 1
    return "example"


def build_minimal_example(model: type[BaseModel], tool_name: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for name, field in model.model_fields.items():
        if field.default is not PydanticUndefined:
            if field.default is not None:
                payload[name] = _json_safe(field.default)
            continue
        if field.default_factory is not None:
            payload[name] = _json_safe(field.default_factory())
            continue
        payload[name] = _hint_value(name, field)
    if tool_name and tool_name in _EXAMPLE_OVERRIDES:
        payload.update(_EXAMPLE_OVERRIDES[tool_name])
    return _json_safe(payload)


def build_tool_catalog(server) -> list[dict[str, Any]]:
    catalog = []
    for name, tool in sorted(server.tools.items()):
        catalog.append(
            {
                "name": name,
                "description": tool.description,
                "input_model": tool.input_model.__name__,
                "input_schema": tool.input_model.model_json_schema(),
                "minimal_example": build_minimal_example(tool.input_model, name),
                "provider_support": ProviderRouter.describe_route(name),
                "common_errors": _COMMON_ERRORS,
                "freshness": _FRESHNESS,
            }
        )
    return catalog


def find_tool(catalog: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((item for item in catalog if item["name"] == name), None)


def render_tool_catalog_markdown(catalog: list[dict[str, Any]]) -> str:
    lines = [
        "# Tool Catalog (`cn-stock-mcp`)",
        "",
        "> 本文件由当前 MCP registry 和 Pydantic schema 生成。请使用 `cn-stock-mcp --list-tools --json` 获取机器可读目录，或使用 `cn-stock-mcp --describe-tool <name>` 查询单个工具。",
        "",
        f"工具总数：**{len(catalog)}**",
        "",
        "## 工具索引",
        "",
        "| Tool | Provider route | Description |",
        "|---|---|---|",
    ]
    for item in catalog:
        route = item["provider_support"]
        route_text = ", ".join([str(route["primary"]), *[str(value) for value in route["fallback"]]])
        description = item["description"].replace("|", "\\|")
        lines.append(f"| `{item['name']}` | `{route_text}` | {description} |")

    lines.extend(
        [
            "",
            "## 统一说明",
            "",
            "成功响应的顶层 `meta` 包含 freshness 和 `data_quality_v1`。freshness 的 `status=realtime` 只表示源数据带有时间级字段，不代表交易所当前处于交易时段。",
            "",
            "常见错误：`INVALID_ARGUMENT`、`PROVIDER_TIMEOUT`、`PROVIDER_UNAVAILABLE`、`PROVIDER_AUTH_FAILED`、`UNSUPPORTED_MARKET`。",
            "",
            "## 工具详情",
            "",
        ]
    )
    for item in catalog:
        lines.extend(
            [
                f"### `{item['name']}`",
                "",
                item["description"],
                "",
                f"Provider route: `{item['provider_support']['primary']}`; fallback: `{', '.join(item['provider_support']['fallback']) or 'none'}`",
                "",
                "最小示例：",
                "",
                "```json",
                json.dumps(item["minimal_example"], ensure_ascii=False, indent=2),
                "```",
                "",
                "Input schema：",
                "",
                "```json",
                json.dumps(item["input_schema"], ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def write_tool_catalog(path, server) -> None:
    catalog = build_tool_catalog(server)
    path.write_text(render_tool_catalog_markdown(catalog), encoding="utf-8")


if __name__ == "__main__":
    from pathlib import Path

    from cn_stock_mcp.server.mcp_server import create_server

    output = Path(__file__).resolve().parents[4] / "docs" / "TOOL_CATALOG.md"
    write_tool_catalog(output, create_server())
    print(output)

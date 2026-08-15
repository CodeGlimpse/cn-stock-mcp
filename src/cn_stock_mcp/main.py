from __future__ import annotations

import argparse
import json

from cn_stock_mcp.app.services.doctor import collect_doctor_report, render_doctor_json, render_doctor_report
from cn_stock_mcp.infra.config import get_settings
from cn_stock_mcp.infra.logging import setup_logging
from cn_stock_mcp.server.transport import TransportApp


def _doctor(include_network: bool = False, json_output: bool = False) -> int:
    settings = get_settings()
    app = TransportApp()
    report = collect_doctor_report(settings=settings, app=app, include_network=include_network)
    print(render_doctor_json(report) if json_output else render_doctor_report(report))
    return report.exit_code


def main(argv: list[str] | None = None) -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    parser = argparse.ArgumentParser(description="cn-stock-mcp")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--doctor", action="store_true", help="Run local self-check and exit")
    parser.add_argument("--doctor-network", action="store_true", help="Run local self-check plus upstream network/provider verification")
    parser.add_argument("--json", action="store_true", help="Render doctor output as JSON")
    parser.add_argument("--list-tools", action="store_true", help="List registered tools")
    parser.add_argument("--tool", type=str, help="Tool name to invoke")
    parser.add_argument("--payload", type=str, help="Inline JSON payload for tool invocation")
    parser.add_argument("--stdio", action="store_true", help="Run MCP stdio transport")
    args = parser.parse_args(argv)

    if args.version:
        print(settings.mcp_server_version)
        return

    if args.doctor_network:
        if args.json:
            raise SystemExit(_doctor(include_network=True, json_output=True))
        raise SystemExit(_doctor(include_network=True))

    if args.doctor:
        if args.json:
            raise SystemExit(_doctor(include_network=False, json_output=True))
        raise SystemExit(_doctor(include_network=False))

    app = TransportApp()

    if args.stdio:
        app.run_stdio()
        return

    if args.list_tools:
        print(json.dumps(app.list_tools(), ensure_ascii=False, indent=2))
        return

    if args.tool:
        payload = json.loads(args.payload or "{}")
        app.run_stdio_once(args.tool, payload)
        return

    print("cn-stock-mcp ready")


if __name__ == "__main__":
    main()

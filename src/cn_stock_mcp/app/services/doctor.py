from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cn_stock_mcp.infra.config import Settings
from cn_stock_mcp.server.transport import TransportApp


@dataclass
class DoctorCheck:
    status: str
    name: str
    detail: str


@dataclass
class DoctorReport:
    title: str
    version: str
    checks: list[DoctorCheck]

    @property
    def has_fail(self) -> bool:
        return any(check.status == "FAIL" for check in self.checks)

    @property
    def has_warn(self) -> bool:
        return any(check.status == "WARN" for check in self.checks)

    @property
    def exit_code(self) -> int:
        return 1 if self.has_fail else 0

    @property
    def result_label(self) -> str:
        if self.has_fail:
            return "FAIL"
        if self.has_warn:
            return "WARN"
        return "OK"

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "version": self.version,
            "result": self.result_label,
            "exit_code": self.exit_code,
            "checks": [
                {"status": check.status, "name": check.name, "detail": check.detail}
                for check in self.checks
            ],
        }


def collect_doctor_report(settings: Settings, app: TransportApp, include_network: bool = False) -> DoctorReport:
    checks: list[DoctorCheck] = []

    checks.append(DoctorCheck("OK", "python", sys.executable))
    checks.append(DoctorCheck("OK", "package", f"{settings.mcp_server_name} {settings.mcp_server_version}"))

    cn_cmd = shutil.which("cn-stock-mcp")
    checks.append(
        DoctorCheck(
            "OK" if cn_cmd else "WARN",
            "command",
            cn_cmd or "cn-stock-mcp command not found in PATH (this is normal in some local source/dev environments; installed package users should see OK)",
        )
    )

    env_file = Path.cwd() / ".env"
    checks.append(
        DoctorCheck(
            "OK" if env_file.exists() else "WARN",
            "env_file",
            str(env_file) if env_file.exists() else ".env not found in current directory",
        )
    )

    token_count = len(settings.resolve_zhitu_tokens())
    token_status_fn = getattr(settings, "zhitu_token_config_status", None)
    if callable(token_status_fn):
        token_status = token_status_fn()
        if token_status.get("status") not in {"missing", "ok"}:
            checks.append(
                DoctorCheck(
                    "WARN",
                    "zhitu_token_config",
                    f"{token_status.get('path')}: {token_status.get('message')}",
                )
            )
    checks.append(
        DoctorCheck(
            "OK" if token_count > 0 else "WARN",
            "zhitu_token",
            f"resolved tokens: {token_count}" if token_count > 0 else "no ZHITU token found in current shell/env",
        )
    )

    tools = app.list_tools()
    checks.append(DoctorCheck("OK" if len(tools) > 0 else "FAIL", "tool_registry", f"registered tools: {len(tools)}"))

    if include_network:
        if token_count == 0:
            checks.append(DoctorCheck("FAIL", "provider_health", "network check requested but no ZHITU token found"))
        else:
            provider_health = app.call_tool("provider_health", {})
            provider_ok = bool(provider_health.get("success")) and provider_health.get("error") is None
            if provider_ok:
                checks.append(DoctorCheck("OK", "provider_health", "provider_health ok"))
            else:
                err = provider_health.get("error") or {}
                checks.append(DoctorCheck("FAIL", "provider_health", err.get("message", "provider_health failed")))
    else:
        checks.append(DoctorCheck("WARN", "provider_health", "network check skipped; run --doctor-network to verify upstream access"))

    title = f"{settings.mcp_server_name} doctor"
    if include_network:
        title += " (network)"

    return DoctorReport(title=title, version=settings.mcp_server_version, checks=checks)


def render_doctor_report(report: DoctorReport) -> str:
    lines: list[str] = [report.title, f"version: {report.version}", ""]
    for check in report.checks:
        lines.append(f"[{check.status}] {check.name}: {check.detail}")
    lines.append("")
    lines.append(f"Doctor result: {report.result_label}")

    if report.has_fail:
        lines.append("Next steps:")
        lines.append("- If command is missing, reinstall with: pip install cn-stock-mcp  (or: python -m pip install -e . for local dev)")
        lines.append("- If token is missing, set ZHITU_TOKEN in your MCP host config env block")
        lines.append("- If provider_health failed, check network access and upstream token validity")
    elif report.has_warn:
        lines.append("This usually means local installation is usable, but some optional checks were skipped or incomplete.")

    return "\n".join(lines)


def render_doctor_json(report: DoctorReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

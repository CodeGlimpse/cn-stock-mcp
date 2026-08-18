from __future__ import annotations

from cn_stock_mcp.app.services.doctor import collect_doctor_report, render_doctor_report


class _AppOK:
    def list_tools(self):
        return [{"name": "provider_health"}]

    def call_tool(self, name, payload):
        return {"success": True, "error": None}


class _AppFail:
    def list_tools(self):
        return []

    def call_tool(self, name, payload):
        return {"success": False, "error": {"message": "provider down"}}


class _AppRetail:
    def list_tools(self):
        return [{"name": "stock_quote"}]

    def call_tool(self, name, payload):
        return {
            "success": False,
            "error": {
                "error_code": "TOOL_NOT_FOUND",
                "message": "Tool not found: provider_health",
            },
        }


class _Settings:
    mcp_server_name = "cn-stock-mcp"
    mcp_server_version = "0.1.0"

    def __init__(self, tokens=None):
        self._tokens = tokens or []

    def resolve_zhitu_tokens(self):
        return list(self._tokens)

    def zhitu_token_config_status(self):
        return {"path": "config/zhitu_tokens.json", "status": "ok", "message": "token config parsed"}


def test_collect_doctor_report_local_warns_but_does_not_fail_without_token():
    report = collect_doctor_report(settings=_Settings(tokens=[]), app=_AppOK(), include_network=False)
    assert report.has_fail is False
    assert report.has_warn is True
    assert report.exit_code == 0
    text = render_doctor_report(report)
    assert "Doctor result: WARN" in text
    assert "network check skipped" in text


def test_collect_doctor_report_network_fails_without_token():
    report = collect_doctor_report(settings=_Settings(tokens=[]), app=_AppOK(), include_network=True)
    assert report.has_fail is True
    assert report.exit_code == 1
    text = render_doctor_report(report)
    assert "Doctor result: FAIL" in text
    assert "no ZHITU token found" in text or "network check requested but no ZHITU token found" in text


def test_doctor_guidance_uses_user_config_instead_of_host_environment():
    report = collect_doctor_report(settings=_Settings(tokens=[]), app=_AppOK(), include_network=True)

    text = render_doctor_report(report)

    assert "--init-config" in text
    assert "MCP host config env block" not in text


def test_collect_doctor_report_network_ok_with_token_and_provider_ok():
    report = collect_doctor_report(settings=_Settings(tokens=["abc"]), app=_AppOK(), include_network=True)
    assert report.has_fail is False
    text = render_doctor_report(report)
    assert "provider_health ok" in text


def test_collect_doctor_report_uses_full_network_app_for_hidden_provider_health():
    report = collect_doctor_report(
        settings=_Settings(tokens=["abc"]),
        app=_AppRetail(),
        network_app=_AppOK(),
        include_network=True,
    )

    assert report.has_fail is False
    assert "provider_health ok" in render_doctor_report(report)


def test_collect_doctor_report_fails_when_tool_registry_empty():
    report = collect_doctor_report(settings=_Settings(tokens=["abc"]), app=_AppFail(), include_network=False)
    assert report.has_fail is True
    text = render_doctor_report(report)
    assert "registered tools: 0" in text


def test_collect_doctor_report_warns_on_invalid_token_config():
    settings = _Settings(tokens=["abc"])
    settings.zhitu_token_config_status = lambda: {
        "path": "config/zhitu_tokens.json",
        "status": "invalid",
        "message": "token config JSON is invalid at line 1, column 2",
    }

    report = collect_doctor_report(settings=settings, app=_AppOK(), include_network=False)

    assert any(check.name == "zhitu_token_config" and check.status == "WARN" for check in report.checks)
    assert "config/zhitu_tokens.json" in render_doctor_report(report)

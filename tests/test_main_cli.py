from __future__ import annotations

import pytest

from cn_stock_mcp import main as cli


def test_main_version_flag(capsys):
    cli.main(["--version"])
    captured = capsys.readouterr()
    assert captured.out.strip() == __import__("cn_stock_mcp").__version__


def test_main_doctor_flag_dispatches_without_network(monkeypatch):
    called: dict[str, bool] = {}

    def fake_doctor(*, include_network: bool = False) -> int:
        called["include_network"] = include_network
        return 0

    monkeypatch.setattr(cli, "_doctor", fake_doctor)

    with pytest.raises(SystemExit) as exc:
        cli.main(["--doctor"])

    assert exc.value.code == 0
    assert called == {"include_network": False}


def test_main_doctor_network_flag_dispatches_and_propagates_exit_code(monkeypatch):
    called: dict[str, bool] = {}

    def fake_doctor(*, include_network: bool = False) -> int:
        called["include_network"] = include_network
        return 1

    monkeypatch.setattr(cli, "_doctor", fake_doctor)

    with pytest.raises(SystemExit) as exc:
        cli.main(["--doctor-network"])

    assert exc.value.code == 1
    assert called == {"include_network": True}


def test_main_doctor_json_dispatches_json_output(monkeypatch):
    called: dict[str, bool] = {}

    def fake_doctor(*, include_network: bool = False, json_output: bool = False) -> int:
        called["include_network"] = include_network
        called["json_output"] = json_output
        return 0

    monkeypatch.setattr(cli, "_doctor", fake_doctor)

    with pytest.raises(SystemExit) as exc:
        cli.main(["--doctor", "--json"])

    assert exc.value.code == 0
    assert called == {"include_network": False, "json_output": True}


def test_doctor_network_keeps_hidden_provider_health_available(monkeypatch, capsys):
    class _Server:
        def __init__(self, full=False):
            self.tools = {"provider_health": object()} if full else {"stock_quote": object()}

    class _App:
        def __init__(self, profile_override=None):
            self.server = _Server(profile_override == "full")

        def list_tools(self):
            return [{"name": name} for name in self.server.tools]

        def call_tool(self, name, payload):
            assert name == "provider_health"
            return {"success": True, "error": None}

    class _Settings:
        mcp_server_name = "cn-stock-mcp"
        mcp_server_version = "0.2.0"

        def resolve_zhitu_tokens(self):
            return ["configured-but-never-printed"]

        def zhitu_token_config_status(self):
            return {"path": "config.json", "status": "ok", "message": "token config parsed"}

    monkeypatch.setattr(cli, "get_settings", lambda: _Settings())
    monkeypatch.setattr(cli, "TransportApp", _App)

    assert cli._doctor(include_network=True, json_output=True) == 0
    output = capsys.readouterr().out
    assert '"provider_health"' in output


def test_main_list_tools_json_requests_detailed_catalog(monkeypatch, capsys):
    class _App:
        def list_tools(self, detailed=False):
            assert detailed is True
            return [{"name": "stock_snapshot", "input_schema": {}}]

    monkeypatch.setattr(cli, "TransportApp", _App)

    cli.main(["--list-tools", "--json"])

    assert '"stock_snapshot"' in capsys.readouterr().out


def test_main_describe_tool_prints_catalog_entry(monkeypatch, capsys):
    class _App:
        def describe_tool(self, name):
            assert name == "stock_quote"
            return {"name": name, "description": "quote"}

    monkeypatch.setattr(cli, "TransportApp", _App)

    cli.main(["--describe-tool", "stock_quote"])

    assert '"name": "stock_quote"' in capsys.readouterr().out

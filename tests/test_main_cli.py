from __future__ import annotations

import pytest

from cn_stock_mcp import main as cli


def test_main_version_flag(capsys):
    cli.main(["--version"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "0.1.0"


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

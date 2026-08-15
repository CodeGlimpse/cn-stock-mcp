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

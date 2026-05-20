"""Tests for money_rate usecase with mocked provider."""
from unittest.mock import MagicMock, patch

from cn_stock_mcp.app.usecases.money_rate import MoneyRateUseCase
from cn_stock_mcp.server.schemas import MoneyRateRequest


def _make_shibor_rows():
    return [
        {
            "日期": "2026-05-12",
            "O/N-定价": 1.255, "O/N-涨跌幅": 3.4,
            "1W-定价": 1.308, "1W-涨跌幅": -3.2,
            "2W-定价": 1.343, "2W-涨跌幅": -1.2,
            "1M-定价": 1.394, "1M-涨跌幅": -0.1,
            "3M-定价": 1.412, "3M-涨跌幅": -0.2,
            "6M-定价": 1.438, "6M-涨跌幅": -0.3,
            "9M-定价": 1.457, "9M-涨跌幅": 0.0,
            "1Y-定价": 1.469, "1Y-涨跌幅": 0.0,
        },
        {
            "日期": "2026-05-13",
            "O/N-定价": 1.267, "O/N-涨跌幅": 1.2,
            "1W-定价": 1.299, "1W-涨跌幅": -0.9,
            "2W-定价": 1.338, "2W-涨跌幅": -0.5,
            "1M-定价": 1.391, "1M-涨跌幅": -0.3,
            "3M-定价": 1.409, "3M-涨跌幅": -0.3,
            "6M-定价": 1.436, "6M-涨跌幅": -0.2,
            "9M-定价": 1.456, "9M-涨跌幅": -0.1,
            "1Y-定价": 1.468, "1Y-涨跌幅": -0.1,
        },
    ]


def _make_interbank_rows():
    return [
        {"报告日": "2026-05-12", "利率": 1.255, "涨跌": 3.4},
        {"报告日": "2026-05-13", "利率": 1.267, "涨跌": 1.2},
    ]


def _make_repo_rows():
    return [
        {"date": "2026-05-12", "FR001": 1.3, "FR007": 1.36, "FR014": 1.37, "FDR001": 1.26, "FDR007": 1.30, "FDR014": 1.33},
        {"date": "2026-05-13", "FR001": 1.3, "FR007": 1.35, "FR014": 1.36, "FDR001": 1.27, "FDR007": 1.29, "FDR014": 1.31},
    ]


def test_money_rate_shibor():
    uc = MoneyRateUseCase()
    mock_provider = MagicMock()
    mock_provider.get_shibor_all.return_value = _make_shibor_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = MoneyRateRequest(include=["shibor"], shibor_days=10)
        result = uc.execute(req)
    assert result["shibor_count"] == 2
    latest = result["shibor"][-1]
    assert latest["overnight"] == 1.267
    assert latest["week_1"] == 1.299
    assert latest["year_1"] == 1.468


def test_money_rate_interbank():
    uc = MoneyRateUseCase()
    mock_provider = MagicMock()
    mock_provider.get_interbank_rate.return_value = _make_interbank_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = MoneyRateRequest(include=["interbank"], interbank_indicator="隔夜")
        result = uc.execute(req)
    assert result["interbank_count"] == 2
    latest = result["interbank"][-1]
    assert latest["rate"] == 1.267
    assert latest["change"] == 1.2


def test_money_rate_repo_latest():
    uc = MoneyRateUseCase()
    mock_provider = MagicMock()
    mock_provider.get_repo_rate_latest.return_value = _make_repo_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = MoneyRateRequest(include=["repo"], repo_mode="latest")
        result = uc.execute(req)
    assert result["repo_count"] == 2
    latest = result["repo"][-1]
    assert latest["FR007"] == 1.35
    assert latest["FDR007"] == 1.29


def test_money_rate_repo_hist():
    uc = MoneyRateUseCase()
    mock_provider = MagicMock()
    mock_provider.get_repo_rate_hist.return_value = _make_repo_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = MoneyRateRequest(include=["repo"], repo_mode="hist", start_date="2026-05-01", end_date="2026-05-13")
        result = uc.execute(req)
    assert result["repo_count"] == 2
    mock_provider.get_repo_rate_hist.assert_called_once_with(start_date="2026-05-01", end_date="2026-05-13")


def test_money_rate_repo_hist_requires_start_date():
    from pydantic import ValidationError
    try:
        MoneyRateRequest(include=["repo"], repo_mode="hist")
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "start_date" in str(e)


def test_money_rate_summary():
    uc = MoneyRateUseCase()
    mock_provider = MagicMock()
    mock_provider.get_shibor_all.return_value = _make_shibor_rows()
    mock_provider.get_repo_rate_latest.return_value = _make_repo_rows()
    with patch.object(uc.router, "get_provider", return_value=mock_provider):
        req = MoneyRateRequest(include=["shibor", "repo"])
        result = uc.execute(req)
    assert "SHIBOR" in result["summary"]
    assert "FR007" in result["summary"]

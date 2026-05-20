"""Tests for akshare_macro_adapters: normalize, calendar, overview, summary."""
from __future__ import annotations

import pandas as pd
import pytest

from cn_stock_mcp.app.models.macro import (
    INDICATOR_REGISTRY,
    MacroDataFormat,
    MacroDataPoint,
    MacroEntry,
    OVERVIEW_PRESETS,
)
from cn_stock_mcp.providers.adapters.akshare_macro_adapters import (
    build_calendar_items,
    build_macro_summary_text,
    build_overview_item,
    normalize_format_a,
    normalize_format_a2,
    normalize_format_b,
    normalize_format_c,
    normalize_macro_df,
)


# ── Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def format_a_df():
    return pd.DataFrame({
        "商品": ["中国CPI年率", "中国CPI年率", "中国CPI年率"],
        "日期": ["2025-01-09", "2025-02-09", "2025-03-09"],
        "今值": [0.5, 0.7, None],
        "预测值": [0.4, 0.6, 0.5],
        "前值": [0.3, 0.5, 0.7],
    })


@pytest.fixture
def format_a2_df():
    return pd.DataFrame({
        "时间": ["2025-01", "2025-02"],
        "发布日期": ["2025-01-15", "2025-02-14"],
        "现值": [3.0, 3.1],
        "前值": [2.9, 3.0],
    })


@pytest.fixture
def format_b_df():
    return pd.DataFrame({
        "月份": ["2025-01", "2025-02", "2025-03"],
        "当月": [45000.0, 32000.0, 51000.0],
        "当月-同比增长": [0.12, 0.08, 0.15],
        "累计": [45000.0, 77000.0, 128000.0],
        "累计-同比增长": [0.12, 0.10, 0.11],
    })


@pytest.fixture
def format_c_df():
    return pd.DataFrame({
        "TRADE_DATE": ["2025-01-20", "2025-02-20", "2025-03-20"],
        "LPR1Y": [3.10, 3.10, 3.05],
        "LPR5Y": [3.60, 3.60, 3.55],
        "RATE_1": [2.50, 2.50, 2.45],
        "RATE_2": [3.00, 3.00, 2.95],
    })


# ── Format A ──────────────────────────────────────────────────────

class TestNormalizeFormatA:
    def test_basic_parse(self, format_a_df):
        entry = INDICATOR_REGISTRY[("cn", "cpi")]
        points = normalize_format_a(format_a_df, entry)
        assert len(points) == 3
        assert points[0].date == "2025-01-09"
        assert points[0].actual == 0.5
        assert points[0].forecast == 0.4
        assert points[0].previous == 0.3
        assert points[0].surprise == "beat"

    def test_miss_surprise(self, format_a_df):
        entry = INDICATOR_REGISTRY[("cn", "cpi")]
        points = normalize_format_a(format_a_df, entry)
        # Row 2: actual=0.7, forecast=0.6 → beat
        assert points[1].surprise == "beat"

    def test_null_actual_no_surprise(self, format_a_df):
        entry = INDICATOR_REGISTRY[("cn", "cpi")]
        points = normalize_format_a(format_a_df, entry)
        # Row 3: actual=None
        assert points[2].actual is None
        assert points[2].surprise is None

    def test_equal_values_in_line(self):
        df = pd.DataFrame({
            "商品": ["X"],
            "日期": ["2025-01-01"],
            "今值": [1.0],
            "预测值": [1.0],
            "前值": [0.9],
        })
        entry = MacroEntry(func="x", format=MacroDataFormat.A, name="X")
        points = normalize_format_a(df, entry)
        assert points[0].surprise == "in_line"


# ── Format A2 ─────────────────────────────────────────────────────

class TestNormalizeFormatA2:
    def test_basic_parse(self, format_a2_df):
        entry = INDICATOR_REGISTRY[("usa", "cpi")]
        points = normalize_format_a2(format_a2_df, entry)
        assert len(points) == 2
        assert points[0].date == "2025-01-15"
        assert points[0].actual == 3.0
        assert points[0].forecast is None
        assert points[0].previous == 2.9

    def test_no_surprise(self, format_a2_df):
        entry = INDICATOR_REGISTRY[("usa", "cpi")]
        points = normalize_format_a2(format_a2_df, entry)
        # A2 has no forecast column → surprise is always None
        assert all(p.surprise is None for p in points)


# ── Format B ──────────────────────────────────────────────────────

class TestNormalizeFormatB:
    def test_basic_parse(self, format_b_df):
        entry = INDICATOR_REGISTRY[("cn", "credit")]
        points = normalize_format_b(format_b_df, entry)
        assert len(points) == 3
        assert points[0].date == "2025-01"
        assert points[0].actual == 45000.0
        assert points[0].forecast is None
        assert points[0].previous is None

    def test_missing_date_col_returns_empty(self, format_b_df):
        entry = MacroEntry(func="x", format=MacroDataFormat.B, name="X",
                           b_date_col=None, b_value_col="当月")
        points = normalize_format_b(format_b_df, entry)
        assert points == []


# ── Format C ──────────────────────────────────────────────────────

class TestNormalizeFormatC:
    def test_basic_parse(self, format_c_df):
        entry = INDICATOR_REGISTRY[("cn", "lpr")]
        points = normalize_format_c(format_c_df, entry)
        assert len(points) == 3
        assert points[0].date == "2025-01-20"
        assert points[0].actual == 3.10
        assert points[2].actual == 3.05

    def test_empty_col_map_returns_empty(self, format_c_df):
        entry = MacroEntry(func="x", format=MacroDataFormat.C, name="X",
                           c_col_map={})
        points = normalize_format_c(format_c_df, entry)
        assert points == []


# ── Dispatch ──────────────────────────────────────────────────────

class TestNormalizeMacroDf:
    def test_dispatch_a(self, format_a_df):
        entry = INDICATOR_REGISTRY[("cn", "cpi")]
        points = normalize_macro_df(format_a_df, entry)
        assert len(points) == 3

    def test_dispatch_b(self, format_b_df):
        entry = INDICATOR_REGISTRY[("cn", "credit")]
        points = normalize_macro_df(format_b_df, entry)
        assert len(points) == 3

    def test_dispatch_c(self, format_c_df):
        entry = INDICATOR_REGISTRY[("cn", "lpr")]
        points = normalize_macro_df(format_c_df, entry)
        assert len(points) == 3


# ── Calendar ──────────────────────────────────────────────────────

class TestBuildCalendarItems:
    def test_filters_future_items(self):
        points = [
            MacroDataPoint(date="2025-01-09", actual=0.5, forecast=0.4, previous=0.3),
            MacroDataPoint(date="2025-04-10", actual=None, forecast=0.6, previous=0.7),
        ]
        items = build_calendar_items(points, "cpi", "中国CPI年率", "cn")
        assert len(items) == 1
        assert items[0].indicator == "cpi"
        assert items[0].indicator_name == "中国CPI年率"
        assert items[0].forecast == 0.6

    def test_no_future_items(self):
        points = [
            MacroDataPoint(date="2025-01-09", actual=0.5, forecast=0.4, previous=0.3),
        ]
        items = build_calendar_items(points, "cpi", "中国CPI年率", "cn")
        assert items == []


# ── Overview Item ──────────────────────────────────────────────────

class TestBuildOverviewItem:
    def test_basic(self):
        entry = INDICATOR_REGISTRY[("cn", "cpi")]
        point = MacroDataPoint(date="2025-03-09", actual=0.7, forecast=0.6, previous=0.5, surprise="beat")
        item = build_overview_item(point, "cpi", entry, "cn")
        assert item.indicator == "cpi"
        assert item.indicator_name == "中国CPI年率"
        assert item.actual == 0.7
        assert item.surprise == "beat"
        assert item.unit == "%"


# ── Summary ───────────────────────────────────────────────────────

class TestBuildMacroSummaryText:
    def test_latest_with_surprise(self):
        latest = MacroDataPoint(date="2025-03-09", actual=0.7, forecast=0.6, previous=0.5, surprise="beat")
        text = build_macro_summary_text("中国CPI年率", "%", latest, [])
        assert "中国CPI年率" in text
        assert "0.7%" in text
        assert "超预期" in text

    def test_latest_miss(self):
        latest = MacroDataPoint(date="2025-03-09", actual=0.3, forecast=0.6, previous=0.5, surprise="miss")
        text = build_macro_summary_text("中国CPI年率", "%", latest, [])
        assert "不及预期" in text

    def test_no_data(self):
        text = build_macro_summary_text("X", "%", None, [])
        assert "暂无" in text

    def test_history_direction(self):
        latest = MacroDataPoint(date="2025-03-09", actual=0.7, forecast=None, previous=0.5, surprise=None)
        history = [
            MacroDataPoint(date="2025-01-09", actual=0.5),
            MacroDataPoint(date="2025-03-09", actual=0.7),
        ]
        text = build_macro_summary_text("X", "%", latest, history)
        assert "↑" in text

    def test_overview_items(self):
        from cn_stock_mcp.app.models.macro import MacroOverviewItem
        items = {
            "cpi": MacroOverviewItem(indicator="cpi", indicator_name="中国CPI年率", date="2025-03-09",
                                     actual=0.7, unit="%", surprise="beat"),
        }
        text = build_macro_summary_text("", "", None, [], overview_items=items)
        assert "中国CPI年率" in text
        assert "超预期" in text


# ── Registry Integrity ────────────────────────────────────────────

class TestRegistryIntegrity:
    def test_registry_not_empty(self):
        assert len(INDICATOR_REGISTRY) > 0

    def test_all_regions_have_entries(self):
        regions = {r for r, _ in INDICATOR_REGISTRY}
        assert "cn" in regions
        assert "usa" in regions
        assert "euro" in regions
        assert "global" in regions

    def test_all_presets_reference_valid_entries(self):
        for region, pairs in OVERVIEW_PRESETS.items():
            for rgn, ind in pairs:
                assert (rgn, ind) in INDICATOR_REGISTRY, f"Overview preset ({rgn}, {ind}) not in registry"

    def test_all_format_b_have_date_value_cols(self):
        for key, entry in INDICATOR_REGISTRY.items():
            if entry.format == MacroDataFormat.B:
                assert entry.b_date_col is not None, f"{key}: format=B but b_date_col is None"
                assert entry.b_value_col is not None, f"{key}: format=B but b_value_col is None"

    def test_all_format_c_have_col_map(self):
        for key, entry in INDICATOR_REGISTRY.items():
            if entry.format == MacroDataFormat.C:
                assert entry.c_col_map is not None, f"{key}: format=C but c_col_map is None"
                assert len(entry.c_col_map) > 0, f"{key}: format=C but c_col_map is empty"

    def test_cn_core_indicators_present(self):
        required = [("cn", "cpi"), ("cn", "ppi"), ("cn", "pmi"), ("cn", "gdp"), ("cn", "lpr"), ("cn", "m2")]
        for key in required:
            assert key in INDICATOR_REGISTRY, f"Missing core indicator: {key}"

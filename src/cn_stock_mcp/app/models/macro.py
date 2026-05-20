from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MacroDataFormat(str, Enum):
    """Column structure format of AKShare macro API response."""

    A = "A"     # [商品, 日期, 今值, 预测值, 前值]
    A2 = "A2"   # [时间, 发布日期, 现值, 前值]
    B = "B"     # NBS wide-table, per-indicator normalize
    C = "C"     # Special (e.g. LPR)


class MacroEntry(BaseModel):
    """Registry entry mapping (region, indicator) to AKShare function + normalize rules."""

    func: str                    # AKShare function name
    format: MacroDataFormat      # Which normalize strategy to use
    name: str                    # Human-readable Chinese name
    unit: str = ""               # Unit string (e.g. "%", "亿元")
    freq: str = "monthly"        # Data frequency: daily/weekly/monthly/quarterly/yearly/irregular
    # For format=B: which columns to extract
    b_date_col: str | None = None
    b_value_col: str | None = None
    b_extra_cols: list[str] | None = None
    # For format=C: column mapping
    c_col_map: dict[str, str] | None = None


class MacroDataPoint(BaseModel):
    """A single macro data observation."""

    date: str
    actual: float | None = None
    forecast: float | None = None
    previous: float | None = None
    surprise: str | None = None   # "beat" / "miss" / "in_line" / None


class MacroCalendarItem(BaseModel):
    """An upcoming macro event from the calendar view."""

    indicator: str
    indicator_name: str
    date: str
    forecast: float | None = None
    previous: float | None = None
    region: str = "cn"


class MacroOverviewItem(BaseModel):
    """Compact snapshot for one indicator in an overview."""

    indicator: str
    indicator_name: str
    date: str | None = None
    actual: float | None = None
    forecast: float | None = None
    previous: float | None = None
    surprise: str | None = None
    unit: str = ""
    freq: str = "monthly"


class MacroIndicatorResult(BaseModel):
    """Full result for macro_indicator tool."""

    indicator: str
    indicator_name: str
    region: str = "cn"
    unit: str = ""
    frequency: str = "monthly"

    latest: MacroDataPoint | None = None
    history: list[MacroDataPoint] = Field(default_factory=list)
    history_count: int = 0
    calendar: list[MacroCalendarItem] = Field(default_factory=list)
    overview: dict[str, Any] | None = None
    summary: str = ""
    source: str = "akshare"


# ── Indicator Registry ──────────────────────────────────────────────

INDICATOR_REGISTRY: dict[tuple[str, str], MacroEntry] = {
    # ── China ──
    ("cn", "cpi"):        MacroEntry(func="macro_china_cpi_yearly",     format=MacroDataFormat.A,  name="中国CPI年率",            unit="%",    freq="monthly"),
    ("cn", "cpi_m"):      MacroEntry(func="macro_china_cpi_monthly",    format=MacroDataFormat.A,  name="中国CPI月率",            unit="%",    freq="monthly"),
    ("cn", "ppi"):        MacroEntry(func="macro_china_ppi_yearly",     format=MacroDataFormat.A,  name="中国PPI年率",            unit="%",    freq="monthly"),
    ("cn", "pmi"):        MacroEntry(func="macro_china_pmi_yearly",     format=MacroDataFormat.A,  name="官方制造业PMI",          unit="",     freq="monthly"),
    ("cn", "pmi_non"):    MacroEntry(func="macro_china_non_man_pmi",    format=MacroDataFormat.A,  name="官方非制造业PMI",        unit="",     freq="monthly"),
    ("cn", "pmi_cx"):     MacroEntry(func="macro_china_cx_pmi_yearly",  format=MacroDataFormat.A,  name="财新制造业PMI",          unit="",     freq="monthly"),
    ("cn", "pmi_cx_svc"): MacroEntry(func="macro_china_cx_services_pmi_yearly", format=MacroDataFormat.A, name="财新服务业PMI", unit="", freq="monthly"),
    ("cn", "gdp"):        MacroEntry(func="macro_china_gdp_yearly",     format=MacroDataFormat.A,  name="中国GDP年率",            unit="%",    freq="quarterly"),
    ("cn", "lpr"):        MacroEntry(func="macro_china_lpr",            format=MacroDataFormat.C,  name="LPR报价",                unit="%",    freq="monthly",
                                       c_col_map={"LPR1Y": "1年期", "LPR5Y": "5年期"}),
    ("cn", "m2"):         MacroEntry(func="macro_china_m2_yearly",      format=MacroDataFormat.A,  name="M2同比",                unit="%",    freq="monthly"),
    ("cn", "credit"):     MacroEntry(func="macro_china_new_financial_credit", format=MacroDataFormat.B, name="新增信贷",  unit="亿元", freq="monthly",
                                       b_date_col="月份", b_value_col="当月",
                                       b_extra_cols=["当月-同比增长", "累计", "累计-同比增长"]),
    ("cn", "exports"):    MacroEntry(func="macro_china_exports_yoy",    format=MacroDataFormat.A,  name="出口同比",               unit="%",    freq="monthly"),
    ("cn", "imports"):    MacroEntry(func="macro_china_imports_yoy",    format=MacroDataFormat.A,  name="进口同比",               unit="%",    freq="monthly"),
    ("cn", "fx_reserves"):MacroEntry(func="macro_china_fx_reserves_yearly", format=MacroDataFormat.A, name="外汇储备",  unit="亿美元", freq="monthly"),
    ("cn", "rrr"):        MacroEntry(func="macro_china_reserve_requirement_ratio", format=MacroDataFormat.B, name="存准率", unit="%", freq="irregular",
                                       b_date_col="公布时间", b_value_col="大型金融机构-调整后",
                                       b_extra_cols=["中小金融机构-调整后"]),

    # ── USA ──
    ("usa", "cpi"):       MacroEntry(func="macro_usa_cpi_yoy",          format=MacroDataFormat.A2, name="美国CPI年率",            unit="%",    freq="monthly"),
    ("usa", "core_cpi"):  MacroEntry(func="macro_usa_core_cpi_monthly", format=MacroDataFormat.A,  name="美国核心CPI月率",        unit="%",    freq="monthly"),
    ("usa", "non_farm"):  MacroEntry(func="macro_usa_non_farm",         format=MacroDataFormat.A,  name="非农就业",               unit="万人", freq="monthly"),
    ("usa", "pmi"):       MacroEntry(func="macro_usa_ism_pmi",          format=MacroDataFormat.A,  name="ISM制造业PMI",          unit="",     freq="monthly"),
    ("usa", "jobless"):   MacroEntry(func="macro_usa_initial_jobless",  format=MacroDataFormat.A,  name="初请失业金",             unit="万人", freq="weekly"),
    ("usa", "rate"):      MacroEntry(func="macro_bank_usa_interest_rate", format=MacroDataFormat.A, name="美联储利率",             unit="%",    freq="irregular"),
    ("usa", "gdp"):       MacroEntry(func="macro_usa_gdp_monthly",      format=MacroDataFormat.A,  name="美国GDP月率",            unit="%",    freq="monthly"),
    ("usa", "retail"):    MacroEntry(func="macro_usa_retail_sales",      format=MacroDataFormat.A,  name="美国零售销售月率",        unit="%",    freq="monthly"),

    # ── Euro ──
    ("euro", "cpi"):      MacroEntry(func="macro_euro_cpi_yoy",         format=MacroDataFormat.A,  name="欧元区CPI年率",          unit="%",    freq="monthly"),
    ("euro", "pmi"):      MacroEntry(func="macro_euro_manufacturing_pmi", format=MacroDataFormat.A, name="欧元区制造业PMI",       unit="",     freq="monthly"),
    ("euro", "rate"):     MacroEntry(func="macro_bank_euro_interest_rate", format=MacroDataFormat.A, name="欧洲央行利率",         unit="%",    freq="irregular"),

    # ── Global / Commodities ──
    ("global", "bdi"):    MacroEntry(func="macro_shipping_bdi",         format=MacroDataFormat.A,  name="BDI波罗的海指数",       unit="",     freq="daily"),
    ("global", "gold"):   MacroEntry(func="macro_cons_gold",            format=MacroDataFormat.A,  name="黄金",                  unit="$/oz", freq="daily"),
}

# Overview presets: which indicators to include for each region
OVERVIEW_PRESETS: dict[str, list[tuple[str, str]]] = {
    "cn": [
        ("cn", "cpi"), ("cn", "ppi"), ("cn", "pmi"), ("cn", "pmi_non"),
        ("cn", "gdp"), ("cn", "lpr"), ("cn", "m2"), ("cn", "credit"),
        ("cn", "exports"), ("cn", "fx_reserves"),
    ],
    "usa": [
        ("usa", "cpi"), ("usa", "non_farm"), ("usa", "pmi"),
        ("usa", "jobless"), ("usa", "rate"), ("usa", "gdp"),
    ],
    "euro": [
        ("euro", "cpi"), ("euro", "pmi"), ("euro", "rate"),
    ],
}

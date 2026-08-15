from cn_stock_mcp.app.services.data_quality import build_data_quality


def test_data_quality_reports_fallback_partial_failure_and_stale_flags():
    quality = build_data_quality(
        {
            "items": [],
            "count": 0,
            "partial_failure": True,
            "meta": {
                "used_fallback": True,
                "stale": True,
                "missing_fields": ["items.0.price"],
            },
        },
        {"status": "realtime", "age_seconds": 3600},
    )

    assert quality["schema"] == "data_quality_v1"
    assert quality["label"] == "low"
    assert quality["score"] < 60
    assert set(quality["flags"]) >= {
        "provider_fallback",
        "partial_failure",
        "stale_cache",
        "empty_result",
        "missing_fields",
        "aged_data",
    }


def test_data_quality_detects_anomalous_values_and_unknown_freshness():
    quality = build_data_quality(
        {"value": float("nan"), "meta": {}},
        {"status": "unknown", "age_seconds": None},
    )

    assert quality["factors"]["anomaly_count"] == 1
    assert "anomalous_values" in quality["flags"]
    assert "freshness_unknown" in quality["flags"]


def test_data_quality_detects_per_symbol_fallback_and_errors():
    quality = build_data_quality(
        {
            "items": [{"symbol": "600519.SH"}],
            "errors": [{"symbol": "000858.SZ", "error_code": "PROVIDER_TIMEOUT"}],
            "meta": {
                "per_symbol": {
                    "600519.SH": {"used_fallback": True},
                },
            },
        },
        {"status": "realtime", "age_seconds": 2},
    )

    assert "provider_fallback" in quality["flags"]
    assert "partial_failure" in quality["flags"]

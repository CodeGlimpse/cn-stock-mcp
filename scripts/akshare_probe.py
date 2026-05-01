from __future__ import annotations

import json
import os
import traceback

import requests

try:
    import akshare as ak
except Exception as exc:  # pragma: no cover
    ak = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def main() -> None:
    print("=== AKShare probe ===")
    print(json.dumps({
        "env_proxies": {k: v for k, v in os.environ.items() if "proxy" in k.lower()}
    }, ensure_ascii=False, indent=2))

    if ak is None:
        print(json.dumps({
            "error": f"akshare import failed: {IMPORT_ERROR}"
        }, ensure_ascii=False, indent=2))
        return

    cases = [
        (
            "stock_zh_a_hist_default",
            lambda: ak.stock_zh_a_hist(symbol="600519", period="daily", start_date="", end_date="", adjust=""),
        ),
        (
            "stock_zh_a_hist_daterange",
            lambda: ak.stock_zh_a_hist(symbol="600519", period="daily", start_date="20260401", end_date="20260430", adjust=""),
        ),
    ]

    for name, fn in cases:
        print(f"\n=== CASE: {name} ===")
        try:
            df = fn()
            print(json.dumps({
                "rows": len(df),
                "columns": list(df.columns),
                "sample": df.head(2).to_dict(orient="records"),
            }, ensure_ascii=False, indent=2))
        except Exception as exc:
            print(json.dumps({
                "error": str(exc),
                "type": type(exc).__name__,
            }, ensure_ascii=False, indent=2))
            traceback.print_exc()

    print("\n=== CASE: raw_eastmoney_request ===")
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",
        "fqt": "0",
        "secid": "1.600519",
        "beg": "20260401",
        "end": "20260430",
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        print(json.dumps({
            "status_code": response.status_code,
            "text_prefix": response.text[:500],
        }, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({
            "error": str(exc),
            "type": type(exc).__name__,
        }, ensure_ascii=False, indent=2))
        traceback.print_exc()


if __name__ == "__main__":
    main()

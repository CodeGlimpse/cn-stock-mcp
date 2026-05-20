from cn_stock_mcp.providers.adapters.akshare_adapters import (
    adapt_akshare_fund_list_row,
    adapt_akshare_index_list_row,
)


def test_adapt_akshare_index_list_row_supports_index_stock_info_fields():
    item = adapt_akshare_index_list_row(
        {
            "index_code": "399006",
            "display_name": "创业板指",
        }
    )

    assert item.symbol == "399006.SZ"
    assert item.name == "创业板指"
    assert item.sec_type == "index"
    assert item.exchange == "SZ"


def test_adapt_akshare_fund_list_row_guesses_exchange_for_etf_code():
    item = adapt_akshare_fund_list_row(
        {
            "基金代码": "159001",
            "基金简称": "货币ETF易方达",
        }
    )

    assert item.symbol == "159001.SZ"
    assert item.exchange == "SZ"
    assert item.sec_type == "fund"

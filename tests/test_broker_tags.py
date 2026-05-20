from cn_stock_mcp.providers.adapters.broker_tags import broker_tags, summarize_broker_tags


def test_broker_tags_institution_and_connect():
    assert broker_tags("机构专用") == ["机构专用"]
    assert broker_tags("深股通专用") == ["陆股通"]


def test_broker_tags_hot_money_and_branch():
    tags = broker_tags("国信证券股份有限公司佛山南海大沥证券营业部")
    assert "营业部" in tags
    assert "知名游资" in tags

    branch_tags = broker_tags("华源证券股份有限公司湖北分公司")
    assert "分公司" in branch_tags


def test_broker_tags_summary():
    summary = summarize_broker_tags([
        {"broker_tags": ["营业部", "知名游资"]},
        {"broker_tags": ["陆股通"]},
        type("Item", (), {"broker_tags": ["营业部"]})(),
    ])
    assert summary == {"营业部": 2, "知名游资": 1, "陆股通": 1}

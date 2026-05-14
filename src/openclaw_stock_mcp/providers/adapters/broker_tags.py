from __future__ import annotations

from collections import Counter

KNOWN_HOT_MONEY_PATTERNS: tuple[tuple[str, str], ...] = (
    ("东方路", "知名游资"),
    ("章盟主", "知名游资"),
    ("上海溧阳路", "知名游资"),
    ("深圳深南东路", "知名游资"),
    ("佛山", "知名游资"),
    ("桑田路", "知名游资"),
    ("劳动路", "知名游资"),
    ("牡丹江路", "知名游资"),
    ("北京中关村", "知名游资"),
    ("杭州上塘路", "知名游资"),
    ("上海宛平南路", "知名游资"),
    ("宁波和源路", "知名游资"),
    ("厦门湖滨南路", "知名游资"),
)


def broker_tags(name: str | None) -> list[str]:
    if not name:
        return []
    text = str(name).strip()
    tags: list[str] = []

    def add(tag: str) -> None:
        if tag not in tags:
            tags.append(tag)

    if "机构专用" in text or text == "机构":
        add("机构专用")
    if "沪股通专用" in text or "深股通专用" in text or "港股通" in text:
        add("陆股通")
    if "量化" in text or "高频" in text or "算法" in text:
        add("量化席位")
    if "自营" in text:
        add("券商自营")
    if "资产管理" in text or "资管" in text:
        add("资管席位")
    if "基金" in text:
        add("基金席位")
    if "证券营业部" in text:
        add("营业部")
    if "分公司" in text:
        add("分公司")
    if "总部" in text:
        add("总部席位")
    if "专用" in text and not any(t in tags for t in ("机构专用", "陆股通")):
        add("专用席位")

    for pattern, tag in KNOWN_HOT_MONEY_PATTERNS:
        if pattern in text:
            add(tag)
            break

    if not tags:
        add("普通席位")
    return tags


def summarize_broker_tags(items: list) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in items:
        tags = item.get("broker_tags", []) if isinstance(item, dict) else getattr(item, "broker_tags", [])
        counter.update(tags)
    return dict(counter)

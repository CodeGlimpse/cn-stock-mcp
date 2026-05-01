def build_quote_summary(name: str | None, price: float | None, change_percent: float | None) -> str:
    display_name = name or "标的"
    price_text = "未知" if price is None else str(price)
    cp_text = "未知" if change_percent is None else f"{change_percent}%"
    return f"{display_name}最新价 {price_text}，涨跌幅 {cp_text}。"

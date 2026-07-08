from datetime import datetime, timedelta

from categories import CATEGORY_EMOJI

_DATE_FORMAT = "%Y-%m-%d %H:%M"


def build_report(rows: list[dict], period: str) -> str:
    now = datetime.now()
    if period == "неделя":
        start = now - timedelta(days=7)
    else:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    income_total = 0.0
    expense_total = 0.0
    by_category: dict[str, float] = {}

    for row in rows:
        try:
            dt = datetime.strptime(str(row["Дата"]), _DATE_FORMAT)
            amount = float(row["Сумма"])
        except (KeyError, ValueError):
            continue

        if dt < start:
            continue

        if row.get("Тип") == "Доход":
            income_total += amount
        else:
            expense_total += amount
            category = row.get("Категория", "прочее")
            by_category[category] = by_category.get(category, 0.0) + amount

    balance = income_total - expense_total
    balance_emoji = "✅" if balance >= 0 else "⚠️"

    lines = [
        f"📅 <b>Отчёт за {period}</b>",
        "",
        f"💰 Доходы: <b>{income_total:.0f}₽</b>",
        f"💸 Расходы: <b>{expense_total:.0f}₽</b>",
        f"{balance_emoji} Остаток: <b>{balance:.0f}₽</b>",
    ]

    if by_category:
        lines.append("")
        lines.append("<b>По категориям:</b>")
        for category, amount in sorted(by_category.items(), key=lambda kv: -kv[1]):
            emoji = CATEGORY_EMOJI.get(category, "📦")
            lines.append(f"{emoji} {category}: {amount:.0f}₽")

    return "\n".join(lines)

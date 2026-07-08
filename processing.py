from datetime import datetime

from categories import CATEGORY_EMOJI
from gemini_parser import parse_with_gemini
from parser import try_strict_parse
from sheets import append_row

TYPE_LABELS = {"income": "Доход", "expense": "Расход"}

NOT_UNDERSTOOD_MESSAGE = (
    "🤔 Не понял сообщение. Формат: <b>500 еда</b> или <b>+50000 зарплата</b>, "
    "либо опиши обычным текстом."
)


def process_entry(text: str, user: dict, source: str) -> str:
    entry = try_strict_parse(text)
    if entry is None:
        entry = parse_with_gemini(text)
    if entry is None:
        return NOT_UNDERSTOOD_MESSAGE

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = [
        now,
        TYPE_LABELS[entry["type"]],
        entry["amount"],
        entry["category"],
        entry.get("description", ""),
        source,
    ]
    append_row(user["credentials_path"], user["spreadsheet_id"], row)

    category = entry["category"]
    emoji = CATEGORY_EMOJI.get(category, "📦")
    sign = "+" if entry["type"] == "income" else "-"
    trend = "📈" if entry["type"] == "income" else "📉"
    return f"{trend} Записал: <b>{sign}{entry['amount']:.0f}₽</b> {emoji} {category}"

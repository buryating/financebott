from __future__ import annotations

import re

from categories import EXPENSE_SYNONYMS, INCOME_SYNONYMS

STRICT_RE = re.compile(r"^([+-]?)\s*(\d+(?:[.,]\d+)?)\s+(\S.*)$")


def try_strict_parse(text: str) -> dict | None:
    match = STRICT_RE.match(text.strip())
    if not match:
        return None

    sign, amount_str, rest = match.groups()
    entry_type = "income" if sign == "+" else "expense"
    synonyms = INCOME_SYNONYMS if entry_type == "income" else EXPENSE_SYNONYMS

    category = _match_category(rest, synonyms)
    if category is None:
        return None

    return {
        "type": entry_type,
        "amount": float(amount_str.replace(",", ".")),
        "category": category,
        "description": rest.strip(),
    }


def _match_category(text: str, synonyms: dict[str, list[str]]) -> str | None:
    text_lower = text.lower()
    for category, words in synonyms.items():
        for word in words:
            if word in text_lower:
                return category
    return None

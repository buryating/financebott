from __future__ import annotations

import json
import logging

from google import genai
from google.genai import types

from categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES
from config import GEMINI_API_KEY, GEMINI_MODEL, PROXY_URL

logger = logging.getLogger(__name__)

_http_options = types.HttpOptions(client_args={"proxy": PROXY_URL}) if PROXY_URL else None
_client = genai.Client(api_key=GEMINI_API_KEY, http_options=_http_options)

_ALL_CATEGORIES = sorted(set(EXPENSE_CATEGORIES) | set(INCOME_CATEGORIES))

_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["income", "expense"]},
        "amount": {"type": "number"},
        "category": {"type": "string", "enum": _ALL_CATEGORIES},
        "description": {"type": "string"},
    },
    "required": ["type", "amount", "category", "description"],
}

_PROMPT = """Извлеки из сообщения о финансовой операции структурированные данные.

type: "income" если это доход (зарплата, подработка, подарок), "expense" если расход.
amount: сумма в рублях, число без знака.
category: ближайшая подходящая категория из разрешённого списка.
description: краткое описание своими словами.

Сообщение: {text}"""


def parse_with_gemini(text: str) -> dict | None:
    try:
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=_PROMPT.format(text=text),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_SCHEMA,
            ),
        )
        data = json.loads(response.text)
    except Exception:
        logger.exception("Gemini parsing failed for text: %r", text)
        return None

    if not all(key in data for key in ("type", "amount", "category")):
        return None

    return data

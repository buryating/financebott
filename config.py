from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL = os.environ["GEMINI_MODEL"]

def _optional_chat_id(env_var: str) -> int | None:
    value = os.getenv(env_var, "")
    return int(value) if value.strip().isdigit() else None


USERS = {
    "diman": {
        "chat_id": _optional_chat_id("DIMAN_CHAT_ID"),
        "spreadsheet_id": os.environ["DIMAN_SPREADSHEET_ID"],
        "shortcut_token": os.environ["DIMAN_SHORTCUT_TOKEN"],
        "credentials_path": os.environ["DIMAN_GOOGLE_CREDENTIALS_PATH"],
    },
    "partner": {
        "chat_id": _optional_chat_id("PARTNER_CHAT_ID"),
        "spreadsheet_id": os.environ["PARTNER_SPREADSHEET_ID"],
        "shortcut_token": os.environ["PARTNER_SHORTCUT_TOKEN"],
        "credentials_path": os.environ["PARTNER_GOOGLE_CREDENTIALS_PATH"],
    },
}

_BY_CHAT_ID = {u["chat_id"]: u for u in USERS.values() if u["chat_id"] is not None}
_BY_TOKEN = {u["shortcut_token"]: u for u in USERS.values()}


def get_user_by_chat_id(chat_id: int) -> dict | None:
    return _BY_CHAT_ID.get(chat_id)


def get_user_by_token(token: str | None) -> dict | None:
    if token is None:
        return None
    return _BY_TOKEN.get(token)

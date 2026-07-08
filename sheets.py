from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_SHEET_NAME = "Операции"
_HEADER = ["Дата", "Тип", "Сумма", "Категория", "Описание", "Источник"]

_clients: dict[str, gspread.Client] = {}


def _get_client(credentials_path: str) -> gspread.Client:
    if credentials_path not in _clients:
        creds = Credentials.from_service_account_file(credentials_path, scopes=_SCOPES)
        _clients[credentials_path] = gspread.authorize(creds)
    return _clients[credentials_path]


def _get_worksheet(credentials_path: str, spreadsheet_id: str) -> gspread.Worksheet:
    spreadsheet = _get_client(credentials_path).open_by_key(spreadsheet_id)
    try:
        return spreadsheet.worksheet(_SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=_SHEET_NAME, rows=1000, cols=len(_HEADER))
        worksheet.append_row(_HEADER)
        worksheet.format(f"A1:{chr(ord('A') + len(_HEADER) - 1)}1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.85, "green": 0.9, "blue": 0.98},
        })
        worksheet.freeze(rows=1)
        return worksheet


def append_row(credentials_path: str, spreadsheet_id: str, row: list) -> None:
    worksheet = _get_worksheet(credentials_path, spreadsheet_id)
    worksheet.append_row(row, value_input_option="USER_ENTERED")


def get_all_rows(credentials_path: str, spreadsheet_id: str) -> list[dict]:
    worksheet = _get_worksheet(credentials_path, spreadsheet_id)
    return worksheet.get_all_records()

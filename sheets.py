from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials

from categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_SHEET_NAME = "Операции"
_SUMMARY_SHEET_NAME = "Сводка"
_HEADER = ["Дата", "Тип", "Сумма", "Категория", "Описание"]
_HEADER_BG = {"red": 0.85, "green": 0.9, "blue": 0.98}

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
            "backgroundColor": _HEADER_BG,
        })
        worksheet.format("C2:C1000", {"numberFormat": {"type": "CURRENCY", "pattern": "#,##0 ₽"}})
        worksheet.freeze(rows=1)
        _ensure_summary_sheet(spreadsheet)
        return worksheet


def _formula_separator(spreadsheet: gspread.Spreadsheet) -> str:
    locale = spreadsheet.fetch_sheet_metadata().get("properties", {}).get("locale", "en_US")
    return "," if locale.startswith("en") else ";"


def _ensure_summary_sheet(spreadsheet: gspread.Spreadsheet) -> None:
    try:
        spreadsheet.worksheet(_SUMMARY_SHEET_NAME)
        return
    except gspread.WorksheetNotFound:
        pass

    sep = _formula_separator(spreadsheet)

    rows: list[list] = [
        ["Баланс", f'=SUMIF(Операции!B:B{sep}"Доход"{sep}Операции!C:C)-SUMIF(Операции!B:B{sep}"Расход"{sep}Операции!C:C)'],
        ["Доходы всего", f'=SUMIF(Операции!B:B{sep}"Доход"{sep}Операции!C:C)'],
        ["Расходы всего", f'=SUMIF(Операции!B:B{sep}"Расход"{sep}Операции!C:C)'],
        [],
        ["Расходы по категориям"],
        ["Категория", "Сумма"],
    ]
    expense_header_row = len(rows)
    for category in EXPENSE_CATEGORIES:
        rows.append([category, f'=SUMIFS(Операции!C:C{sep}Операции!D:D{sep}"{category}"{sep}Операции!B:B{sep}"Расход")'])

    rows.append([])
    rows.append(["Доходы по категориям"])
    income_title_row = len(rows)
    rows.append(["Категория", "Сумма"])
    income_header_row = len(rows)
    for category in INCOME_CATEGORIES:
        rows.append([category, f'=SUMIFS(Операции!C:C{sep}Операции!D:D{sep}"{category}"{sep}Операции!B:B{sep}"Доход")'])

    worksheet = spreadsheet.add_worksheet(title=_SUMMARY_SHEET_NAME, rows=len(rows) + 3, cols=2)
    worksheet.update("A1", rows, value_input_option="USER_ENTERED")

    worksheet.format("A1:B3", {"textFormat": {"bold": True}})
    worksheet.format("A5", {"textFormat": {"bold": True}})
    worksheet.format(f"A{expense_header_row}:B{expense_header_row}", {"textFormat": {"bold": True}, "backgroundColor": _HEADER_BG})
    worksheet.format(f"A{income_title_row}", {"textFormat": {"bold": True}})
    worksheet.format(f"A{income_header_row}:B{income_header_row}", {"textFormat": {"bold": True}, "backgroundColor": _HEADER_BG})
    worksheet.format("B1:B1000", {"numberFormat": {"type": "CURRENCY", "pattern": "#,##0 ₽"}})
    worksheet.freeze(cols=1)


def append_row(credentials_path: str, spreadsheet_id: str, row: list) -> None:
    worksheet = _get_worksheet(credentials_path, spreadsheet_id)
    worksheet.append_row(row, value_input_option="USER_ENTERED")


def get_all_rows(credentials_path: str, spreadsheet_id: str) -> list[dict]:
    worksheet = _get_worksheet(credentials_path, spreadsheet_id)
    return worksheet.get_all_records()

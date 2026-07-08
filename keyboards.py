from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

REPORT_MONTH_BUTTON = "Отчёт за месяц"
REPORT_WEEK_BUTTON = "Отчёт за неделю"


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=REPORT_MONTH_BUTTON), KeyboardButton(text=REPORT_WEEK_BUTTON)],
        ],
        resize_keyboard=True,
    )

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from config import get_user_by_chat_id
from keyboards import REPORT_MONTH_BUTTON, REPORT_WEEK_BUTTON, main_keyboard
from processing import process_entry
from report import build_report
from sheets import get_all_rows

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    user = get_user_by_chat_id(message.chat.id)
    if user is None:
        logger.info("Незарегистрированный chat_id: %s (%s)", message.chat.id, message.chat.username)
        await message.answer(
            "Этот бот настроен для конкретных людей.\n"
            f"Твой chat_id: {message.chat.id} — если ты один из хозяев, впиши его в .env."
        )
        return
    await message.answer(
        "👋 Привет! Пиши траты/доходы текстом, например <b>500 такси</b> или <b>+50000 оффлайн</b>.",
        reply_markup=main_keyboard(),
    )


async def _send_report(message: Message, period: str) -> None:
    user = get_user_by_chat_id(message.chat.id)
    if user is None:
        return

    rows = get_all_rows(user["credentials_path"], user["spreadsheet_id"])
    await message.answer(build_report(rows, period))


@router.message(F.text == REPORT_MONTH_BUTTON)
async def report_month_button(message: Message) -> None:
    await _send_report(message, "месяц")


@router.message(F.text == REPORT_WEEK_BUTTON)
async def report_week_button(message: Message) -> None:
    await _send_report(message, "неделя")


@router.message(Command("report"))
async def cmd_report(message: Message, command: CommandObject) -> None:
    period = (command.args or "месяц").strip().lower()
    if period not in ("месяц", "неделя"):
        period = "месяц"
    await _send_report(message, period)


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user = get_user_by_chat_id(message.chat.id)
    if user is None:
        return

    reply = process_entry(message.text, user)
    await message.answer(reply)

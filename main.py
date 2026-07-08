import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from config import BOT_TOKEN, WEBHOOK_PORT
from handlers import router
from server import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    logger.info("Shortcut webhook listening on port %s", WEBHOOK_PORT)

    while True:
        try:
            await dp.start_polling(bot)
        except Exception:
            logger.exception("Polling crashed (вероятно, обрыв связи с Telegram), retry through 5s")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())

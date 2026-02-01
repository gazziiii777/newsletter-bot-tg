import asyncio

from aiogram import Bot, Dispatcher

from infrastructure.config import settings
from infrastructure.logger import get_logger
from app.database.connection import init_db
from app.handlers.menu import router as menu_router
from app.handlers.start import router as start_router

log = get_logger(__name__)


async def run_bot() -> None:
    init_db()
    log.info("БД инициализирована")
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(menu_router)
    log.info("Бот запущен, polling стартует")
    await dp.start_polling(bot)


def main() -> None:
    try:
        asyncio.run(run_bot())
    except Exception as e:
        log.exception("Ошибка при запуске бота: %s", e)
        raise
    finally:
        log.info("Бот остановлен")


if __name__ == "__main__":
    main()

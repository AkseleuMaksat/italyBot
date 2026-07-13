"""Точка входа: Telegram-бот «Поступление в Италию».

/start → выбор языка → меню → вопрос студента → поиск по базе →
готовый ответ (или похожие варианты) → кнопки для новых действий.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import routers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def set_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Старт / выбор языка"),
            BotCommand(command="menu", description="Главное меню / Main menu"),
            BotCommand(command="admin", description="Админ-панель (для админов)"),
            BotCommand(command="cancel", description="Отмена / Cancel"),
        ]
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*routers)

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущен. Ожидаю сообщения…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")

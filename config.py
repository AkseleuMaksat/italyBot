"""Конфигурация бота: читаем токен и админов из .env."""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

ADMIN_IDS = {
    int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x
}

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не задан. Скопируйте .env.example в .env и вставьте токен от @BotFather."
    )

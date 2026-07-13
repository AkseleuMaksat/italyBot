"""Роутеры бота. Порядок важен: admin раньше общего текстового хэндлера."""
from .common import router as common_router
from .topics import router as topics_router
from .admin import router as admin_router
from .ask import router as ask_router

routers = (common_router, admin_router, topics_router, ask_router)

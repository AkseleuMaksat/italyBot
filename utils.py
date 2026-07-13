"""Общие помощники для хэндлеров."""
from i18n import DEFAULT_LANG, t
from storage import users, kb
from keyboards import after_answer_kb


def lang_of(user_id: int) -> str:
    return users.get_lang(user_id) or DEFAULT_LANG


def format_answer(item: dict, lang: str) -> str:
    """Собирает текст ответа: сам ответ + подпись темы."""
    answer = item["answer"].get(lang) or item["answer"]["ru"]
    topic = kb.topic(item.get("topic", ""))
    parts = [answer]
    if topic:
        title = topic["title"].get(lang, topic["title"]["ru"])
        parts.append("")
        parts.append(f"📁 {t('source_topic', lang, topic=title)}")
    return "\n".join(parts)


async def send_answer(message_or_cb, item: dict, lang: str):
    """Отправляет ответ + кнопки «новый вопрос / в меню». Работает с Message и CallbackQuery."""
    from aiogram.types import CallbackQuery

    text = format_answer(item, lang)
    kbd = after_answer_kb(lang)
    if isinstance(message_or_cb, CallbackQuery):
        await message_or_cb.message.answer(text, reply_markup=kbd, disable_web_page_preview=True)
    else:
        await message_or_cb.answer(text, reply_markup=kbd, disable_web_page_preview=True)

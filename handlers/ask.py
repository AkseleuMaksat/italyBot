"""Свободный вопрос от студента → поиск по базе → ответ/варианты/не найдено.

Ловит любой текст (не команду). Регистрируется последним, поэтому FSM-шаги
админа и другие хэндлеры имеют приоритет.
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from i18n import t
from storage import kb
from search import classify
from keyboards import suggestions_kb, main_menu_kb
from utils import lang_of, send_answer

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def on_question(message: Message, state: FSMContext):
    await state.clear()
    lang = lang_of(message.from_user.id)
    kind, payload = classify(message.text, kb.faq)

    if kind == "answer":
        await send_answer(message, payload, lang)
    elif kind == "suggest":
        await message.answer(t("suggest", lang), reply_markup=suggestions_kb(payload, lang))
    else:
        await message.answer(t("not_found", lang), reply_markup=main_menu_kb(lang))

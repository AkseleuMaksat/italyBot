"""Старт, выбор языка, главное меню, показ ответа по FAQ-кнопке."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from i18n import t
from storage import users, kb
from keyboards import LangCB, MenuCB, FaqCB, language_kb, main_menu_kb, topics_kb
from states import AskFlow
from utils import lang_of, send_answer

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(t("choose_lang", lang_of(message.from_user.id)), reply_markup=language_kb())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    lang = lang_of(message.from_user.id)
    await message.answer(t("menu_title", lang), reply_markup=main_menu_kb(lang))


@router.callback_query(LangCB.filter())
async def on_language(cb: CallbackQuery, callback_data: LangCB, state: FSMContext):
    await state.clear()
    users.set_lang(cb.from_user.id, callback_data.lang)
    lang = callback_data.lang
    await cb.message.edit_text(t("welcome", lang))
    await cb.message.answer(t("menu_title", lang), reply_markup=main_menu_kb(lang))
    await cb.answer()


@router.callback_query(MenuCB.filter(F.action == "home"))
async def on_home(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = lang_of(cb.from_user.id)
    await cb.message.answer(t("menu_title", lang), reply_markup=main_menu_kb(lang))
    await cb.answer()


@router.callback_query(MenuCB.filter(F.action == "lang"))
async def on_change_lang(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer(t("choose_lang", lang_of(cb.from_user.id)), reply_markup=language_kb())
    await cb.answer()


@router.callback_query(MenuCB.filter(F.action == "ask"))
async def on_ask(cb: CallbackQuery, state: FSMContext):
    lang = lang_of(cb.from_user.id)
    await state.set_state(AskFlow.waiting_question)
    await cb.message.answer(t("ask_prompt", lang))
    await cb.answer()


@router.callback_query(MenuCB.filter(F.action == "topics"))
async def on_topics(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = lang_of(cb.from_user.id)
    await cb.message.answer(t("topics_title", lang), reply_markup=topics_kb(lang))
    await cb.answer()


@router.callback_query(FaqCB.filter())
async def on_faq_click(cb: CallbackQuery, callback_data: FaqCB, state: FSMContext):
    await state.clear()
    lang = lang_of(cb.from_user.id)
    item = kb.faq_by_id(callback_data.faq_id)
    if not item:
        await cb.answer(t("not_found", lang), show_alert=True)
        return
    await send_answer(cb, item, lang)
    await cb.answer()

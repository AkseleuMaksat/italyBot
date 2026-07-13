"""Админ-панель: добавление Q&A в базу без остановки бота + статистика."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS
from i18n import t
from storage import kb
from keyboards import AdminCB, admin_menu_kb, admin_topics_kb
from states import AdminAdd
from utils import lang_of

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    lang = lang_of(message.from_user.id)
    if not is_admin(message.from_user.id):
        await message.answer(t("admin_only", lang))
        return
    await state.clear()
    await message.answer(t("admin_menu", lang), reply_markup=admin_menu_kb(lang))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.clear()
        await message.answer(t("admin_cancelled", lang_of(message.from_user.id)))


@router.callback_query(AdminCB.filter(F.action == "cancel"))
async def cb_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer(t("admin_cancelled", lang_of(cb.from_user.id)))
    await cb.answer()


@router.callback_query(AdminCB.filter(F.action == "stats"))
async def cb_stats(cb: CallbackQuery):
    lang = lang_of(cb.from_user.id)
    if not is_admin(cb.from_user.id):
        await cb.answer(t("admin_only", lang), show_alert=True)
        return
    lines = []
    for topic in kb.topics:
        title = topic["title"].get(lang, topic["title"]["ru"])
        lines.append(f"• {title}: {len(kb.faq_by_topic(topic['id']))}")
    await cb.message.answer(
        t("admin_stats", lang, n=len(kb.faq), by_topic="\n".join(lines))
    )
    await cb.answer()


@router.callback_query(AdminCB.filter(F.action == "add"))
async def cb_add(cb: CallbackQuery, state: FSMContext):
    lang = lang_of(cb.from_user.id)
    if not is_admin(cb.from_user.id):
        await cb.answer(t("admin_only", lang), show_alert=True)
        return
    await state.set_state(AdminAdd.topic)
    await cb.message.answer(t("admin_pick_topic", lang), reply_markup=admin_topics_kb(lang))
    await cb.answer()


@router.callback_query(AdminAdd.topic, AdminCB.filter(F.action == "topic"))
async def cb_pick_topic(cb: CallbackQuery, callback_data: AdminCB, state: FSMContext):
    lang = lang_of(cb.from_user.id)
    await state.update_data(topic=callback_data.value)
    await state.set_state(AdminAdd.question_ru)
    await cb.message.answer(t("admin_q_ru", lang))
    await cb.answer()


@router.message(AdminAdd.question_ru, F.text)
async def add_q_ru(message: Message, state: FSMContext):
    await state.update_data(question_ru=message.text.strip())
    await state.set_state(AdminAdd.question_en)
    await message.answer(t("admin_q_en", lang_of(message.from_user.id)))


@router.message(AdminAdd.question_en, F.text)
async def add_q_en(message: Message, state: FSMContext):
    val = message.text.strip()
    await state.update_data(question_en="" if val == "-" else val)
    await state.set_state(AdminAdd.answer_ru)
    await message.answer(t("admin_a_ru", lang_of(message.from_user.id)))


@router.message(AdminAdd.answer_ru, F.text)
async def add_a_ru(message: Message, state: FSMContext):
    await state.update_data(answer_ru=message.text.strip())
    await state.set_state(AdminAdd.answer_en)
    await message.answer(t("admin_a_en", lang_of(message.from_user.id)))


@router.message(AdminAdd.answer_en, F.text)
async def add_a_en(message: Message, state: FSMContext):
    val = message.text.strip()
    await state.update_data(answer_en="" if val == "-" else val)
    await state.set_state(AdminAdd.keywords)
    await message.answer(t("admin_keywords", lang_of(message.from_user.id)))


@router.message(AdminAdd.keywords, F.text)
async def add_keywords(message: Message, state: FSMContext):
    lang = lang_of(message.from_user.id)
    raw = message.text.strip()
    keywords = [] if raw == "-" else [k.strip() for k in raw.split(",") if k.strip()]

    data = await state.get_data()
    topic_id = data["topic"]
    q_ru = data.get("question_ru", "")
    q_en = data.get("question_en") or q_ru
    a_ru = data.get("answer_ru", "")
    a_en = data.get("answer_en") or a_ru

    item = {
        "id": kb.next_id(topic_id),
        "topic": topic_id,
        "question": {"ru": q_ru, "en": q_en},
        "answer": {"ru": a_ru, "en": a_en},
        "keywords": keywords,
    }
    kb.add_faq(item)
    await state.clear()
    await message.answer(t("admin_saved", lang, n=len(kb.faq)), reply_markup=admin_menu_kb(lang))

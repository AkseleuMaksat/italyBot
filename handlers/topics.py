"""Просмотр тем и списка вопросов внутри темы."""
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from i18n import t
from storage import kb
from keyboards import TopicCB, topic_questions_kb
from utils import lang_of

router = Router()


@router.callback_query(TopicCB.filter())
async def on_topic(cb: CallbackQuery, callback_data: TopicCB, state: FSMContext):
    await state.clear()
    lang = lang_of(cb.from_user.id)
    topic = kb.topic(callback_data.topic_id)
    if not topic:
        await cb.answer()
        return
    title = topic["title"].get(lang, topic["title"]["ru"])
    questions = kb.faq_by_topic(topic["id"])
    if not questions:
        await cb.message.answer(t("topic_empty", lang), reply_markup=topic_questions_kb(topic["id"], lang))
    else:
        await cb.message.answer(
            t("topic_pick_question", lang, topic=title),
            reply_markup=topic_questions_kb(topic["id"], lang),
        )
    await cb.answer()

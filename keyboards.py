"""Inline-клавиатуры и callback-данные."""
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from i18n import t
from storage import kb


class LangCB(CallbackData, prefix="lang"):
    lang: str


class MenuCB(CallbackData, prefix="menu"):
    action: str  # ask | topics | lang | home


class TopicCB(CallbackData, prefix="topic"):
    topic_id: str


class FaqCB(CallbackData, prefix="faq"):
    faq_id: str


class AdminCB(CallbackData, prefix="admin"):
    action: str          # add | stats | cancel | topic
    value: str = ""      # для action=topic — id темы


def language_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🇷🇺 Русский", callback_data=LangCB(lang="ru"))
    b.button(text="🇬🇧 English", callback_data=LangCB(lang="en"))
    b.adjust(2)
    return b.as_markup()


def main_menu_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("btn_ask", lang), callback_data=MenuCB(action="ask"))
    b.button(text=t("btn_topics", lang), callback_data=MenuCB(action="topics"))
    b.button(text=t("btn_lang", lang), callback_data=MenuCB(action="lang"))
    b.adjust(1, 1, 1)
    return b.as_markup()


def topics_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for topic in kb.topics:
        title = f"{topic.get('emoji', '')} {topic['title'].get(lang, topic['title']['ru'])}".strip()
        b.button(text=title, callback_data=TopicCB(topic_id=topic["id"]))
    b.button(text=t("btn_back_menu", lang), callback_data=MenuCB(action="home"))
    b.adjust(1)
    return b.as_markup()


def topic_questions_kb(topic_id: str, lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for item in kb.faq_by_topic(topic_id):
        q = item["question"].get(lang) or item["question"]["ru"]
        b.button(text=q[:60], callback_data=FaqCB(faq_id=item["id"]))
    b.button(text=t("btn_topics", lang), callback_data=MenuCB(action="topics"))
    b.button(text=t("btn_back_menu", lang), callback_data=MenuCB(action="home"))
    b.adjust(1)
    return b.as_markup()


def suggestions_kb(items: list, lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for item in items:
        q = item["question"].get(lang) or item["question"]["ru"]
        b.button(text=q[:60], callback_data=FaqCB(faq_id=item["id"]))
    b.button(text=t("btn_back_menu", lang), callback_data=MenuCB(action="home"))
    b.adjust(1)
    return b.as_markup()


def after_answer_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("btn_ask_again", lang), callback_data=MenuCB(action="ask"))
    b.button(text=t("btn_back_menu", lang), callback_data=MenuCB(action="home"))
    b.adjust(1)
    return b.as_markup()


def admin_menu_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("admin_add", lang), callback_data=AdminCB(action="add"))
    b.button(text=t("admin_count", lang), callback_data=AdminCB(action="stats"))
    b.adjust(1)
    return b.as_markup()


def admin_topics_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for topic in kb.topics:
        title = f"{topic.get('emoji', '')} {topic['title'].get(lang, topic['title']['ru'])}".strip()
        b.button(text=title, callback_data=AdminCB(action="topic", value=topic["id"]))
    b.button(text=t("admin_cancel", lang), callback_data=AdminCB(action="cancel"))
    b.adjust(1)
    return b.as_markup()

"""Тексты интерфейса на двух языках (RU/EN)."""

DEFAULT_LANG = "ru"
LANGS = ("ru", "en")

TEXTS = {
    "choose_lang": {
        "ru": "👋 Привет! Я помогу с поступлением в Италию.\n\nВыберите язык / Choose your language:",
        "en": "👋 Hi! I'll help you with studying in Italy.\n\nВыберите язык / Choose your language:",
    },
    "welcome": {
        "ru": (
            "Готово! Я бот-консультант по поступлению в Италию 🇮🇹\n\n"
            "Просто напишите свой вопрос — например, «Какие документы нужны для визы?».\n"
            "Или выберите тему в меню ниже."
        ),
        "en": (
            "All set! I'm your assistant for studying in Italy 🇮🇹\n\n"
            "Just type your question — e.g. \"What documents do I need for the visa?\".\n"
            "Or pick a topic from the menu below."
        ),
    },
    "menu_title": {
        "ru": "📋 Главное меню. Чем помочь?",
        "en": "📋 Main menu. How can I help?",
    },
    "btn_ask": {"ru": "❓ Задать вопрос", "en": "❓ Ask a question"},
    "btn_topics": {"ru": "📁 Темы", "en": "📁 Topics"},
    "btn_lang": {"ru": "🌐 Сменить язык", "en": "🌐 Change language"},
    "btn_back_menu": {"ru": "🏠 В меню", "en": "🏠 Menu"},
    "btn_ask_again": {"ru": "🔄 Задать новый вопрос", "en": "🔄 Ask another question"},
    "ask_prompt": {
        "ru": "✍️ Напишите свой вопрос одним сообщением.",
        "en": "✍️ Type your question in one message.",
    },
    "topics_title": {
        "ru": "Выберите тему:",
        "en": "Choose a topic:",
    },
    "topic_pick_question": {
        "ru": "Частые вопросы по теме «{topic}». Выберите:",
        "en": "Popular questions in \"{topic}\". Choose one:",
    },
    "topic_empty": {
        "ru": "Пока нет вопросов по этой теме.",
        "en": "No questions in this topic yet.",
    },
    "suggest": {
        "ru": "🤔 Не нашёл точного ответа. Может, вы имели в виду:",
        "en": "🤔 No exact match. Did you mean:",
    },
    "not_found": {
        "ru": (
            "😕 Пока у меня нет информации по этому вопросу.\n"
            "Пожалуйста, уточните вопрос или выберите тему из меню."
        ),
        "en": (
            "😕 I don't have information on this yet.\n"
            "Please rephrase your question or pick a topic from the menu."
        ),
    },
    "source_topic": {"ru": "Тема: {topic}", "en": "Topic: {topic}"},
    # --- admin ---
    "admin_only": {"ru": "Команда только для админов.", "en": "Admins only."},
    "admin_menu": {"ru": "🛠 Админ-панель:", "en": "🛠 Admin panel:"},
    "admin_add": {"ru": "➕ Добавить Q&A", "en": "➕ Add Q&A"},
    "admin_count": {"ru": "📊 Статистика", "en": "📊 Stats"},
    "admin_cancel": {"ru": "✖️ Отмена", "en": "✖️ Cancel"},
    "admin_pick_topic": {"ru": "Выберите тему для вопроса:", "en": "Pick a topic:"},
    "admin_q_ru": {"ru": "Введите вопрос (RU):", "en": "Enter question (RU):"},
    "admin_q_en": {"ru": "Введите вопрос (EN) или «-» чтобы пропустить:", "en": "Enter question (EN) or \"-\" to skip:"},
    "admin_a_ru": {"ru": "Введите ответ (RU):", "en": "Enter answer (RU):"},
    "admin_a_en": {"ru": "Введите ответ (EN) или «-» чтобы пропустить:", "en": "Enter answer (EN) or \"-\" to skip:"},
    "admin_keywords": {"ru": "Ключевые слова через запятую (или «-»):", "en": "Keywords, comma-separated (or \"-\"):"},
    "admin_saved": {"ru": "✅ Сохранено! В базе теперь {n} вопросов.", "en": "✅ Saved! Knowledge base now has {n} questions."},
    "admin_cancelled": {"ru": "Отменено.", "en": "Cancelled."},
    "admin_stats": {"ru": "📊 Вопросов в базе: {n}\nПо темам:\n{by_topic}", "en": "📊 Questions: {n}\nBy topic:\n{by_topic}"},
}


def t(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in LANGS else DEFAULT_LANG
    template = TEXTS[key].get(lang) or TEXTS[key][DEFAULT_LANG]
    return template.format(**kwargs) if kwargs else template

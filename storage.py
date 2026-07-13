"""Хранилище: база знаний (FAQ) и языки пользователей — простые JSON-файлы."""
import json
import os
import threading
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
KB_PATH = os.path.join(DATA_DIR, "knowledge_base.json")
USERS_PATH = os.path.join(DATA_DIR, "users.json")

_lock = threading.Lock()


def _read_json(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


class KnowledgeBase:
    """Держит FAQ в памяти, умеет перезагружаться и дозаписывать новые Q&A."""

    def __init__(self, path: str = KB_PATH):
        self.path = path
        self._data = {"topics": [], "faq": []}
        self.reload()

    def reload(self) -> None:
        with _lock:
            self._data = _read_json(self.path, {"topics": [], "faq": []})

    @property
    def topics(self) -> list:
        return self._data.get("topics", [])

    @property
    def faq(self) -> list:
        return self._data.get("faq", [])

    def topic(self, topic_id: str) -> Optional[dict]:
        return next((t for t in self.topics if t["id"] == topic_id), None)

    def faq_by_id(self, faq_id: str) -> Optional[dict]:
        return next((q for q in self.faq if q["id"] == faq_id), None)

    def faq_by_topic(self, topic_id: str) -> list:
        return [q for q in self.faq if q.get("topic") == topic_id]

    def add_faq(self, item: dict) -> None:
        """Добавляет Q&A и сразу пишет на диск (бот не останавливается)."""
        with _lock:
            self._data.setdefault("faq", []).append(item)
            _write_json(self.path, self._data)

    def next_id(self, topic_id: str) -> str:
        n = len(self.faq_by_topic(topic_id)) + 1
        base = f"{topic_id}-{n}"
        existing = {q["id"] for q in self.faq}
        while base in existing:
            n += 1
            base = f"{topic_id}-{n}"
        return base


class UserStore:
    """Запоминает выбранный язык пользователя между перезапусками."""

    def __init__(self, path: str = USERS_PATH):
        self.path = path
        self._data = _read_json(path, {})

    def get_lang(self, user_id: int) -> Optional[str]:
        return self._data.get(str(user_id), {}).get("lang")

    def set_lang(self, user_id: int, lang: str) -> None:
        with _lock:
            self._data.setdefault(str(user_id), {})["lang"] = lang
            _write_json(self.path, self._data)


kb = KnowledgeBase()
users = UserStore()

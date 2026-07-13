"""Локальный fuzzy-поиск по базе знаний — без ИИ и без внешних ключей.

Считаем близость запроса к каждому вопросу по трём сигналам:
  1. пословное пересечение (Jaccard по токенам),
  2. символьное сходство строк (difflib SequenceMatcher),
  3. вхождение ключевых слов.
Ищем и по RU, и по EN, и по списку keywords — язык вопроса значения не имеет.
"""
import re
from difflib import SequenceMatcher
from typing import List, Tuple

# Порог «точного» ответа — сразу выдаём.
EXACT_THRESHOLD = 0.72
# Порог «похоже» — показываем как варианты «может, вы имели в виду».
SUGGEST_THRESHOLD = 0.30
MAX_SUGGESTIONS = 4

_word_re = re.compile(r"[^\w]+", re.UNICODE)
# Короткие стоп-слова, которые только шумят при сравнении (RU/EN).
_STOP = {
    "и", "в", "во", "на", "по", "для", "что", "это", "мне", "нужно", "нужны",
    "нужен", "ли", "с", "у", "о", "об", "за", "the", "a", "an", "to", "for", "of",
    "do", "i", "is", "are", "need", "my", "me",
}

# Частые окончания RU (длинные — первыми), чтобы «виза»/«визы»/«визой» → один корень.
_RU_SUFFIXES = (
    "иями", "ями", "ами", "ыми", "ими", "ого", "его", "ому", "ему", "ыми",
    "ах", "ях", "ов", "ев", "ей", "ий", "ый", "ая", "яя", "ое", "ее", "ые",
    "ие", "ом", "ем", "ую", "юю", "ой", "ыx", "их", "ий",
    "а", "я", "о", "е", "у", "ю", "ы", "и", "ь",
)


def normalize(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = _word_re.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _stem(word: str) -> str:
    """Очень простой стеммер: срезаем частое RU-окончание и хвостовую 's' у EN."""
    if len(word) > 4:
        for suf in _RU_SUFFIXES:
            if word.endswith(suf) and len(word) - len(suf) >= 4:
                return word[: -len(suf)]
    if len(word) > 3 and word.endswith("s") and word.isascii():
        return word[:-1]
    return word


def tokenize(text: str) -> set:
    return {_stem(w) for w in normalize(text).split() if w and w not in _STOP}


def _item_tokens(item: dict) -> set:
    """Все токены-корни вопроса (RU+EN) и ключевых слов."""
    toks = set()
    for lang in ("ru", "en"):
        toks |= tokenize(item.get("question", {}).get(lang, ""))
    for kw in item.get("keywords", []):
        toks |= tokenize(kw)
    return toks


def _item_score(query_norm: str, q_tokens: set, item: dict) -> float:
    if not q_tokens:
        return 0.0
    cand_tokens = _item_tokens(item)
    # coverage: какая доля слов запроса покрыта вопросом/ключевыми словами.
    coverage = len(q_tokens & cand_tokens) / len(q_tokens)
    # символьное сходство с самым похожим текстом вопроса.
    seq = 0.0
    for lang in ("ru", "en"):
        cand = normalize(item.get("question", {}).get(lang, ""))
        if cand:
            seq = max(seq, SequenceMatcher(None, query_norm, cand).ratio())
    return 0.6 * coverage + 0.4 * seq


def search(query: str, faq: List[dict]) -> List[Tuple[float, dict]]:
    """Возвращает список (score, item), отсортированный по убыванию, только score > 0."""
    query_norm = normalize(query)
    q_tokens = tokenize(query)
    if not query_norm:
        return []
    scored = [(_item_score(query_norm, q_tokens, item), item) for item in faq]
    scored = [pair for pair in scored if pair[0] > 0]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def classify(query: str, faq: List[dict]):
    """Решает исход поиска.

    Возвращает кортеж (kind, payload):
      ("answer", item)        — нашли точный ответ,
      ("suggest", [items])    — есть похожие варианты,
      ("none", None)          — ничего подходящего.
    """
    scored = search(query, faq)
    if not scored:
        return "none", None

    top_score, top_item = scored[0]
    if top_score >= EXACT_THRESHOLD:
        return "answer", top_item

    suggestions = [item for score, item in scored if score >= SUGGEST_THRESHOLD][:MAX_SUGGESTIONS]
    if suggestions:
        return "suggest", suggestions
    return "none", None

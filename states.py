"""FSM-состояния."""
from aiogram.fsm.state import State, StatesGroup


class AskFlow(StatesGroup):
    waiting_question = State()


class AdminAdd(StatesGroup):
    topic = State()
    question_ru = State()
    question_en = State()
    answer_ru = State()
    answer_en = State()
    keywords = State()

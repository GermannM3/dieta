from aiogram.fsm.state import State, StatesGroup


class Chat(StatesGroup):
    active = State()
    inactive = State()
    waiting = State()

class Image(StatesGroup):
    prompt = State()

class FatTracker(StatesGroup):
    waist = State()      # Ввод обхвата талии
    hip = State()        # Ввод обхвата бедер
    neck = State()       # Ввод обхвата шеи (для мужчин)
    goal = State()       # Ввод целевого процента жира
    view_history = State()  # Просмотр истории измерений
from aiogram.fsm.state import StatesGroup, State

class UserForm(StatesGroup):
    language = State()
    goal = State()
    weight = State()
    height = State()

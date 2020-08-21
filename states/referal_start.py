from aiogram.dispatcher.filters.state import StatesGroup, State


class ReferalStart(StatesGroup):
    WaitCode = State()

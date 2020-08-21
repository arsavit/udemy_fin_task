from aiogram.dispatcher.filters.state import StatesGroup, State


class Quantity(StatesGroup):
    WaitQuantity = State()
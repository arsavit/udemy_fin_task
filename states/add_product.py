from aiogram.dispatcher.filters.state import StatesGroup, State


class NewProduct(StatesGroup):
    """Стейты для добавления товара"""
    Title = State()
    Description = State()
    Price = State()
    PriceDollar = State()
    Photo = State()
    PhotoUrl = State()
    Confirmation = State()
    EditTitle = State()
    EditDescription = State()
    EditPrice = State()
    EditPhoto = State()
    EditPhotoUrl = State()

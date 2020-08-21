import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, CallbackQuery

from data.config import admins
# from keyboards.inline.callback_data import confirm_new_product_callback

from keyboards.inline.edit_product import edit_product_markup
from loader import dp, bot, db
from states.add_product import NewProduct


@dp.message_handler(text='add_product', user_id=admins)
async def admin_add_product(message: types.Message):
    """Начинаем добавлять товар"""
    await message.answer('Сейчас добавим новый товар. \n Пожалуйста введите название')
    await NewProduct.Title.set()


@dp.message_handler(state=NewProduct.Title, user_id=admins)
async def get_product_title(message: types.Message, state: FSMContext):
    """Получаем название товара"""
    title = message.text
    await state.update_data(title=title)
    await message.answer(f'Пожалуйста добавьте описание товара {title}')
    await NewProduct.Description.set()


@dp.message_handler(state=NewProduct.Description, user_id=admins)
async def get_product_description(message: types.Message, state: FSMContext):
    """Получаем описание товара"""
    description = message.text
    await state.update_data(description=description)
    await message.answer('Пожалуйста укажите цену в долларах')
    await NewProduct.PriceDollar.set()


@dp.message_handler(state=NewProduct.PriceDollar, user_id=admins)
async def get_product_price_dollar(message: types.Message, state: FSMContext):
    """Получаем цену товара в долларах"""
    price_dollar = message.text
    await state.update_data(price_dollar=price_dollar)
    await message.answer('Пожалуйста укажите цену в формате телеграма\n1.00$ = 100')
    await NewProduct.Price.set()


@dp.message_handler(state=NewProduct.Price, user_id=admins)
async def get_product_price(message: types.Message, state: FSMContext):
    """Получаем цену товара в формате телеграма"""
    price = message.text
    await state.update_data(price=price)
    await message.answer('Теперь добавьте ссылку на миниатюру')
    await NewProduct.PhotoUrl.set()


@dp.message_handler(state=NewProduct.PhotoUrl, user_id=admins)
async def get_product_photo_thumb(message: types.Message, state: FSMContext):
    """Получаем миниатюру фото товара"""
    photo_url = message.text
    await state.update_data(photo_url=photo_url)
    await message.answer('Теперь добавьте фотографию')
    await NewProduct.Photo.set()


@dp.message_handler(state=NewProduct.Photo, user_id=admins, content_types=ContentTypes.PHOTO)
async def get_product_photo(message: types.Message, state: FSMContext):
    """Получаем фотографию товара"""
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    data = await state.get_data()
    title = data.get('title')
    price = data.get('price_dollar')
    description = data.get('description')
    photo_url = data.get('photo_url')
    await message.answer('Пожалуйста проверьте все еще раз.')
    await bot.send_photo(chat_id=message.from_user.id,
                         caption=f'Название: {title}\n Описание: {description}\n Цена: {price}$\n ссылка на фото: {photo_url}',
                         photo=photo_id)
    await message.answer(text='Добваляем товар?', reply_markup=edit_product_markup)
    await NewProduct.Confirmation.set()


@dp.callback_query_handler(text='edit_new_product_title', state=NewProduct.Confirmation)
async def edit_new_product_title(call: CallbackQuery):
    """Изменяем название товара"""
    await call.message.answer('Введите новое название товара')
    await NewProduct.EditTitle.set()


@dp.message_handler(state=NewProduct.EditTitle, user_id=admins)
async def get_product_edit_title(message: types.Message, state: FSMContext):
    """Получаем новое название товара"""
    title = message.text
    await state.update_data(title=title)
    await message.answer(f'Новое название товара: {title}')
    data = await state.get_data()
    description = data.get('description')
    price = data.get('price_dollar')
    photo_id = data.get('photo_id')
    photo_url = data.get('photo_url')
    await message.answer('Пожалуйста проверьте все еще раз.')
    await bot.send_photo(chat_id=message.from_user.id,
                         caption=f'Название: {title}\n Описание: {description}\n Цена: {price}$\n Миниатюра: {photo_url}',
                         photo=photo_id)
    await message.answer(text='Добваляем товар?', reply_markup=edit_product_markup)
    await NewProduct.Confirmation.set()


@dp.callback_query_handler(text='edit_new_product_description', state=NewProduct.Confirmation)
async def edit_new_product_description(call: CallbackQuery):
    """Изменяем описание товара"""
    await call.message.answer('Введите новое описание товара')
    await NewProduct.EditDescription.set()


@dp.message_handler(state=NewProduct.EditDescription, user_id=admins)
async def get_product_edit_description(message: types.Message, state: FSMContext):
    """Получаем новое описание товара"""
    description = message.text
    await state.update_data(description=description)
    await message.answer(f'Новая цена товара: {description}')
    data = await state.get_data()
    title = data.get('title')
    price = data.get('price_dollar')
    photo_id = data.get('photo_id')
    photo_url = data.get('photo_url')
    await message.answer('Пожалуйста проверьте все еще раз.')
    await bot.send_photo(chat_id=message.from_user.id,
                         caption=f'Название: {title}\n Описание: {description}\n Цена: {price}$\n Миниатюра: {photo_url}',
                         photo=photo_id)
    await message.answer(text='Добваляем товар?', reply_markup=edit_product_markup)
    await NewProduct.Confirmation.set()


@dp.callback_query_handler(text='edit_new_product_price', state=NewProduct.Confirmation)
async def edit_new_product_price(call: CallbackQuery):
    """Изменяем цену товара"""
    await call.message.answer('Введите новую цену товара')
    await NewProduct.EditPrice.set()


@dp.message_handler(state=NewProduct.EditPrice, user_id=admins)
async def get_product_edit_price(message: types.Message, state: FSMContext):
    """Получаем новую цену товара"""
    price = message.text
    await state.update_data(price_dollar=price)
    await message.answer(f'Новая цена товара: {price}')
    data = await state.get_data()
    title = data.get('title')
    description = data.get('description')
    photo_id = data.get('photo_id')
    photo_url = data.get('photo_url')
    await message.answer('Пожалуйста проверьте все еще раз.')
    await bot.send_photo(chat_id=message.from_user.id,
                         caption=f'Название: {title}\n Описание: {description}\n Цена: {price}$\n ссылка на миниатюру: {photo_url}',
                         photo=photo_id)
    await message.answer(text='Добваляем товар?', reply_markup=edit_product_markup)
    await NewProduct.Confirmation.set()


@dp.callback_query_handler(text='edit_new_product_photo_url', state=NewProduct.Confirmation)
async def edit_new_product_photo_url(call: CallbackQuery):
    """Изменяем миниатюру"""
    await call.message.answer('Введите новую ссылку на миниатюру')
    await NewProduct.EditPhotoUrl.set()


@dp.message_handler(state=NewProduct.EditPhotoUrl, user_id=admins)
async def get_product_edit_photo_url(message: types.Message, state: FSMContext):
    """Получаем новую миниатюру"""
    photo_url = message.text
    await state.update_data(photo_url=photo_url)
    await message.answer(f'Новая ссылка на миниатюру: {photo_url}')
    data = await state.get_data()
    title = data.get('title')
    description = data.get('description')
    photo_id = data.get('photo_id')
    price = data.get('price_dollar')
    await message.answer('Пожалуйста проверьте все еще раз.')
    await bot.send_photo(chat_id=message.from_user.id,
                         caption=f'Название: {title}\n Описание: {description}\n Цена: {price}$\n Ссылка на миниатюру: {photo_url}',
                         photo=photo_id)
    await message.answer(text='Добваляем товар?', reply_markup=edit_product_markup)
    await NewProduct.Confirmation.set()


@dp.callback_query_handler(text='edit_new_product_photo', state=NewProduct.Confirmation)
async def edit_new_product_photo(call: CallbackQuery):
    """Изменяем фото товара"""
    await call.message.answer('Загрузите новую фотографию товара')
    await NewProduct.EditPhoto.set()


@dp.message_handler(state=NewProduct.EditPhoto, user_id=admins, content_types=ContentTypes.PHOTO)
async def get_product_edit_photo(message: types.Message, state: FSMContext):
    """Получаем новую фотографию товара"""
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    data = await state.get_data()
    title = data.get('title')
    description = data.get('description')
    price = data.get('price_dollar')
    photo_url = data.get('photo_url')
    await message.answer('Пожалуйста проверьте все еще раз.')
    await bot.send_photo(chat_id=message.from_user.id,
                         caption=f'Название: {title}\n Описание: {description}\n Цена: {price}$\n ссылка на миниатюру: {photo_url}',
                         photo=photo_id)
    await message.answer(text='Добваляем товар?', reply_markup=edit_product_markup)
    await NewProduct.Confirmation.set()


@dp.callback_query_handler(text='confirm_new_product', state=NewProduct.Confirmation)
async def confirm_new_product(call: CallbackQuery, state: FSMContext):
    """Если админ подтверждает добавление товара, добавляем его в базу данных"""
    data = await state.get_data()
    title = data.get('title')
    description = data.get('description')
    price = int(data.get('price'))
    price_dollar = int(data.get('price_dollar'))
    photo_id = data.get('photo_id')
    photo_url = data.get('photo_url')
    await db.add_product(title, description, price, price_dollar, photo_id, photo_url, 5)

    await call.answer('Новый товар добавлен!', show_alert=True)
    await call.message.edit_reply_markup()
    await state.finish()


@dp.callback_query_handler(text='delete_new_product', state=NewProduct.Confirmation)
async def confirm_new_product(call: CallbackQuery, state: FSMContext):
    """Отменяем добавление нового товара"""
    await call.answer('Новый товар удален!', show_alert=True)
    await call.message.edit_reply_markup()
    await state.finish()

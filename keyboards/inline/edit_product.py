from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

edit_product_markup = InlineKeyboardMarkup(row_width=2,
                                           inline_keyboard=[
                                               [
                                                   InlineKeyboardButton(
                                                       text="Сохранить изменения",
                                                       callback_data='confirm_new_product'
                                                   ),
                                               ],
                                               [
                                                   InlineKeyboardButton(
                                                       text="Редактировать название",
                                                       callback_data='edit_new_product_title'
                                                   ),
                                               ],

                                               [
                                                   InlineKeyboardButton(
                                                       text="Редактировать описание",
                                                       callback_data='edit_new_product_description'
                                                   ),
                                               ],
                                               [
                                                   InlineKeyboardButton(
                                                       text="Редактировать цену",
                                                       callback_data='edit_new_product_price'
                                                   ),
                                               ],

                                               [
                                                   InlineKeyboardButton(
                                                       text="Изменить фотографию",
                                                       callback_data='edit_new_product_photo'
                                                   ),
                                               ],
                                               [
                                                   InlineKeyboardButton(
                                                       text="Удалить товар",
                                                       callback_data='delete_new_product'
                                                   ),
                                               ],

                                           ])

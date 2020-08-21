from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMessageContent

from loader import dp, db


async def get_products(products, bot_user):
    """Формируем списаок товаров для инлайн режима"""
    prod = []
    for product in products:
        item = types.InlineQueryResultArticle(
            id=product['id'],
            thumb_url=product['photo_url'],
            title=f"{product['title']}",
            description=f"Цена: {product['price']}\n{product['description']}",
            input_message_content=InputMessageContent(
                message_text=f"{product['photo_url']}\n {product['title']}\nЦена: {product['price']}\n{product['description']}\n"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Посмотреть товар',
                                             url=f'http://t.me/{bot_user.username}?start=product_{product["id"]}')
                    ]
                ]
            )

        )
        prod.append(item)
    return prod


@dp.inline_handler(text="")
async def empty_query(query: types.InlineQuery):
    """Выдаем отсортированный список при пустом запросе"""
    allowed_users = await db.select_all_user_id()
    print(allowed_users)
    user = int(query.from_user.id)
    print(user)
    if user in allowed_users:
        products = await db.select_all_products()
        bot_user = await dp.bot.get_me()
        await query.answer(
            results=await get_products(products, bot_user)

        )
    else:
        await query.answer(
            results=[],
            switch_pm_text='Бот недоступен. Подключить бота',
            switch_pm_parameter='connect_user'
        )
        return


@dp.inline_handler()
async def get_product_by_name(query: types.InlineQuery):
    """Формируем список товаров в зависимости от запроса"""
    allowed_users = await db.select_all_user_id()
    print(allowed_users)
    user = query.from_user.id

    if user in allowed_users:
        name_of_prod = query.query
        products = await db.select_product_by_beginning_of_name(name_of_prod)
        bot_user = await dp.bot.get_me()
        await query.answer(
            results=await get_products(products, bot_user)
        )

    else:
        await query.answer(
            results=[],
            switch_pm_text='Бот недоступен. Подключить бота',
            switch_pm_parameter='connect_user'
        )
        return

from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.types import LabeledPrice

from loader import dp, bot, db
from utils.misc.item import Item

from states.quantity import Quantity


@dp.message_handler(regexp="product_\d\w*")
async def show_product(message: types.Message, state: FSMContext):
    """Ловим запрос из инлайн мода и достаем из бд информацию о товаре, после чего просим ввести количество"""
    product_id = int(message.text.split('_')[-1])
    print(product_id)
    user = await db.select_user(message.from_user.id)
    prod = await db.select_product(product_id)
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=prod["photo_id"],
                         caption=f'Вы выбрали\n {prod["title"]}\n{prod["description"]}\n{prod["price_dollar"]}$')
    await message.answer('Пожалуйста, введите количество товара')
    await Quantity.WaitQuantity.set()
    await state.update_data(product_id=prod['id'])
    await state.update_data(prod_title=prod['title'])
    await state.update_data(prod_description=prod['description'])
    await state.update_data(discount=user['discount'])
    await state.update_data(prod_price=prod['price'])
    await state.update_data(photo_url=prod['photo_url'])


@dp.message_handler(regexp="\d\w*", state=Quantity.WaitQuantity)
async def get_product_quantity(message: types.Message, state: FSMContext):
    """Формируем заказ в зависимости от количества товара и скидки"""
    quantity = int(message.text)
    data = await state.get_data()
    print(data['prod_price'])
    price = data['prod_price'] * quantity
    print(price)
    await state.update_data(prod_price=price)
    if data['discount'] <= price:
        discount = data['discount']
    else:
        discount = price
    await state.update_data(discount=discount)
    await state.update_data(quantity=quantity)
    Product = Item(
        title=data['prod_title'],
        description=data['prod_description'],
        currency="USD",
        prices=[
            LabeledPrice(
                label=data['prod_title'],
                amount=price
            ),
            LabeledPrice(
                label='скидка',
                amount=-discount
            )
        ],
        start_parameter=f"create_invoice_{data['product_id']}",
        photo_url=data['photo_url'],
        photo_size=600
    )
    await message.answer(f'Вы выбрали\n {data["prod_title"]}\n Количество: {quantity}')
    try:
        await bot.send_invoice(message.from_user.id,
                               **Product.generate_invoice(),
                               payload=data['product_id'])
    except:
        await message.answer('Слишком большая сумма получается, попробуйте ввести меньшее количество')


@dp.shipping_query_handler(state=Quantity.WaitQuantity)
async def choose_shipping(query: types.ShippingQuery):
    await bot.answer_shipping_query(shipping_query_id=query.id,
                                    ok=True)


@dp.pre_checkout_query_handler(state=Quantity.WaitQuantity)
async def process_pre_checkout_query(query: types.PreCheckoutQuery, state: FSMContext):
    """После оплаты заносим данные в бд для доставки и уменьшаем реферальный баланс"""
    await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id,
                                        ok=True)
    data = await state.get_data()
    print(data['quantity'])
    print(data)
    await db.reduce_discount(query.from_user.id, data['discount'])
    await db.add_order(order_id=int(query.id), quantity=data['quantity'], user_id=query.from_user.id,
                       user_fn=query.from_user.first_name, user_username=query.from_user.username,
                       invoice_payload=int(query.invoice_payload),
                       country_code=query.order_info.shipping_address.country_code,
                       state_prod=query.order_info.shipping_address.state, city=query.order_info.shipping_address.city,
                       street_line1=query.order_info.shipping_address.street_line1,
                       street_line2=query.order_info.shipping_address.street_line2,
                       post_code=int(query.order_info.shipping_address.post_code), title=data['prod_title'],
                       price=data['prod_price'],
                       discount=data['discount'])

    print(query)
    print(query.total_amount)
    await bot.send_message(chat_id=query.from_user.id, text='Спасибо за покупку')
    await state.finish()

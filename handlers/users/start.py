from re import compile

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, db
from states.referal_start import ReferalStart


@dp.message_handler(CommandStart(deep_link='connect_user'))
async def connect_user(message: types.Message):
    """Инструкции пользователю, пришедшего из инлайн режима"""
    user_id = int(message.from_user.id)
    refr = await db.select_all_user_id()
    name = message.from_user.full_name
    bot_user = await dp.bot.get_me()
    if user_id in refr:
        await message.answer('Вы уже зарегистрированы в боте и можете начать поиск товаров или приглашение друзей\n'
                             f'  http://t.me/{bot_user.username}?start={user_id}',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Начать поиск товаров',
                                                              switch_inline_query_current_chat='')
                                     ]
                                 ]
                             ))
    else:
        await message.answer(f'Привет, {name}!\n'
                             f'Для пользования ботом Вы должны ввести пригласительный код\n'
                             f'Пожалуйста, ведите реферальный код или перейдите по действующей ссылке')
        await ReferalStart.WaitCode.set()


@dp.message_handler(CommandStart(deep_link=compile(r'\d\w*')))
async def bot_start_referal(message: types.Message):
    """Отлавливаем реферальные ссылки"""
    deep_link_args = int(message.get_args())
    print(deep_link_args)
    user_id = int(message.from_user.id)
    name = message.from_user.full_name
    refr = await db.select_all_user_id()
    bot_user = await dp.bot.get_me()
    if user_id in refr:
        await message.answer('Вы уже зарегистрированы в боте и можете начать поиск товаров или приглашение друзей\n'
                             f'  http://t.me/{bot_user.username}?start={user_id}',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Начать поиск товаров',
                                                              switch_inline_query_current_chat='')
                                     ]
                                 ]
                             ))
        # отправить ссылку на инлайн режим и реф код
    elif deep_link_args in refr:
        await db.add_user(user_id, deep_link_args, name)
        await db.add_referal(deep_link_args)
        await db.add_discount(deep_link_args)
        await message.answer(f'Привет, {name}!\n'
                             f'Ваш реферальный код принят\n'
                             f'Вы можете пригласить друзей по Вашей реферальной ссылке и получить по 10$ на баланс за каждого\n'
                             f'Ваша реферальная ссылка:\n'
                             f'  http://t.me/{bot_user.username}?start={user_id}\n'
                             f'Нажмите чтобы начать поиск товаров \n',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Начать поиск товаров',
                                                              switch_inline_query_current_chat='')
                                     ]
                                 ]
                             )
                             )  # Добавить переход в инлайн режим
    else:
        await message.answer(f'Привет, {name}!\n'
                             f'Реферальная ссылка недействительна! А без нее Вы не можете пользоваться ботом\n'
                             f'Пожалуйста, ведите реферальный код или перейдите по действующей ссылке')
        await ReferalStart.WaitCode.set()


@dp.message_handler(CommandStart(deep_link=None))
async def start(message: types.Message):
    """Ловим пользователей без реферальной ссылки"""
    user_id = message.from_user.id
    name = message.from_user.full_name
    refr = await db.select_all_user_id()
    print(refr)
    bot_user = await dp.bot.get_me()
    if user_id in refr:
        await message.answer('Вы уже зарегистрированы в боте и можете начать поиск товаров или приглашение друзей'
                             f' http://t.me/{bot_user.username}?start={user_id}\n',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Начать поиск товаров',
                                                              switch_inline_query_current_chat='')
                                     ]
                                 ]
                             ))
    else:
        await message.answer(f'Привет, {name}!\n'
                             f'Для пользования ботом Вы должны ввести пригласительный код\n'
                             f'Пожалуйста, ведите реферальный код или перейдите по действующей ссылке')
        await ReferalStart.WaitCode.set()


@dp.message_handler(CommandStart(deep_link=compile(r'\d\w*')), state=ReferalStart.WaitCode)
async def bot_start_referal(message: types.Message, state: FSMContext):
    """Ловим реферальную ссылку после попытки подключиться без ссылки"""
    deep_link_args = int(message.get_args())
    user_id = int(message.from_user.id)
    name = message.from_user.full_name
    refr = await db.select_all_user_id()
    bot_user = await dp.bot.get_me()
    if deep_link_args in refr:
        await db.add_user(user_id, deep_link_args, name)
        await db.add_referal(deep_link_args)
        await db.add_discount(deep_link_args)
        await state.finish()
        await message.answer(f'Привет, {name}!\n'
                             f'Ваш реферальный код принят\n'
                             f'Вы можете пригласить друзей по Вашей реферальной ссылке и получить по 10$ на баланс за каждого\n'
                             f'Ваша реферальная ссылка:\n'
                             f'  http://t.me/{bot_user.username}?start={user_id}\n',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Начать поиск товаров',
                                                              switch_inline_query_current_chat='')
                                     ]
                                 ]
                             ))  # Добавить переход в инлайн режим
    else:
        await message.answer(f'Привет, {name}!\n'
                             f'Реферальная ссылка недействительна! А без нее Вы не можете пользоваться ботом\n'
                             f'Пожалуйста, ведите реферальный код или перейдите по действующей ссылке')


@dp.message_handler(regexp="\d\w*", state=ReferalStart.WaitCode)
async def get_referal_code(message: types.Message, state: FSMContext):
    """Ловим реферальный код после попытки подключиться без ссылки"""
    user_id = message.from_user.id
    name = message.from_user.full_name
    ref_cod = int(message.text)
    refr = await db.select_all_user_id()
    bot_user = await dp.bot.get_me()
    if ref_cod in refr:
        await db.add_user(user_id, ref_cod, name)
        await db.add_referal(ref_cod)
        await db.add_discount(ref_cod)
        await state.finish()
        await message.answer(f'Привет, {name}!\n'
                             f'Ваш реферальный код принят\n'
                             f'Вы можете пригласить друзей по Вашей реферальной ссылке и получить по 10$ на баланс за каждого\n'
                             f'Ваша реферальная ссылка:\n'
                             f'  http://t.me/{bot_user.username}?start={user_id}\n',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Начать поиск товаров',
                                                              switch_inline_query_current_chat='')
                                     ]
                                 ]
                             ))  # Добавить переход в инлайн режим
    else:
        await message.answer(f'Привет, {name}!\n'
                             f'Реферальный код недействителен! А без него Вы не можете пользоваться ботом\n'
                             f'Пожалуйста, ведите реферальный код или перейдите по действующей ссылке')
        await ReferalStart.WaitCode.set()


@dp.message_handler(state=ReferalStart.WaitCode)
async def error_codes(message: types.Message):
    """Ловим все кроме реферальных кодов и ссылок"""
    await message.answer('Это не похоже на реферальный код. Попробуйте еще раз.')

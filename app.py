from loader import db
from data.config import admins








async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)
    print("создаю")
    await db.create_table_users()
    print('Готово')
    print('Создаю 2')
    await db.create_table_products()
    for user in admins:
        await db.add_user(user, 0, 'admin')
    print('готово')
    print('Создаю 3')
    await db.create_table_orders()
    print('Готово')

    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)

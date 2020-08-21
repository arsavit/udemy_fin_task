import asyncio
import asyncpg

from data import config


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.pool: asyncio.pool.Pool = loop.run_until_complete(
            asyncpg.create_pool(
                user=config.PGUSER,
                password=config.PGPASSWORD,
                host=config.ip
            )
        )

    async def create_table_users(self):
        """Создаем таблицу пользователей"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL UNIQUE ,
        name VARCHAR(255),
        referer INT NOT NULL,
        count_referals INT,
        discount INT);
        """
        await self.pool.execute(sql)

    async def create_table_products(self):
        """Создаем таблицу товаров"""
        sql = """
        CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        quantity INT,
        title VARCHAR(1000),
        description TEXT,
        price INT NOT NULL,
        price_dollar INT NOT NULL,
        photo_id VARCHAR(500),
        photo_url VARCHAR(1000));
        """
        await self.pool.execute(sql)

    async def create_table_orders(self):
        """Создаем таблицу заказов"""
        sql = """
        CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        order_id bigint,
        quantity INT,
        user_id INT,
        user_fn VARCHAR(255),
        user_username VARCHAR(255),
        invoice_payload INT,
        country_code VARCHAR(10),
        state_prod VARCHAR(255),
        city VARCHAR(255),
        street_line1 VARCHAR(1000),
        street_line2 VARCHAR(1000),
        post_code INT,
        title VARCHAR(1000),
        price INT NOT NULL,
        discount INT);
        """
        await self.pool.execute(sql)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += ' AND '.join([
            f'{item} = ${num}' for num, item in enumerate(parameters, start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, user_id: int, referer: int, name: str):
        """Добавляем пользователя в бд"""
        try:
            sql = "INSERT INTO users (user_id, name, referer, count_referals, discount) VALUES ($1, $2, $3, $4, $5)"
            await self.pool.execute(sql, user_id, name, referer, 0, 0)
        except asyncpg.exceptions.UniqueViolationError:
            print('Пользователь с таким user_id уже существует')

    async def select_all_users(self):
        """Выбираем всех пользователей"""
        sql = 'SELECT * FROM users'
        return await self.pool.fetch(sql)

    async def select_all_user_id(self):
        """Выбираем все id Пользователей"""
        all_users = await self.pool.fetch('SELECT user_id FROM users')
        all_users_id = [id['user_id'] for id in all_users]
        return all_users_id

    async def select_user(self, user_id):
        """Выбираем одного пользователя"""
        return await self.pool.fetchrow(f'SELECT * FROM users WHERE user_id = {user_id}')

    async def count_users(self):
        """Достаем количество пользователей"""
        return await self.pool.fetchval('SELECT COUNT(*) FROM users')

    async def add_referal(self, user_id):
        """Добавляем реферала пользователю"""
        count_ref = await self.pool.fetchval(f'SELECT count_referals FROM users WHERE user_id = {user_id}')
        count_ref += 1
        await self.pool.execute(f"UPDATE users SET count_referals = {count_ref} WHERE user_id = {user_id}")
        print(f'Количчесво рефералов у пользователя с user_id = {user_id} --{count_ref}')

    async def add_discount(self, user_id):
        """Добавляем 10$ за каждого реферала"""
        discount = await self.pool.fetchval(f'SELECT discount FROM users WHERE user_id = {user_id}')
        discount += 1000
        await self.pool.execute(f"UPDATE users SET discount = {discount} WHERE user_id = {user_id}")
        print(f'Баланс с рефералов пользователя с user_id = {user_id} для покупок {discount}')

    async def reduce_discount(self, user_id, amount):
        """Уменьшаем реферальный баланс"""
        discount = await self.pool.fetchval(f'SELECT discount FROM users WHERE user_id = {user_id}')
        discount -= amount
        await self.pool.execute(f"UPDATE users SET discount = {discount} WHERE user_id = {user_id}")

    async def add_product(self, title, description, price, price_dollar, photo_id, photo_url, quantity):
        """обавляем товар"""
        sql = "INSERT INTO products (title, description, price, price_dollar, photo_id, photo_url, quantity) VALUES ($1, $2, $3, $4, $5, $6, $7)"
        await self.pool.execute(sql, title, description, price, price_dollar, photo_id, photo_url, quantity)

    async def select_all_products(self):
        """Достаем все товары отсортированные по названию"""
        sql = 'SELECT * FROM products ORDER BY title'
        return await self.pool.fetch(sql)

    async def select_product(self, id):
        """Выбираем товар по id"""
        return await self.pool.fetchrow(f'SELECT * FROM products WHERE id = {id}')

    async def delete_product(self, product_id: int):
        """Удаляем товар"""
        return await self.pool.execute(f'DELETE FROM products WHERE id = {product_id}')

    async def select_product_by_beginning_of_name(self, user_input: str):
        """Достаем товары по части названия"""
        return await self.pool.fetch(f"SELECT * FROM products WHERE title ~~* '%{user_input}%' ORDER BY title")

    async def add_order(self, order_id, quantity, user_id, user_fn, user_username, invoice_payload, country_code,
                        state_prod, city, street_line1, street_line2, post_code, title, price, discount):
        """Добавляем заказ"""
        sql = "INSERT INTO orders (order_id, quantity, user_id, user_fn, user_username, invoice_payload, country_code, state_prod, city, street_line1, street_line2, post_code, title, price, discount) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)"
        await self.pool.execute(sql, order_id, quantity, user_id, user_fn, user_username, invoice_payload, country_code,
                                state_prod, city, street_line1, street_line2, post_code, title, price, discount)

# db = Database(loop=asyncio.get_event_loop())

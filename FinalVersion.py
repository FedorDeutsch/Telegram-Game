import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

token = "7014899022:AAEddAEJBNhGZsLNRqBu_JEOk1CtUp_OkTg"

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.gold = 0
        self.exp = 0
        self.level = 1
        self.workers = 2
        self.gold_per_sec = 0
        self.exp_per_sec = 0
        self.gold_workers = 0
        self.exp_workers = 0
        self.needed_exp = 200
        self.start_true = False
        self.pickaxe_level = 3
        self.sword_level = 3
        self.pickaxe_cost = 200
        self.sword_cost = 200

    def update_resources(self):
        self.gold += self.gold_per_sec
        self.exp += self.exp_per_sec

        while self.exp >= self.needed_exp:
            self.exp = 0
            self.level += 1
            self.needed_exp *= 2

class GameBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.users = {}
        self.worker_cost = 100

    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = User(user_id)
        return self.users[user_id]

    async def start(self):
        self.dp.message.register(self.start_command, Command(commands=["start"]))
        self.dp.message.register(self.save_command, Command(commands=["save"]))
        self.dp.callback_query.register(self.button_click, lambda c: True)
        await self.bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(self.update_resources_loop())
        await self.dp.start_polling(self.bot)

    async def update_resources_loop(self):
        while True:
            for user in self.users.values():
                user.update_resources()
            await asyncio.sleep(1)

    async def get_user_from_db(self, user_id):
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='Users',
            host='192.168.1.24',
            port=5424
        )

        user_data = await conn.fetchrow(f'''
            SELECT * FROM Users WHERE user_id = {user_id}
        ''')

        await conn.close()

        if user_data:
            user = User(user_id)
            user.gold = user_data['gold']
            user.exp = user_data['exp']
            user.level = user_data['level']
            user.workers = user_data['workers']
            user.gold_per_sec = user_data['gold_per_sec']
            user.exp_per_sec = user_data['exp_per_sec']
            user.gold_workers = user_data['gold_workers']
            user.exp_workers = user_data['exp_workers']
            user.needed_exp = user_data['needed_exp']
            user.pickaxe_level = user_data['pickaxe_level']
            user.sword_level = user_data['sword_level']
            user.pickaxe_cost = user_data['pickaxe_cost']
            user.sword_cost = user_data['sword_cost']
            return user
        return None

    async def start_command(self, message: types.Message):
        user_id = message.from_user.id
        user = await self.get_user_from_db(user_id)

        if user is None:
            # Если пользователь не найден в базе данных, создаем нового
            user = User(user_id)
            self.users[user_id] = user
            await self.save_user(user)
        else:
            # Если пользователь найден в базе данных, добавляем его в словарь
            self.users[user_id] = user

        if not user.start_true:
            user.start_true = True
            await self.save_user(user)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добыча золота 💰", callback_data="gold")],
            [InlineKeyboardButton(text="Добыча опыта ✨", callback_data="exp")],
            [InlineKeyboardButton(text="Магазин 🛒", callback_data="shop")],
            [InlineKeyboardButton(text="Профиль 👤", callback_data="profile")],
            [InlineKeyboardButton(text="Статистика 📊", callback_data="statistics")],
            [InlineKeyboardButton(text="Сохранить статистику 💾", callback_data="save_stats")]
        ])
        await message.answer("Основное меню", reply_markup=keyboard)

    async def save_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.get_user(user_id)
        await self.save_user(user)
        await message.answer("Ваш прогресс сохранен!")

    async def button_click(self, callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        user = self.get_user(user_id)
        user.update_resources()
        action = callback_query.data

        if action == "gold":
            await self.gold_click(callback_query, user)
        elif action == "exp":
            await self.exp_click(callback_query, user)
        elif action == "shop":
            await self.shop_menu(callback_query, user)
        elif action == "profile":
            await self.profile(callback_query, user)
        elif action == "statistics":
            await self.statistics(callback_query, user)
        elif action == "buy_worker":
            await self.buy_worker(callback_query, user)
        elif action == "upgrade_pickaxe":
            await self.upgrade_pickaxe(callback_query, user)
        elif action == "upgrade_sword":
            await self.upgrade_sword(callback_query, user)
        elif action == "save_stats":
            await self.save_stats(callback_query, user)

    async def gold_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нет рабочих")
        else:
            user.workers -= 1
            user.gold_workers += 1
            user.gold_per_sec += 10
            await callback_query.message.answer(
                f"1 рабочий отправлен на добычу золота.\nОсталось рабочих: {user.workers}"
            )

    async def exp_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нет рабочих")
        else:
            user.workers -= 1
            user.exp_workers += 1
            user.exp_per_sec += 20
            await callback_query.message.answer(
                f"1 рабочий отправлен на добычу опыта.\nОсталось рабочих: {user.workers}"
            )

    async def shop_menu(self, callback_query, user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить рабочего 👷", callback_data="buy_worker")],
            [InlineKeyboardButton(text="Улучшить кирку ⛏️", callback_data="upgrade_pickaxe")],
            [InlineKeyboardButton(text="Улучшить меч ⚔️", callback_data="upgrade_sword")]
        ])
        await callback_query.message.answer("Добро пожаловать в магазин!", reply_markup=keyboard)

    async def profile(self, callback_query, user):
        await callback_query.message.answer(
            f"Ваш профиль 👤:\n"
            f"Уровень: {user.level}\n"
            f"Опыт: {int(user.exp)}/{user.level * 200}\n"
            f"Золото: {int(user.gold)}\n"
            f"Золото/с: {user.gold_per_sec}\n"
            f"Опыт/с: {user.exp_per_sec}\n"
            f"Рабочие: {user.workers}"
        )

    async def statistics(self, callback_query, user):
        await callback_query.message.answer(
            f"Статистика 📊:\n"
            f"Рабочие на добыче золота: {user.gold_workers}\n"
            f"Рабочие на добыче опыта: {user.exp_workers}\n"
            f"Золото в секунду: {user.gold_per_sec}\n"
            f"Опыт в секунду: {user.exp_per_sec}"
        )

    async def buy_worker(self, callback_query, user):
        if user.gold >= self.worker_cost:
            user.gold -= self.worker_cost
            user.workers += 1
            self.worker_cost *= 2

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Купить рабочего 👷", callback_data="buy_worker")],
                [InlineKeyboardButton(text="Улучшить кирку ⛏️", callback_data="upgrade_pickaxe")],
                [InlineKeyboardButton(text="Улучшить меч ⚔️", callback_data="upgrade_sword")]
            ])
            await callback_query.message.edit_text(
                f"Вы купили рабочего. Осталось рабочих: {user.workers}",
                reply_markup=keyboard
            )
        else:
            await callback_query.message.answer(f"Вам не хватает золота для покупки рабочего. Стоимость: {self.worker_cost} золота")

    async def upgrade_pickaxe(self, callback_query, User):

        if User.gold >= User.pickaxe_cost and User.level >= User.pickaxe_level:
            User.gold -= User.pickaxe_cost
            User.gold_per_sec *= 2
            User.pickaxe_cost *= 2
            User.pickaxe_level *= 2
            await callback_query.message.answer(
                f"Вы улучшили свою кирку. Теперь золото в секунду: {User.gold_per_sec}")
        elif User.level < User.pickaxe_level:
            await callback_query.message.answer(f"Сейчас улучшение кирки открываеться на {User.pickaxe_level} уровне")
        elif User.gold < User.pickaxe_cost:
            await callback_query.message.answer(f"Вам не хватает {User.pickaxe_cost - User.gold} золота")

    async def upgrade_sword(self, callback_query, User):

        if User.gold >= User.sword_cost and User.level >= User.sword_level:
            User.gold -= User.sword_cost
            User.exp_per_sec *= 2
            User.sword_cost *= 2
            User.sword_level *= 2
            await callback_query.message.answer(f"Вы улучшили свой меч. Теперь опыт в секунду: {User.exp_per_sec}")
        elif User.level < User.sword_level:
            await callback_query.message.answer(f"Сейчас улучшение меча открываеться на {User.sword_level} уровне")
        elif User.gold < User.sword_cost:
            await callback_query.message.answer(f"Вам не хватает {User.sword_cost - User.gold} золота")

    async def save_user(self, user):
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='Users',
            host='192.168.1.24',
            port=5424
        )

        # Обновление или вставка данных пользователя
        await conn.execute(f'''
            INSERT INTO Users (user_id, gold, exp, level, workers, gold_per_sec, exp_per_sec, gold_workers, exp_workers, needed_exp, pickaxe_level, sword_level, pickaxe_cost, sword_cost)
            VALUES ({user.user_id}, {user.gold}, {user.exp}, {user.level}, {user.workers}, {user.gold_per_sec}, {user.exp_per_sec}, {user.gold_workers}, {user.exp_workers}, {user.needed_exp}, {user.pickaxe_level}, {user.sword_level}, {user.pickaxe_cost}, {user.sword_cost})
            ON CONFLICT (user_id)
            DO UPDATE SET
                gold = EXCLUDED.gold,
                exp = EXCLUDED.exp,
                level = EXCLUDED.level,
                workers = EXCLUDED.workers,
                gold_per_sec = EXCLUDED.gold_per_sec,
                exp_per_sec = EXCLUDED.exp_per_sec,
                gold_workers = EXCLUDED.gold_workers,
                exp_workers = EXCLUDED.exp_workers,
                needed_exp = EXCLUDED.needed_exp,
                pickaxe_level = EXCLUDED.pickaxe_level,
                sword_level = EXCLUDED.sword_level,
                pickaxe_cost = EXCLUDED.pickaxe_cost,
                sword_cost = EXCLUDED.sword_cost
        ''')

        await conn.close()

    async def save_stats(self, callback_query: types.CallbackQuery, user: User):
        await self.save_user(user)  # Сохранение пользователя в базе данных
        await callback_query.message.answer("Ваша статистика успешно сохранена!")
        await callback_query.answer()  # Подтверждение получения запроса
if __name__ == '__main__':
    bot = GameBot(token)
    asyncio.run(bot.start())

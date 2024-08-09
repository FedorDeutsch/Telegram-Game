import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

token = "YOUR_TOKEN_HERE"

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
        self.pickaxe_level = 3
        self.sword_level = 3
        self.pickaxe_cost = 200
        self.sword_cost = 200

    def update_resources(self):
        self.gold += self.gold_per_sec
        self.exp += self.exp_per_sec

        while self.exp >= self.needed_exp:
            self.exp -= self.needed_exp
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

    async def save_user(self, user):
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='Users',
            host='192.168.1.24',
            port=5424
        )

        await conn.execute(f'''
            INSERT INTO Users (user_id, gold, exp, level, workers, gold_per_sec, exp_per_sec, gold_workers, exp_workers, needed_exp, pickaxe_level, sword_level, pickaxe_cost, sword_cost)
            VALUES ({user.user_id}, {user.gold}, {user.exp}, {user.level}, {user.workers}, {user.gold_per_sec}, {user.exp_per_sec}, {user.gold_workers}, {user.exp_workers}, {user.needed_exp}, {user.pickaxe_level}, {user.sword_level}, {user.pickaxe_cost}, {user.sword_cost})
            ON CONFLICT (user_id) DO UPDATE
            SET gold = EXCLUDED.gold,
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

    async def start_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.get_user(user_id)

        if user.gold == 0 and user.exp == 0:
            db_user = await self.get_user_from_db(user_id)
            if db_user:
                self.users[user_id] = db_user
            else:
                user = User(user_id)
                self.users[user_id] = user
            await self.save_user(user)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Загрузить прогресс", callback_data="load_progress"),
             InlineKeyboardButton(text="Сохранить прогресс", callback_data="save_progress")],
            [InlineKeyboardButton(text="Добыча золота 💰", callback_data="gold"),
             InlineKeyboardButton(text="Добыча опыта ✨", callback_data="exp")],
            [InlineKeyboardButton(text="Магазин 🛒", callback_data="shop")],
            [InlineKeyboardButton(text="Профиль 👤", callback_data="profile")],
            [InlineKeyboardButton(text="Статистика 📊", callback_data="statistics")],
            [InlineKeyboardButton(text="Таблица лидеров 🏆", callback_data="leaderboard")]
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
        action = callback_query.data

        if action == "load_progress":
            db_user = await self.get_user_from_db(user_id)
            if db_user:
                self.users[user_id] = db_user
                await callback_query.message.answer("Прогресс загружен!")
            else:
                await callback_query.message.answer("Не удалось найти сохраненный прогресс.")

        elif action == "save_progress":
            await self.save_user(user)
            await callback_query.message.answer("Прогресс сохранен!")

        elif action == "gold":
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
        elif action == "leaderboard":
            await self.leaderboard(callback_query)

    async def leaderboard(self, callback_query: types.CallbackQuery):
        top_players = await self.get_top_players()

        if not top_players:
            await callback_query.message.answer("Нет данных для отображения.")
        else:
            leaderboard_text = "Топ 3 игрока:\n"
            for idx, player in enumerate(top_players):
                leaderboard_text += f"{idx + 1}. Пользователь {player['user_id']} - Золото: {player['gold']} - Уровень: {player['level']}\n"

            await callback_query.message.answer(leaderboard_text)

    async def gold_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нет рабочих")
        else:
            user.workers -= 1
            user.gold_workers += 1
            user.gold_per_sec += 10
            await callback_query.message.answer(
                f"1 рабочий отправлен на добычу золота.\nОсталось рабочих: {user.workers}")

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
            [InlineKeyboardButton(text=f"Купить рабочего ({self.worker_cost} золота)", callback_data="buy_worker")],
            [InlineKeyboard```python
Button(text=f"Улучшить кирку ({user.pickaxe_cost} золота)", callback_data="upgrade_pickaxe")],
            [InlineKeyboardButton(text=f"Улучшить меч ({user.sword_cost} золота)", callback_data="upgrade_sword")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
        ])

        await callback_query.message.answer("Магазин 🛒", reply_markup=keyboard)

    async def profile(self, callback_query, user):
        profile_text = (
            f"👤 Профиль пользователя:\n"
            f"🆔 ID: {user.user_id}\n"
            f"💰 Золото: {user.gold}\n"
            f"✨ Опыт: {user.exp}/{user.needed_exp}\n"
            f"⭐ Уровень: {user.level}\n"
            f"🔨 Уровень кирки: {user.pickaxe_level}\n"
            f"⚔️ Уровень меча: {user.sword_level}\n"
            f"👷 Рабочие: {user.workers}\n"
            f"💸 Золото в секунду: {user.gold_per_sec}\n"
            f"📈 Опыт в секунду: {user.exp_per_sec}\n"
        )
        await callback_query.message.answer(profile_text)

    async def statistics(self, callback_query, user):
        statistics_text = (
            f"📊 Статистика:\n"
            f"💰 Добыто золота: {user.gold}\n"
            f"✨ Добыто опыта: {user.exp}\n"
            f"⭐ Уровень: {user.level}\n"
            f"👷 Рабочие: {user.workers}\n"
            f"💸 Золото в секунду: {user.gold_per_sec}\n"
            f"📈 Опыт в секунду: {user.exp_per_sec}\n"
        )
        await callback_query.message.answer(statistics_text)

    async def buy_worker(self, callback_query, user):
        if user.gold >= self.worker_cost:
            user.gold -= self.worker_cost
            user.workers += 1
            await callback_query.message.answer(
                f"Вы наняли рабочего! Осталось рабочих: {user.workers}")
        else:
            await callback_query.message.answer("Недостаточно золота для найма рабочего.")

    async def upgrade_pickaxe(self, callback_query, user):
        if user.gold >= user.pickaxe_cost:
            user.gold -= user.pickaxe_cost
            user.pickaxe_level += 1
            user.gold_per_sec += 10  # Пример, может быть любая другая логика
            user.pickaxe_cost *= 2  # Увеличиваем стоимость следующего улучшения
            await callback_query.message.answer(
                f"Вы улучшили кирку до уровня {user.pickaxe_level}!")
        else:
            await callback_query.message.answer("Недостаточно золота для улучшения кирки.")

    async def upgrade_sword(self, callback_query, user):
        if user.gold >= user.sword_cost:
            user.gold -= user.sword_cost
            user.sword_level += 1
            user.exp_per_sec += 10  # Пример, может быть любая другая логика
            user.sword_cost *= 2  # Увеличиваем стоимость следующего улучшения
            await callback_query.message.answer(
                f"Вы улучшили меч до уровня {user.sword_level}!")
        else:
            await callback_query.message.answer("Недостаточно золота для улучшения меча.")

    async def get_top_players(self):
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='Users',
            host='192.168.1.24',
            port=5424
        )

        top_players = await conn.fetch('''
            SELECT user_id, gold, level FROM Users
            ORDER BY gold DESC
            LIMIT 3
        ''')

        await conn.close()
        return top_players

if __name__ == "__main__":
    game_bot = GameBot(token)
    asyncio.run(game_bot.start())

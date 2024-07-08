import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command


token = "7014899022:AAEddAEJBNhGZsLNRqBu_JEOk1CtUp_OkTg"

class Item:
    def __init__(self, name, cost, effect, level):
        self.name = name
        self.cost = cost
        self.effect = effect
        self.level = level

class Shop:
    def __init__(self):
        self.worker_cost = 100
        self.available_workers = 2
        self.pickaxes = [
            Item("Деревянная кирка", 50, 5, 1),
            Item("Бронзовая кирка", 100, 10, 3),
            Item("Железная кирка", 200, 20, 6),
            Item("Серебряная кирка", 400, 40, 12),
            Item("Золотая кирка", 800, 80, 24),
            Item("Платиновая кирка", 1600, 160, 48),
            Item("Алмазная кирка", 3200, 320, 96),
            Item("Титановая кирка", 6400, 640, 192),
            Item("Мифриловая кирка", 12800, 1280, 384),
            Item("Магическая кирка", 25600, 2560, 768)
        ]
        self.swords = [
            Item("Деревянный меч", 50, 10, 1),
            Item("Бронзовый меч", 100, 20, 3),
            Item("Железный меч", 200, 40, 6),
            Item("Серебряный меч", 400, 80, 12),
            Item("Золотой меч", 800, 160, 24),
            Item("Платиновый меч", 1600, 320, 48),
            Item("Алмазный меч", 3200, 640, 96),
            Item("Титановый меч", 6400, 1280, 192),
            Item("Мифриловый меч", 12800, 2560, 384),
            Item("Магический меч", 25600, 5120, 768)
        ]

    def get_available_items(self, level, item_type):
        items = self.pickaxes if item_type == 'pickaxe' else self.swords
        return [item for item in items if level >= item.level]

class User:
    def __init__(self):
        self.gold = 0
        self.exp = 0
        self.level = 1
        self.workers = 2
        self.gold_per_sec = 0
        self.exp_per_sec = 0

class GameBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.shop = Shop()
        self.users = {}

    async def start(self):
        self.dp.message.register(self.start, Command(commands=["start"]))
        self.dp.callback_query.register(self.button_click, lambda c: True)
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = User()
        return self.users[user_id]

    async def start(self, message: types.Message):
        buttons = [
            [InlineKeyboardButton(text="Добыча золота 💰", callback_data="gold")],
            [InlineKeyboardButton(text="Добыча опыта ✨", callback_data="exp")],
            [InlineKeyboardButton(text="Профиль 🤖", callback_data="profile")],
            [InlineKeyboardButton(text="Статистика 📊", callback_data="stats")],
            [InlineKeyboardButton(text="Магазин 🛒", callback_data="shop")],
            [InlineKeyboardButton(text="Гайд ⚙️", callback_data="guide")]
        ]
        await message.answer("Выберите кнопку", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

    async def button_click(self, callback_query: types.CallbackQuery):
        user = self.get_user(callback_query.from_user.id)
        action = callback_query.data
        if action == "gold":
            await self.gold_click(callback_query, user)
        elif action == "exp":
            await self.exp_click(callback_query, user)
        elif action == "profile":
            await self.profile(callback_query, user)
        elif action == "stats":
            await self.stats(callback_query, user)
        elif action == "shop":
            await self.shop(callback_query, user)
        elif action == "guide":
            await self.guide(callback_query)
        elif action == "buy_worker":
            await self.buy_worker(callback_query, user)

    async def gold_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нету рабочих")
        else:
            user.workers -= 1
            user.gold_per_sec += 10
            if user.gold_per_sec == 10:
                asyncio.create_task(self.give_gold(callback_query.from_user.id))
            await callback_query.message.answer(f"1 рабочий отправлен на добычу золота.\nОсталось рабочих: {user.workers}")

    async def exp_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нету рабочих")
        else:
            user.workers -= 1
            user.exp_per_sec += 20
            if user.exp_per_sec == 20:
                asyncio.create_task(self.give_exp(callback_query.from_user.id))
            await callback_query.message.answer(f"1 рабочий отправлен на добычу опыта. \nОсталось рабочих: {user.workers}")

    async def profile(self, callback_query, user):
        await callback_query.message.answer(f"Ваш профиль 👾:\nУровень 👽: {user.level}\nЗолото 💰: {user.gold}\nОпыт ✨: {user.exp}\nРабочие 👷: {user.workers}")

    async def stats(self, callback_query, user):
        await callback_query.message.answer(f"Статистика:\nЗолото/с: {user.gold_per_sec}\nОпыт/с: {user.exp_per_sec}")

    async def shop(self, callback_query):
        await callback_query.message.answer(f"Добро пожаловать в магазин!\nТекущая стоимость рабочего: {self.shop.worker_cost} золота.\nДля покупки рабочего нажмите на кнопку ниже:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Купить рабочего 👷", callback_data="buy_worker")]]))

    async def guide(self, callback_query):
        await callback_query.message.answer("Это руководство по использованию бота.")

    async def buy_worker(self, callback_query, user):
        if user.gold >= self.shop.worker_cost and self.shop.available_workers > 0:
            user.gold -= self.shop.worker_cost
            user.workers += 1
            self.shop.available_workers -= 1
            await callback_query.message.answer(f"Вы купили рабочего. Осталось рабочих: {self.shop.available_workers}\nСтоимость следующего рабочего: {self.shop.worker_cost * 2} золота.\nУ вас теперь {user.workers} рабочих.")
        else:
            await callback_query.message.answer("Недостаточно золота или нет доступных рабочих для покупки.")

    async def give_gold(self, user_id):
        while self.users[user_id].gold_per_sec > 0:
            self.users[user_id].gold += self.users[user_id].gold_per_sec
            await asyncio.sleep(1)

    async def give_exp(self, user_id):
        while self.users[user_id].exp_per_sec > 0:
            self.users[user_id].exp += self.users[user_id].exp_per_sec
            await asyncio.sleep(1)


bot = GameBot(token)
asyncio.run(bot.start())

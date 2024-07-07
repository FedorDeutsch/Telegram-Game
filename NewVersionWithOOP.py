import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command


token = "7014899022:AAEddAEJBNhGZsLNRqBu_JEOk1CtUp_OkTg"
class Item:
    def __init__(self, name, cost, effect, level):
        self.name = name
        self.cost = cost
        self.effect = effect
        self.level = level

class Store:
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

    def get_available_items(self, level, item_type): # Создание функции для определения
        items = self.pickaxes if item_type == 'pickaxe' else self.swords # Если `item_type` равен 'pickaxe', то в переменную `items` записывается список `self.pickaxes` (предположительно, список кирок)
        # Если `item_type` равен 'sword', то в переменную `items` записывается список `self.swords`
        return [item for item in items if level >= item.level] # Возвращаем список предметов доступных по уровню

class User:
    def __init__(self):
        self.gold = 0
        self.exp = 0
        self.level = 1
        self.pickaxe_level = 0
        self.sword_level = 0
        self.workers = 2
        self.gold_per_sec = 0
        self.exp_per_sec = 0

    def update_stats(self):
        self.gold_per_sec = 10 + self.workers * self.pickaxe_level
        self.exp_per_sec = 20 + self.workers * self.sword_level

class GameBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.store = Store()
        self.users = {}

    async def start(self):
        self.dp.message.register(self.start, Command(commands=["start"]))
        self.dp.callback_query.register(self.button_click, lambda c: True)
        await self.bot.delete_webhook(drop_pending_updates=True) # Удаляем вебхук и сообщения который били отправленны боту когда он был выключен
        await self.dp.start_polling(self.bot)

    def get_user(self, user_id): # Функция, которая проверяет есть ли id пользователя в словаре users, если нет то добавляет его
        if user_id not in self.users:
            self.users[user_id] = User()
        return self.users[user_id]

    async def start(self, message: types.Message):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Добыча золота 💰", callback_data="gold"),
            InlineKeyboardButton(text="Добыча опыта ✨", callback_data="exp")
        )
        builder.row(
            InlineKeyboardButton(text="Профиль 🤖", callback_data="profile"),
            InlineKeyboardButton(text="Статистика 📊", callback_data="stats")
        )
        builder.row(
            InlineKeyboardButton(text="Магазин 🛒", callback_data="shop")
        )
        builder.add(
            InlineKeyboardButton(text="Гайд ⚙️", callback_data="guide")
        )


        await message.answer("Выберите кнопку", reply_markup=builder.as_markup())

    async def button_click(self, callback_query: types.CallbackQuery): # callback_query содержит информацию о том, какая кнопка была нажата.
        user_id = callback_query.from_user.id
        user = self.get_user(user_id)
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
        elif action.startswith("buy_worker"):
            await self.buy_worker(callback_query, user)
        elif action.startswith("buy_pickaxe"):
            await self.buy_pickaxe(callback_query, user)
        elif action.startswith("upgrade_sword"):
            await self.upgrade_sword(callback_query, user)

    async def gold_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нету рабочих")
        else:
            if user.gold_per_sec == 0:
                asyncio.create_task(self.give_gold(callback_query.from_user.id))
            user.workers -= 1
            user.gold_per_sec += 10 + user.pickaxe_level
            await callback_query.message.answer(
                f"Вы будете получать {10 + user.pickaxe_level} золота каждую секунду за каждого рабочего.\n"
                f"1 рабочий отправлен на добычу золота.\nОсталось рабочих: {user.workers}"
            )

    async def exp_click(self, callback_query, user):
        if user.workers <= 0:
            await callback_query.message.answer("У вас нету рабочих")
        else:
            if user.exp_per_sec == 0:
                asyncio.create_task(self.give_exp(callback_query.from_user.id))
            user.workers -= 1
            user.exp_per_sec += 20 + user.sword_level
            await callback_query.message.answer(
                f"Вы будете получать {20 + user.sword_level} опыта каждую секунду за каждого рабочего.\n"
                f"1 рабочий отправлен на добычу опыта. \nОсталось рабочих: {user.workers}"
            )

    async def profile(self, callback_query, user):
        await callback_query.message.answer(
            f"Ваш профиль 👾:\n"
            f"Уровень 👽: {user.level}\n"
            f"Золото 💰: {user.gold}\n"
            f"Опыт ✨: {user.exp}/{user.level * 200}\n"
            f"Рабочие 👷: {user.workers}"
        )

    async def stats(self, callback_query, user):
        await callback_query.message.answer(
            f"Статистика:\n"
            f"Золото/с: {user.gold_per_sec}\n"
            f"Опыт/с: {user.exp_per_sec}"
        )

    async def shop(self, callback_query, user):
        cost = self.store.worker_cost
        available_workers = self.store.available_workers
        await callback_query.message.answer(
            f"Добро пожаловать в магазин!\n"
            f"Вы можете купить рабочих, кирки и улучшить меч здесь.\n"
            f"Текущая стоимость рабочего: {cost} золота.\n"
            f"Доступно рабочих для покупки: {available_workers}\n"
            "Для покупки рабочего нажмите на кнопку ниже:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Купить рабочего 👷", callback_data="buy_worker")],
                [InlineKeyboardButton(text="Кирки ⛏️", callback_data="shop_pickaxes")],
                [InlineKeyboardButton(text="Мечи ⚔️", callback_data="shop_swords")]
            ])
        )

    async def guide(self, callback_query):
        await callback_query.message.answer("Это руководство по использованию бота.")

    async def buy_worker(self, callback_query, user):
        cost = self.store.worker_cost
        if user.gold >= cost and self.store.available_workers > 0:
            user.gold -= cost
            user.workers += 1
            self.store.available_workers -= 1
            next_cost = cost * 2 if self.store.available_workers == 0 else cost
            if self.store.available_workers == 0:
                self.store.worker_cost = next_cost
                self.store.available_workers = 2
            await callback_query.message.answer(
                f"Вы успешно купили рабочего. Осталось рабочих: {self.store.available_workers}\n"
                f"Стоимость следующего рабочего: {next_cost} золота.\n"
                f"У вас теперь {user.workers} рабочих."
            )
        else:
            await callback_query.message.answer("Недостаточно золота или нет доступных рабочих для покупки.")

    async def buy_pickaxe(self, callback_query, user):
        available_pickaxes = self.store.get_available_items(user.level, 'pickaxe')
        if not available_pickaxes:
            await callback_query.message.answer("Нет доступных кирок для вашего уровня.")
            return

        buttons = []
        for pickaxe in available_pickaxes:
            buttons.append(
                InlineKeyboardButton(text=f"{pickaxe.name} - {pickaxe.cost} золота", callback_data=f"pickaxe_{pickaxe.level}")
            )
        await callback_query.message.answer("Доступные кирки:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[buttons]))

    async def upgrade_sword(self, callback_query, user):
        available_swords = self.store.get_available_items(user.level, 'sword')
        if not available_swords:
            await callback_query.message.answer("Нет доступных мечей для вашего уровня.")
            return

        buttons = []
        for sword in available_swords:
            buttons.append(
                InlineKeyboardButton(text=f"{sword.name} - {sword.cost} опыта", callback_data=f"sword_{sword.level}")
            )
        await callback_query.message.answer("Доступные мечи:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[buttons]))

    async def give_gold(self, user_id): # Функция дает столько солото сколько содержиться в переменной gold_per_sec (золото в секунду) и начисляет эту сумму раз в секунду
        while self.users[user_id].gold_per_sec > 0:
            self.users[user_id].gold += self.users[user_id].gold_per_sec
            await asyncio.sleep(1)

    async def give_exp(self, user_id):
        while self.users[user_id].exp_per_sec > 0:
            self.users[user_id].exp += self.users[user_id].exp_per_sec
            await self.level_up(user_id)
            await asyncio.sleep(1)

    async def level_up(self, user_id):
        user = self.get_user(user_id)
        if user.exp >= user.level * 200:
            user.exp -= user.level * 200
            user.level += 1
            await self.bot.send_message(user_id, f"Поздравляем! Вы достигли уровня {user.level}.")


# Запуск бота

bot = GameBot(token)
asyncio.run(bot.start())

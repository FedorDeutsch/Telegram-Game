import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackQuery

bot = Bot("7014899022:AAEddAEJBNhGZsLNRqBu_JEOk1CtUp_OkTg")
dp = Dispatcher()

user_stats = {}
store_stats = {
    "worker_cost": 100,
    "available_workers": 2,
    "pickaxes": [
        {"name": "Деревянная кирка", "cost": 50, "effect": 5, "level": 1},
        {"name": "Бронзовая кирка", "cost": 100, "effect": 10, "level": 3},
        {"name": "Железная кирка", "cost": 200, "effect": 20, "level": 6},
        {"name": "Серебряная кирка", "cost": 400, "effect": 40, "level": 12},
        {"name": "Золотая кирка", "cost": 800, "effect": 80, "level": 24},
        {"name": "Платиновая кирка", "cost": 1600, "effect": 160, "level": 48},
        {"name": "Алмазная кирка", "cost": 3200, "effect": 320, "level": 96},
        {"name": "Титановая кирка", "cost": 6400, "effect": 640, "level": 192},
        {"name": "Мифриловая кирка", "cost": 12800, "effect": 1280, "level": 384},
        {"name": "Магическая кирка", "cost": 25600, "effect": 2560, "level": 768}
    ],
    "sword_upgrades": [
        {"name": "Деревянный меч", "cost": 50, "effect": 10, "level": 1},
        {"name": "Бронзовый меч", "cost": 100, "effect": 20, "level": 3},
        {"name": "Железный меч", "cost": 200, "effect": 40, "level": 6},
        {"name": "Серебряный меч", "cost": 400, "effect": 80, "level": 12},
        {"name": "Золотой меч", "cost": 800, "effect": 160, "level": 24},
        {"name": "Платиновый меч", "cost": 1600, "effect": 320, "level": 48},
        {"name": "Алмазный меч", "cost": 3200, "effect": 640, "level": 96},
        {"name": "Титановый меч", "cost": 6400, "effect": 1280, "level": 192},
        {"name": "Мифриловый меч", "cost": 12800, "effect": 2560, "level": 384},
        {"name": "Магический меч", "cost": 25600, "effect": 5120, "level": 768}
    ]
}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Добыча золота 💰", callback_data="gold"),
        types.InlineKeyboardButton(text="Добыча опыта ✨", callback_data="exp")
    )
    builder.row(
        types.InlineKeyboardButton(text="Профиль 🤖", callback_data="profile"),
        types.InlineKeyboardButton(text="Статистика 📊", callback_data="stats")
    )
    builder.row(
        types.InlineKeyboardButton(text="Магазин 🛒", callback_data="shop")
    )
    builder.add(
        types.InlineKeyboardButton(text="Гайд ⚙️", callback_data="guide")
    )

    builder.adjust(2, 2, 1)
    await message.answer(
        "Выберите кнопку",
        reply_markup=builder.as_markup()
    )


async def give_gold(user_id):
    while True:
        await asyncio.sleep(1)
        user_stats[user_id]["gold"] += user_stats[user_id]["gold_per_sec"]
        print(
            f"User {user_id} received {user_stats[user_id]['gold_per_sec']} gold. Total gold: {user_stats[user_id]['gold']}")


async def give_exp(user_id):
    while True:
        await asyncio.sleep(1)
        user_stats[user_id]["exp"] += user_stats[user_id]["exp_per_sec"]
        print(
            f"User {user_id} received {user_stats[user_id]['exp_per_sec']} exp. Total exp: {user_stats[user_id]['exp']}")

        if user_stats[user_id]["exp"] >= user_stats[user_id]["max_exp"]:
            user_stats[user_id]["level"] += 1
            user_stats[user_id]["exp"] -= user_stats[user_id]["max_exp"]
            user_stats[user_id]["max_exp"] += 200
            print(f"User {user_id} leveled up to {user_stats[user_id]['level']}")


@dp.callback_query(lambda c: c.data == "gold")
async def handle_gold_click(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    if user_stats[user_id]["workers"] <= 0:
        await callback_query.message.answer("У вас нету рабочих")
    else:
        if user_stats[user_id]["gold_per_sec"] == 0:
            asyncio.create_task(give_gold(user_id))

        user_stats[user_id]["workers"] -= 1
        user_stats[user_id]["gold_per_sec"] += 10 + user_stats[user_id]["pickaxe_effect"]

        await callback_query.message.answer(
            f"Вы будете получать {10 + user_stats[user_id]['pickaxe_effect']} золота каждую секунду за каждого рабочего.\n"
            f"1 рабочий отправлен на добычу золота.\nОсталось рабочих: {user_stats[user_id]['workers']}"
        )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "exp")
async def handle_exp_click(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    if user_stats[user_id]["workers"] <= 0:
        await callback_query.message.answer("У вас нету рабочих")
    else:
        if user_stats[user_id]["exp_per_sec"] == 0:
            asyncio.create_task(give_exp(user_id))

        user_stats[user_id]["workers"] -= 1
        user_stats[user_id]["exp_per_sec"] += 20 + user_stats[user_id]["sword_effect"]

        await callback_query.message.answer(
            f"Вы будете получать {20 + user_stats[user_id]['sword_effect']} опыта каждую секунду за каждого рабочего.\n"
            f"1 рабочий отправлен на добычу опыта. \nОсталось рабочих: {user_stats[user_id]['workers']}"
        )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "profile")
async def handle_profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    stats = user_stats[user_id]
    await callback_query.message.answer(
        f"Ваш профиль 👾:\n"
        f"Уровень 👽: {stats['level']}\n"
        f"Золото 💰: {stats['gold']}\n"
        f"Опыт ✨: {stats['exp']}/{stats['max_exp']}\n"
        f"Рабочие 👷: {stats['workers']}"
    )


@dp.callback_query(lambda c: c.data == "stats")
async def handle_stats(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    stats = user_stats[user_id]
    await callback_query.message.answer(
        f"Статистика:\n"
        f"Золото/с: {stats['gold_per_sec']}\n"
        f"Опыт/с: {stats['exp_per_sec']}"
    )


@dp.callback_query(lambda c: c.data == "guide")
async def handle_guide(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Это руководство по использованию бота.")


@dp.callback_query(lambda c: c.data == "shop")
async def handle_shop(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    cost = store_stats["worker_cost"]
    available_workers = store_stats["available_workers"]
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
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "shop_pickaxes")
async def handle_shop_pickaxes(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    current_level = user_stats[user_id]["level"]
    pickaxes = store_stats["pickaxes"]
    buttons = []

    for pickaxe in pickaxes:
        if current_level >= pickaxe["level"]:
            buttons.append([InlineKeyboardButton(text=f"Купить {pickaxe['name']} ({pickaxe['cost']} золота) ⛏️", callback_data=f"buy_pickaxe_{pickaxe['name']}")])

    await callback_query.message.answer(
        "Выберите кирку для покупки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "shop_swords")
async def handle_shop_swords(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    current_level = user_stats[user_id]["level"]
    swords = store_stats["sword_upgrades"]
    buttons = []

    for sword in swords:
        if current_level >= sword["level"]:
            buttons.append([InlineKeyboardButton(text=f"Улучшить меч до {sword['name']} ({sword['cost']} золота) ⚔️", callback_data=f"upgrade_sword_{sword['name']}")])

    await callback_query.message.answer(
        "Выберите улучшение для меча:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "buy_worker")
async def handle_buy_worker(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    cost = store_stats["worker_cost"]
    available_workers = store_stats["available_workers"]

    if user_stats[user_id]["gold"] >= cost and available_workers > 0:
        user_stats[user_id]["gold"] -= cost
        user_stats[user_id]["workers"] += 1
        store_stats["available_workers"] -= 1

        if store_stats["available_workers"] == 0:
            store_stats["worker_cost"] *= 2
            store_stats["available_workers"] = 2
        await callback_query.message.answer(
            f"Вы успешно купили рабочего! 👷\n"
            f"Текущие рабочие: {user_stats[user_id]['workers']}\n"
            f"Золото: {user_stats[user_id]['gold']}\n"
            f"Следующий рабочий будет стоить: {store_stats['worker_cost']} золота."
        )
    else:
        if available_workers <= 0:
            await callback_query.message.answer(
                "Нет доступных рабочих для покупки. Пожалуйста, подождите, пока новые рабочие будут доступны.")
        else:
            await callback_query.message.answer("Недостаточно золота для покупки рабочих.")
    await callback_query.answer()


def update_stats(user_id):
    user_stats[user_id]["gold_per_sec"] = 10 + user_stats[user_id]["workers"] * user_stats[user_id]["pickaxe_effect"]
    user_stats[user_id]["exp_per_sec"] = 20 + user_stats[user_id]["workers"] * user_stats[user_id]["sword_effect"]


@dp.callback_query(lambda c: c.data.startswith("buy_pickaxe_"))
async def handle_buy_pickaxe(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    pickaxe_name = callback_query.data[len("buy_pickaxe_"):]
    pickaxe = next((p for p in store_stats["pickaxes"] if p["name"] == pickaxe_name), None)

    if pickaxe and user_stats[user_id]["level"] >= pickaxe["level"]:
        if user_stats[user_id]["gold"] >= pickaxe["cost"]:
            user_stats[user_id]["gold"] -= pickaxe["cost"]
            user_stats[user_id]["pickaxe_effect"] += pickaxe["effect"]
            update_stats(user_id)
            await callback_query.message.answer(
                f"Вы успешно купили {pickaxe['name']}! ⛏️\n"
                f"Теперь каждый рабочий добывает на {pickaxe['effect']} золота больше в секунду.\n"
                f"Золото: {user_stats[user_id]['gold']}"
            )
        else:
            await callback_query.message.answer("Недостаточно золота для покупки кирки.")
    else:
        await callback_query.message.answer("Недостаточный уровень для покупки этой кирки.")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("upgrade_sword_"))
async def handle_upgrade_sword(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {"gold": 0, "exp": 0, "level": 1, "max_exp": 200, "workers": 2, "gold_per_sec": 0,
                               "exp_per_sec": 0, "pickaxe_effect": 0, "sword_effect": 0}

    sword_name = callback_query.data[len("upgrade_sword_"):]
    sword = next((s for s in store_stats["sword_upgrades"] if s["name"] == sword_name), None)

    if sword and user_stats[user_id]["level"] >= sword["level"]:
        if user_stats[user_id]["gold"] >= sword["cost"]:
            user_stats[user_id]["gold"] -= sword["cost"]
            user_stats[user_id]["sword_effect"] += sword["effect"]
            update_stats(user_id)
            await callback_query.message.answer(
                f"Вы успешно улучшили меч до {sword['name']}! ⚔️\n"
                f"Теперь каждый рабочий добывает на {sword['effect']} опыта больше в секунду.\n"
                f"Золото: {user_stats[user_id]['gold']}"
            )
        else:
            await callback_query.message.answer("Недостаточно золота для улучшения меча.")
    else:
        await callback_query.message.answer("Недостаточный уровень для улучшения этого меча.")
    await callback_query.answer()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

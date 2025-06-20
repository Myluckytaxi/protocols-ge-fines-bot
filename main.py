import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from scraper import check_fines
from scheduler import start_scheduler

import os
import json

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

TRACK_FILE = "tracked.json"


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Отправь команду:\n"
        "`/fines <номер авто> <техпаспорт> [media:on]`\n\n"
        "Пример:\n`/fines YJ762YJ AJA5750122 media:on`\n\n"
        "📌 Чтобы отслеживать штрафы:\n"
        "`/track_add <номер> <техпаспорт>`",
        parse_mode="Markdown"
    )


@dp.message_handler(commands=["fines"])
async def fines_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Формат: `/fines <номер> <техпаспорт> [media:on]`", parse_mode="Markdown")
        return

    car_num, tech_pass = args[1], args[2]
    include_media = "media:on" in message.text

    await message.answer("🔍 Проверяю штрафы...")

    fines = check_fines(car_num, tech_pass, include_media)

    if not fines:
        await message.answer("✅ Штрафов не найдено.")
        return

    for fine in fines:
        await message.answer(fine)


@dp.message_handler(commands=["track_add"])
async def track_add_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Формат: `/track_add <номер> <техпаспорт>`", parse_mode="Markdown")
        return

    car, passport = args[1], args[2]
    user_id = message.from_user.id

    try:
        with open(TRACK_FILE, "r") as f:
            tracked = json.load(f)
    except:
        tracked = {}

    tracked[car] = {"passport": passport, "user_id": user_id}

    with open(TRACK_FILE, "w") as f:
        json.dump(tracked, f)

    await message.answer(f"✅ Авто `{car}` добавлено в отслеживание.", parse_mode="Markdown")


@dp.message_handler(commands=["track_list"])
async def track_list_cmd(message: types.Message):
    try:
        with open(TRACK_FILE, "r") as f:
            tracked = json.load(f)
    except:
        tracked = {}

    if not tracked:
        await message.answer("❌ Нет отслеживаемых авто.")
        return

    text = "📋 Отслеживаются:\n"
    for car, info in tracked.items():
        passport = info["passport"]
        text += f"- `{car}` / `{passport}`\n"

    await message.answer(text, parse_mode="Markdown")


@dp.message_handler(commands=["track_remove"])
async def track_remove_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Формат: `/track_remove <номер>`", parse_mode="Markdown")
        return

    car = args[1]

    try:
        with open(TRACK_FILE, "r") as f:
            tracked = json.load(f)
    except:
        tracked = {}

    if car in tracked:
        del tracked[car]
        with open(TRACK_FILE, "w") as f:
            json.dump(tracked, f)
        await message.answer(f"🗑 Удалено: `{car}`", parse_mode="Markdown")
    else:
        await message.answer("⚠️ Такой машины нет в списке.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_scheduler(bot)
    executor.start_polling(dp, skip_updates=True)

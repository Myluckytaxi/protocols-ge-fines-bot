import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from scraper import check_fines
from scheduler import start_scheduler

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_cmd(message):
    await message.answer("👋 Отправьте: /fines НОМЕР ТЕХПАСПОРТ [media:on]")

@dp.message_handler(commands=["fines"])
async def fines_cmd(message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Формат: /fines НОМЕР ТЕХПАСПОРТ [media:on]")
        return
    car_num, tech_pass = args[1], args[2]
    include_media = "media:on" in message.text
    fines = check_fines(car_num, tech_pass, include_media)
    if not fines:
        await message.answer("✅ Штрафов не найдено.")
        return
    for fine in fines:
        await message.answer(fine)

@dp.message_handler(commands=["track_add"])
async def track_add(message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Формат: /track_add НОМЕР ТЕХПАСПОРТ")
        return
    car, passport = args[1], args[2]
    user_id = message.from_user.id
    try:
        with open("tracked.json", "r") as f:
            tracked = json.load(f)
    except:
        tracked = {}
    tracked[car] = {"passport": passport, "user_id": user_id}
    with open("tracked.json", "w") as f:
        json.dump(tracked, f)
    await message.answer(f"✅ `{car}` добавлено.", parse_mode="Markdown")

async def main():
    # Запускаем планировщик
    await start_scheduler(bot)
    # Запускаем бота
    await executor.start(dp)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если цикл уже запущен, создаем задачу
            loop.create_task(main())
        else:
            # Если цикл не запущен, запускаем через asyncio.run()
            asyncio.run(main())
    except RuntimeError:
        # В случае ошибок — запускаем через asyncio.run()
        asyncio.run(main())

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import check_fines
import json


def start_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Tbilisi")

    @scheduler.scheduled_job("cron", hour=10, minute=0)
    async def daily_check():
        try:
            with open("tracked.json", "r") as f:
                tracked = json.load(f)
        except:
            tracked = {}

        for car, info in tracked.items():
            passport = info["passport"]
            user_id = info["user_id"]

            fines = check_fines(car, passport, include_media=True)
            if fines:
                text = f"🚨 Новые штрафы по `{car}`:\n\n" + "\n\n".join(fines)
                try:
                    await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
                except Exception as e:
                    print(f"❌ Ошибка при отправке уведомления: {e}")

    scheduler.start()
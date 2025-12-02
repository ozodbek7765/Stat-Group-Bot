import asyncio
from app.bot import dp, bot
from app.db import init_db
from app.scheduler import scheduler

async def main():
    await init_db()
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, close_bot_session=True)
    except asyncio.CancelledError:
        print("Bot polling cancelled. Graceful shutdown.")

if __name__ == "__main__":
    asyncio.run(main())
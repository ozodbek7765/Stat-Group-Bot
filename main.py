import asyncio
from app.bot import dp, bot
from app.db import init_db
from app.scheduler import scheduler

async def main():
    await init_db()
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

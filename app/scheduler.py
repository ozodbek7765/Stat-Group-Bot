import asyncio
import datetime
from config import OWNER_ID
from .db import AsyncSessionLocal
from .report import generate_daily_report
from .bot import bot

async def scheduler():
    while True:
        now = datetime.datetime.now()
        if now.hour == 23 and now.minute == 59:
            async with AsyncSessionLocal() as session:
                report = await generate_daily_report(session)
                await bot.send_message(OWNER_ID, report)
            await asyncio.sleep(60)
        await asyncio.sleep(30)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db import AsyncSessionLocal
from app.report import send_daily_report, update_hourly_stats
from app.models import Group
from sqlalchemy import select

scheduler = AsyncIOScheduler()

async def hourly_stats_job():
    async with AsyncSessionLocal() as session:
        groups = await session.scalars(select(Group))
        for group in groups:
            await update_hourly_stats(group.id)

async def daily_report_job(bot):
    async with AsyncSessionLocal() as session:
        groups = await session.scalars(select(Group))
        for group in groups:
            await send_daily_report(bot, group.id, group.owner_id)

def setup_scheduler(bot):
    scheduler.add_job(hourly_stats_job, 'cron', minute=0)
    scheduler.add_job(daily_report_job, 'cron', hour=23, minute=59, args=[bot])
    scheduler.start()

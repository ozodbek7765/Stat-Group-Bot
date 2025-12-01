import datetime
from sqlalchemy import select, func
from app.db import AsyncSessionLocal
from app.models import Member, HourlyStat
from aiogram import Bot

async def update_hourly_stats(group_id):
    now = datetime.datetime.now(datetime.timezone.utc)
    hour = now.replace(minute=0, second=0, microsecond=0)
    async with AsyncSessionLocal() as session:
        joined_count = await session.scalar(
            select(func.count(Member.id)).where(
                Member.joined_at >= hour,
                Member.joined_at < hour + datetime.timedelta(hours=1),
                Member.group_id == group_id
            )
        )
        stat = await session.scalar(select(HourlyStat).where(HourlyStat.hour == hour, HourlyStat.group_id == group_id))
        if not stat:
            stat = HourlyStat(hour=hour, joined_count=joined_count or 0, group_id=group_id)
            session.add(stat)
        else:
            stat.joined_count = joined_count or 0
        await session.commit()

async def send_daily_report(bot: Bot, group_id, owner_id):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    start = datetime.datetime.combine(today, datetime.time.min, tzinfo=datetime.timezone.utc)
    end = datetime.datetime.combine(today, datetime.time.max, tzinfo=datetime.timezone.utc)
    async with AsyncSessionLocal() as session:
        joined_count = await session.scalar(
            select(func.count(Member.id)).where(
                Member.joined_at >= start,
                Member.joined_at <= end,
                Member.group_id == group_id
            )
        )
        left_count = await session.scalar(
            select(func.count(Member.id)).where(
                Member.left_at >= start,
                Member.left_at <= end,
                Member.group_id == group_id
            )
        )
        current_count = await session.scalar(
            select(func.count(Member.id)).where(
                Member.left_at == None,
                Member.group_id == group_id
            )
        )
        max_stat = await session.scalar(
            select(HourlyStat).where(
                HourlyStat.hour >= start,
                HourlyStat.hour <= end,
                HourlyStat.group_id == group_id
            ).order_by(HourlyStat.joined_count.desc())
        )
        min_stat = await session.scalar(
            select(HourlyStat).where(
                HourlyStat.hour >= start,
                HourlyStat.hour <= end,
                HourlyStat.group_id == group_id
            ).order_by(HourlyStat.joined_count.asc())
        )

        report = (
            f"Bugun guruhga qo‘shilganlar: {joined_count or 0} ta\n"
            f"Eng ko‘p qo‘shilgan soat: {max_stat.hour.strftime('%H:%M') if max_stat else '-'} — {max_stat.joined_count if max_stat else 0} ta\n"
            f"Eng kam qo‘shilgan soat: {min_stat.hour.strftime('%H:%M') if min_stat else '-'} — {min_stat.joined_count if min_stat else 0} ta\n"
            f"Guruhdan chiqqanlar soni: {left_count or 0} ta\n"
            f"Hozir guruhda bo‘lganlar: {current_count or 0} ta"
        )
        await bot.send_message(owner_id, report)

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter
from config import BOT_TOKEN, GROUP_ID
from .db import AsyncSessionLocal
from .models import Member, HourlyStat
import datetime
from sqlalchemy import select

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.chat_member(ChatMemberUpdatedFilter())
async def on_chat_member(event: ChatMemberUpdated):
    if event.chat.id != GROUP_ID:
        return

    user_id = event.from_user.id
    full_name = event.from_user.full_name
    now = datetime.datetime.utcnow()
    hour = now.replace(minute=0, second=0, microsecond=0)

    async with AsyncSessionLocal() as session:
        # JOIN
        if event.new_chat_member.status in ("member", "administrator"):
            member = Member(
                telegram_id=user_id,
                full_name=full_name,
                joined_at=now
            )
            session.add(member)
            stat = await session.scalar(
                select(HourlyStat).where(HourlyStat.hour == hour)
            )
            if not stat:
                stat = HourlyStat(hour=hour, joined_count=1)
                session.add(stat)
            else:
                stat.joined_count += 1
            await session.commit()

        # LEFT
        elif event.new_chat_member.status == "left":
            member = await session.scalar(
                select(Member)
                .where(Member.telegram_id == user_id, Member.left_at == None)
                .order_by(Member.joined_at.desc())
            )
            if member:
                member.left_at = now
                member.duration_in_group = now - member.joined_at
                await session.commit()

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ChatMemberUpdated as ChatMemberUpdatedType
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.db import AsyncSessionLocal, add_or_update_group
from app.models import Member, HourlyStat, Group


uzb_tz = timezone(timedelta(hours=5))



load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Salom! Botni o'z guruhingizga qo'shing. Bot har bir guruh uchun statistikani avtomatik yuritadi va sizga hisobot yuboradi."
    )

@dp.my_chat_member()
async def on_my_chat_member(event: ChatMemberUpdatedType):
    if event.new_chat_member.status in ("member", "administrator"):
        group_id = event.chat.id
        group_name = event.chat.title
        inviter = event.from_user
        owner_id = inviter.id
        owner_name = inviter.full_name

        async with AsyncSessionLocal() as session:
            await add_or_update_group(session, group_id, owner_id, group_name, owner_name)
        await bot.send_message(
            owner_id,
            f"Bot {group_name} guruhiga muvaffaqiyatli qo'shildi!\n"
            "Statistika yig'ish boshlandi. Siz har kuni guruh statistikasi haqida hisobot olasiz."
        )

@dp.chat_member()
async def on_chat_member(event: ChatMemberUpdatedType):
    if event.chat.type not in ("group", "supergroup"):
        return

    group_id = event.chat.id
    user_id = event.from_user.id
    full_name = event.from_user.full_name
    now = datetime.now(uzb_tz)
    hour = now.replace(minute=0, second=0, microsecond=0)

    async with AsyncSessionLocal() as session:
        group = await session.scalar(select(Group).where(Group.group_id == group_id))
        if not group or group.owner_id != user_id:
            return 

        # JOIN
        if event.new_chat_member.status in ("member", "administrator"):
            member = Member(
                telegram_id=user_id,
                full_name=full_name,
                joined_at=now,
                group_id=group_id
            )
            session.add(member)
            stat = await session.scalar(
                select(HourlyStat).where(HourlyStat.hour == hour, HourlyStat.group_id == group_id)
            )
            if not stat:
                stat = HourlyStat(hour=hour, joined_count=1, group_id=group_id)
                session.add(stat)
            else:
                stat.joined_count += 1
            await session.commit()

        # LEFT
        elif event.new_chat_member.status == "left":
            member = await session.scalar(
                select(Member)
                .where(Member.telegram_id == user_id, Member.left_at == None, Member.group_id == group_id)
                .order_by(Member.joined_at.desc())
            )
            if member:
                member.left_at = now
                member.duration_in_group = now - member.joined_at
                await session.commit()

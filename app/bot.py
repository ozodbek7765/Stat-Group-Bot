from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.chat_member_updated import ChatMemberUpdated
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
        "Salom! Botni o'z guruhingizga admin sifatida qo'shing va guruhingiz kunlik statistikasi haqida ma'lumot olishni boshlang. "
    )

@dp.chat_member(ChatMemberUpdated())
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
        is_owner = group and group.owner_id == user_id

        if event.new_chat_member.status in ["administrator", "creator"]:
            group_name = event.chat.title
            owner_name = event.from_user.full_name

            if not group:
                await add_or_update_group(session, group_id, user_id, group_name, owner_name)
                await bot.send_message(
                    user_id,
                    f"Bot {group_name} guruhiga muvaffaqiyatli qo'shildi va monitoring boshlandi!"
                )
            elif is_owner:
                await bot.send_message(
                    user_id,
                    f"Bot {group_name} guruhida monitoring davom etmoqda."
                )
            else:
                await bot.send_message(
                    user_id,
                    "Bot faqat guruh egasi uchun statistikani yuritadi.\n"
                    "Siz faqat o'zingiz egasi bo'lgan guruhlar uchun statistikani olishingiz mumkin."
                )
            return

        if not is_owner:
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

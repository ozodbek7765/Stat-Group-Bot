import datetime
from sqlalchemy import func, select
from .models import Member, HourlyStat

async def generate_daily_report(session):
    today = datetime.datetime.utcnow().date()
    tomorrow = today + datetime.timedelta(days=1)

    joined_count = await session.scalar(
        select(func.count()).select_from(Member)
        .where(Member.joined_at >= today, Member.joined_at < tomorrow)
    )
    left_count = await session.scalar(
        select(func.count()).select_from(Member)
        .where(Member.left_at >= today, Member.left_at < tomorrow)
    )
    in_group_count = await session.scalar(
        select(func.count()).select_from(Member)
        .where(Member.left_at == None)
    )
    stats = (await session.execute(
        select(HourlyStat.hour, HourlyStat.joined_count)
        .where(HourlyStat.hour >= today, HourlyStat.hour < tomorrow)
    )).all()
    if stats:
        max_hour, max_count = max(stats, key=lambda x: x[1])
        min_hour, min_count = min(stats, key=lambda x: x[1])
    else:
        max_hour = min_hour = None
        max_count = min_count = 0

    report = (
        f"Bugun guruhga qo‘shilganlar: {joined_count or 0} ta\n"
        f"Eng ko‘p qo‘shilgan soat: {max_hour.strftime('%H:00') if max_hour else '-'} — {max_count} ta\n"
        f"Eng kam qo‘shilgan soat: {min_hour.strftime('%H:00') if min_hour else '-'} — {min_count} ta\n"
        f"Guruhdan chiqqanlar soni: {left_count or 0} ta\n"
        f"Hozir guruhda bo‘lganlar: {in_group_count or 0} ta"
    )
    return report

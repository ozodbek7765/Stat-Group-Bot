from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.future import select
from app.models import Group, Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

async def add_or_update_group(session: AsyncSession, group_id: int, owner_id: int, group_name: str, owner_name: str):
    group = await session.scalar(select(Group).where(Group.group_id == group_id))
    if group:
        group.owner_id = owner_id
        group.group_name = group_name
        group.owner_name = owner_name
    else:
        group = Group(
            group_id=group_id,
            owner_id=owner_id,
            group_name=group_name,
            owner_name=owner_name
        )
        session.add(group)
    await session.commit()
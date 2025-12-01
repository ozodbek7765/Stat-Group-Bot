from sqlalchemy import Column, Integer, String, DateTime, Interval, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, unique=True, nullable=False)
    owner_id = Column(Integer, nullable=False)
    group_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    full_name = Column(String, nullable=False)
    joined_at = Column(DateTime, nullable=False)
    left_at = Column(DateTime)
    duration_in_group = Column(Interval)
    group_id = Column(Integer, ForeignKey("groups.group_id"), nullable=False)

class HourlyStat(Base):
    __tablename__ = "hourly_stats"
    id = Column(Integer, primary_key=True)
    hour = Column(DateTime, nullable=False)
    joined_count = Column(Integer, default=0)
    group_id = Column(Integer, ForeignKey("groups.group_id"), nullable=False)

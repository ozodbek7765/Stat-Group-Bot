from sqlalchemy import Column, String, DateTime, Interval, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    id = Column(BigInteger, primary_key=True)
    group_id = Column(BigInteger, unique=True, nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    group_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)

class Member(Base):
    __tablename__ = "members"
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    full_name = Column(String, nullable=False)
    joined_at = Column(DateTime, nullable=False)
    left_at = Column(DateTime)
    duration_in_group = Column(Interval)
    group_id = Column(BigInteger, ForeignKey("groups.group_id"), nullable=False)

class HourlyStat(Base):
    __tablename__ = "hourly_stats"
    id = Column(BigInteger, primary_key=True)
    hour = Column(DateTime, nullable=False)
    joined_count = Column(BigInteger, default=0)
    group_id = Column(BigInteger, ForeignKey("groups.group_id"), nullable=False)

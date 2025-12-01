from sqlalchemy import Column, BigInteger, String, DateTime, Interval, Integer
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    duration_in_group = Column(Interval, nullable=True)

class HourlyStat(Base):
    __tablename__ = "hourly_stats"
    id = Column(Integer, primary_key=True)
    hour = Column(DateTime, index=True, nullable=False)  # YYYY-MM-DD HH:00:00
    joined_count = Column(Integer, default=0, nullable=False)

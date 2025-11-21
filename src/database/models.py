"""数据模型：扩展艾宾浩斯字段+关联关系"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# 艾宾浩斯间隔单位枚举


class IntervalUnit(enum.Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    # 新增提醒配置
    enable_reminder = Column(Boolean, default=True)
    reminder_channel = Column(String(20), default="app")  # app/email

    # 关联复习计划
    review_schedules = relationship(
        "ReviewSchedule",
        backref="user",
        cascade="all, delete-orphan")


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    # 新增艾宾浩斯初始配置
    initial_interval = Column(Integer, default=1)  # 默认1天
    initial_interval_unit = Column(Enum(IntervalUnit), default=IntervalUnit.DAY)

    # 关联复习计划和记录
    review_schedules = relationship(
        "ReviewSchedule",
        backref="knowledge_item",
        cascade="all, delete-orphan")
    review_records = relationship(
        "ReviewRecord",
        backref="knowledge_item",
        cascade="all, delete-orphan")


class ReviewSchedule(Base):
    __tablename__ = "review_schedules"
    id = Column(Integer, primary_key=True)
    knowledge_item_id = Column(
        Integer,
        ForeignKey("knowledge_items.id"),
        nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)
    interval_index = Column(Integer, default=0)  # 艾宾浩斯阶段（0-6）
    current_interval = Column(Integer)
    current_interval_unit = Column(Enum(IntervalUnit))
    created_at = Column(DateTime, default=datetime.now)

    # 关联复习记录
    review_record = relationship("ReviewRecord", backref="schedule", uselist=False)


class ReviewRecord(Base):
    __tablename__ = "review_records"
    id = Column(Integer, primary_key=True)
    knowledge_item_id = Column(
        Integer,
        ForeignKey("knowledge_items.id"),
        nullable=False)
    schedule_id = Column(Integer, ForeignKey("review_schedules.id"))
    review_date = Column(DateTime, default=datetime.now)
    effectiveness = Column(Integer, nullable=False)  # 1-5分
    recall_score = Column(Float, nullable=False)  # 0-100
    notes = Column(Text)

    __table_args__ = {"sqlite_autoincrement": True}

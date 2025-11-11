"""
数据库模型定义
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户模型"""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class KnowledgeItem(Base):
    """知识点模型"""
    
    __tablename__ = 'knowledge_items'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)


class ReviewSchedule(Base):
    """复习计划模型"""
    
    __tablename__ = 'review_schedules'
    
    id = Column(Integer, primary_key=True)
    knowledge_item_id = Column(Integer, ForeignKey('knowledge_items.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)
    interval_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class ReviewRecord(Base):
    """复习记录模型"""
    
    __tablename__ = 'review_records'
    
    id = Column(Integer, primary_key=True)
    knowledge_item_id = Column(Integer, ForeignKey('knowledge_items.id'), nullable=False)
    review_date = Column(DateTime, nullable=False)
    effectiveness = Column(Integer)
    recall_score = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
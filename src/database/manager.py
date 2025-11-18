"""
数据库管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path="review_alarm.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)

        # 创建表
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """获取数据库会话"""
        return self.Session()

# -*- codeing =utf-8 -*-
# @Time : 2025/11/18 13:33
# @Author: Muncy
# @File : service.py.py
# @Software: PyCharm
"""
调度服务 - 成员C实现
"""

from datetime import datetime, timedelta
from src.database.manager import DatabaseManager
from src.database.models import ReviewSchedule, KnowledgeItem
from .algorithms import EbbinghausScheduler


class SchedulerService:
    """调度服务"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.algorithm = EbbinghausScheduler()

    def schedule_initial_review(self, knowledge_item_id: int, user_id: int):
        """安排初始复习计划"""
        session = self.db_manager.get_session()
        try:
            # 获取知识点
            knowledge_item = (
                session.query(KnowledgeItem)
                .filter(
                    KnowledgeItem.id == knowledge_item_id,
                    KnowledgeItem.user_id == user_id,
                )
                .first()
            )

            if not knowledge_item:
                raise ValueError("知识点不存在")

            # 计算复习时间表
            review_times = self.algorithm.calculate_review_schedule(
                knowledge_item.created_at
            )

            # 创建复习计划
            for i, review_time in enumerate(review_times):
                schedule = ReviewSchedule(
                    user_id=user_id,
                    knowledge_item_id=knowledge_item_id,
                    scheduled_date=review_time,
                    review_stage=i,
                )
                session.add(schedule)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_today_reviews(self, user_id: int) -> List[ReviewSchedule]:
        """获取今日需要复习的内容"""
        session = self.db_manager.get_session()
        try:
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)

            return (
                session.query(ReviewSchedule)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.scheduled_date >= today_start,
                    ReviewSchedule.scheduled_date < today_end,
                    ReviewSchedule.completed == False,
                )
                .all()
            )
        finally:
            session.close()

    def complete_review(
        self, schedule_id: int, recall_score: float, review_duration: int = None
    ):
        """完成复习"""
        session = self.db_manager.get_session()
        try:
            schedule = (
                session.query(ReviewSchedule)
                .filter(ReviewSchedule.id == schedule_id)
                .first()
            )
            if schedule:
                schedule.completed = True

                # 更新知识点的最后复习时间
                knowledge_item = (
                    session.query(KnowledgeItem)
                    .filter(KnowledgeItem.id == schedule.knowledge_item_id)
                    .first()
                )
                if knowledge_item:
                    knowledge_item.last_reviewed = datetime.now()

                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

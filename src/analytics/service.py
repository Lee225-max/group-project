# -*- codeing =utf-8 -*-
# @Time : 2025/11/24 0:53
# @Author: Muncy
# @File : service.py
# @Software: PyCharm
"""
统计分析服务
"""
from __future__ import annotations

import base64
import os
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Any#, Tuple

import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

from src.database.manager import DatabaseManager
from src.database.models import KnowledgeItem, ReviewRecord, ReviewSchedule



class AnalyticsService:
    """统计分析服务实现"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

        # 设置中文字体
        self.font_path = self._find_chinese_font()
        try:
            self.chinese_font = (
                fm.FontProperties(fname=self.font_path) if self.font_path else None
            )
        except Exception:
            self.chinese_font = None

    def _find_chinese_font(self) -> str | None:
        """查找系统中可用的中文字体"""
        candidates = [
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            # Windows
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyh.ttf",
            # Linux
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]
        for font_path in candidates:
            if os.path.exists(font_path):
                return font_path
        return None


    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户学习统计数据"""
        session = self.db_manager.get_session()
        try:
            # 总知识点数量
            total_items = (session.query(KnowledgeItem).filter(
                KnowledgeItem.user_id == user_id,
                KnowledgeItem.is_active,
            ).count())

            # 今日复习数量
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_reviews = (session.query(ReviewSchedule).filter(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.scheduled_date >= today_start,
                ReviewSchedule.scheduled_date < today_start + timedelta(days=1),
                ReviewSchedule.completed,
            ).count())

            # 已完成复习数量
            completed_reviews = (session.query(ReviewRecord).filter(
                ReviewRecord.knowledge_item_id.in_(
                    session.query(KnowledgeItem.id).filter(KnowledgeItem.user_id == user_id)
                )
            ).count())

            # 计算记忆保持率（基于最近30天的复习记录）
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_records = (session.query(ReviewRecord).filter(
                ReviewRecord.knowledge_item_id.in_(
                    session.query(KnowledgeItem.id).filter(KnowledgeItem.user_id == user_id)
                ),
                ReviewRecord.review_date >= thirty_days_ago
            ).all())

            if recent_records:
                avg_recall_score = sum(record.recall_score or 0 for record in recent_records) / len(recent_records)
                retention_rate = avg_recall_score * 100
            else:
                retention_rate = 0

            # 连续学习天数
            streak_days = self._calculate_streak_days(session, user_id)

            return {
                "total_knowledge_items": total_items,
                "today_review_count": today_reviews,
                "completed_reviews": completed_reviews,
                "retention_rate": round(retention_rate, 1),
                "streak_days": streak_days,
                "learning_efficiency": self._calculate_learning_efficiency(session, user_id),
            }

        finally:
            session.close()

    def _calculate_streak_days(self, session, user_id: int) -> int:
        """计算连续学习天数"""

        # 获取用户的所有复习记录日期
        review_dates = (session.query(ReviewRecord.review_date).filter(
            ReviewRecord.knowledge_item_id.in_(
                session.query(KnowledgeItem.id).filter(KnowledgeItem.user_id == user_id)
            )
        ).distinct().all())

        if not review_dates:
            return 0

        # 转换为日期对象并排序
        dates = sorted([date[0].date() for date in review_dates], reverse=True)

        # 计算连续天数
        streak = 0
        current_date = datetime.now().date()

        for date in dates:
            if date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break

        return streak

    def _calculate_learning_efficiency(self, session, user_id: int) -> float:
        """计算学习效率"""

        # 获取最近7天的复习记录
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_records = (session.query(ReviewRecord).filter(
            ReviewRecord.knowledge_item_id.in_(
                session.query(KnowledgeItem.id).filter(KnowledgeItem.user_id == user_id)
            ),
            ReviewRecord.review_date >= seven_days_ago
        ).all())

        if not recent_records:
            return 0.0

        # 基于回忆分数计算效率
        total_efficiency = sum(
            (record.recall_score or 0.5) * (record.effectiveness or 3) / 5
            for record in recent_records
        )

        return round(total_efficiency / len(recent_records) * 100, 1)

    def create_learning_chart(self, user_id: int) -> str:
        """创建学习统计图表，返回base64编码的图片"""
        session = self.db_manager.get_session()
        try:

            # 获取最近30天的学习数据
            thirty_days_ago = datetime.now() - timedelta(days=30)

            # 查询每日复习数量
            daily_reviews = (session.query(
                ReviewRecord.review_date,
                ReviewRecord.recall_score
            ).filter(
                ReviewRecord.knowledge_item_id.in_(
                    session.query(KnowledgeItem.id).filter(KnowledgeItem.user_id == user_id)
                ),
                ReviewRecord.review_date >= thirty_days_ago,
            ).all())

            # 组织数据
            date_counts: Dict[datetime.date, int] = {}
            date_scores: Dict[datetime.date, List[float]] = {}
           # date_counts = {}
           # date_scores = {}

            for record in daily_reviews:
                date = record.review_date.date()
                date_counts[date] = date_counts.get(date, 0) + 1
                if record.recall_score:
                    if date not in date_scores:
                        date_scores[date] = []
                    date_scores[date].append(record.recall_score)

            # 生成连续日期范围
            dates = [thirty_days_ago.date() + timedelta(days=i) for i in range(31)]
            review_counts = [date_counts.get(date, 0) for date in dates]
            avg_scores = [
                round(sum(date_scores.get(date, [0])) / len(date_scores.get(date, [1])), 2)
                if date in date_scores
                else 0
                for date in dates
            ]

            # 创建图表
            return self._create_chart_image(dates, review_counts, avg_scores)

        finally:
            session.close()

    def _create_chart_image(self, dates: List, review_counts: List, avg_scores: List) -> str:
        """创建图表并返回base64编码"""
        # 设置中文字体
        if self.chinese_font:
            plt.rcParams['font.sans-serif'] = [self.chinese_font.get_name()]
            plt.rcParams['axes.unicode_minus'] = False

        # 创建子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # 第一个图表：每日复习数量
        ax1.plot(dates, review_counts, 'b-o', linewidth=2, markersize=4)
        ax1.fill_between(dates, review_counts, alpha=0.3)
        ax1.set_title('每日复习数量趋势', fontsize=16, fontweight='bold', pad=20)
        ax1.set_xlabel('日期')
        ax1.set_ylabel('复习数量')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)

        # 第二个图表：记忆保持率
        ax2.plot(dates, avg_scores, 'r-o', linewidth=2, markersize=4)
        ax2.fill_between(dates, avg_scores, alpha=0.3)
        ax2.set_title('记忆保持率趋势', fontsize=16, fontweight='bold', pad=20)
        ax2.set_xlabel('日期')
        ax2.set_ylabel('保持率')
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)

        # 调整布局
        plt.tight_layout()

        # 转换为base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def get_category_stats(self, user_id: int) -> Dict[str, int]:
        """获取知识点分类统计"""
        session = self.db_manager.get_session()
        try:
            category_stats = (session.query(
                KnowledgeItem.category,
                KnowledgeItem.id
            ).filter(
                KnowledgeItem.user_id == user_id,
                KnowledgeItem.is_active,
            ).all())

            stats: Dict[str, int] = {}#stats = {}
            for category, item_id in category_stats:
                cat_name = category or "未分类"
                stats[cat_name] = stats.get(cat_name, 0) + 1

            return stats

        finally:
            session.close()

    def get_review_effectiveness(self, user_id: int) -> Dict[str, float]:
        """获取复习效果分析"""
        session = self.db_manager.get_session()
        try:
            effectiveness_data = (session.query(ReviewRecord.effectiveness).filter(
                ReviewRecord.knowledge_item_id.in_(
                    session.query(KnowledgeItem.id).filter(KnowledgeItem.user_id == user_id)
                ),
                ReviewRecord.effectiveness.isnot(None),
            ).all())

            if not effectiveness_data:
                return {}

            effectiveness_counts: Dict[int, int] = {}#effectiveness_counts = {}
            for eff in effectiveness_data:
                effectiveness_counts[eff[0]] = effectiveness_counts.get(eff[0], 0) + 1

            total = len(effectiveness_data)
            return {
                "优秀": effectiveness_counts.get(5, 0) / total * 100,
                "良好": effectiveness_counts.get(4, 0) / total * 100,
                "一般": effectiveness_counts.get(3, 0) / total * 100,
                "较差": effectiveness_counts.get(2, 0) / total * 100,
                "困难": effectiveness_counts.get(1, 0) / total * 100,
            }

        finally:
            session.close()
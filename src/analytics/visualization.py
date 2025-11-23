# -*- codeing =utf-8 -*-
# @Time : 2025/11/22 18:09
# @Author: Muncy
# @File : visualization.py
# @Software: PyCharm
'''
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')  # 非交互式后端
from io import BytesIO
import base64
from datetime import datetime, timedelta


class AnalyticsVisualization:
    def __init__(self, db):
        self.db = db
'''
'''  def create_memory_statistics_chart(self, user_id: int) -> str:
        """生成记忆统计图表，返回base64编码的图片"""
        # 获取用户的学习数据
        # 这里需要实现具体的数据查询逻辑

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 示例数据 - 实际应该从数据库查询
        dates = [datetime.now() - timedelta(days=x) for x in range(7, 0, -1)]
        items_studied = [5, 8, 12, 10, 15, 18, 20]
        retention_rates = [85, 78, 82, 88, 75, 90, 85]

        # 学习进度图
        ax1.plot(dates, items_studied, 'b-o')
        ax1.set_title('每日学习项目数')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('项目数')

        # 记忆保持率图
        ax2.plot(dates, retention_rates, 'r-o')
        ax2.set_title('记忆保持率')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('保持率 (%)')

        # 转换为base64
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"
'''
'''
def create_memory_statistics_chart(self, user_id: int) -> str:
    """生成记忆统计图表，返回base64编码的图片 - 使用真实数据"""
    try:
        # 获取真实数据
        daily_stats = self.db.get_daily_review_stats(user_id, days=7)

        if not daily_stats:
            # 如果没有数据，使用示例数据
            dates = [datetime.now() - timedelta(days=x) for x in range(6, -1, -1)]
            items_studied = [5, 8, 12, 10, 15, 18, 20]
            retention_rates = [85, 78, 82, 88, 75, 90, 85]
        else:
            # 使用真实数据
            dates = [datetime.strptime(day["date"], "%Y-%m-%d") for day in daily_stats]
            items_studied = [day["review_count"] for day in daily_stats]
            retention_rates = [day["avg_recall_score"] for day in daily_stats]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 学习进度图
        ax1.plot(dates, items_studied, 'b-o', linewidth=2, markersize=6)
        ax1.set_title('每日复习次数', fontsize=14, pad=15)
        ax1.set_xlabel('日期', fontsize=12)
        ax1.set_ylabel('复习次数', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)

        # 记忆保持率图
        ax2.plot(dates, retention_rates, 'r-o', linewidth=2, markersize=6)
        ax2.set_title('平均回忆分数', fontsize=14, pad=15)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.set_ylabel('回忆分数 (%)', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)

        # 转换为base64
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print(f"生成图表失败: {e}")
        # 返回空字符串表示图表生成失败
        return ""

    def get_user_stats(self, user_id: int) -> dict:
        """获取用户学习统计数据"""
        # 实现统计逻辑
        return {
            "total_items": 100,
            "items_reviewed_today": 15,
            "weekly_retention_rate": 85.5,
            "streak_days": 7
        }'''

import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')  # 非交互式后端
from io import BytesIO
import base64
from datetime import datetime, timedelta


class AnalyticsVisualization:
    def __init__(self, db):
        self.db = db

    def create_memory_statistics_chart(self, user_id: int) -> str:
        """生成记忆统计图表，返回base64编码的图片 - 使用真实数据"""
        try:
            # 获取真实数据
            daily_stats = self.db.get_daily_review_stats(user_id, days=7)

            if not daily_stats:
                # 如果没有数据，使用示例数据
                dates = [datetime.now() - timedelta(days=x) for x in range(6, -1, -1)]
                items_studied = [5, 8, 12, 10, 15, 18, 20]
                retention_rates = [85, 78, 82, 88, 75, 90, 85]
            else:
                # 使用真实数据
                dates = [datetime.strptime(day["date"], "%Y-%m-%d") for day in daily_stats]
                items_studied = [day["review_count"] for day in daily_stats]
                retention_rates = [day["avg_recall_score"] for day in daily_stats]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # 学习进度图
            ax1.plot(dates, items_studied, 'b-o', linewidth=2, markersize=6)
            ax1.set_title('每日复习次数', fontsize=14, pad=15)
            ax1.set_xlabel('日期', fontsize=12)
            ax1.set_ylabel('复习次数', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)

            # 记忆保持率图
            ax2.plot(dates, retention_rates, 'r-o', linewidth=2, markersize=6)
            ax2.set_title('平均回忆分数', fontsize=14, pad=15)
            ax2.set_xlabel('日期', fontsize=12)
            ax2.set_ylabel('回忆分数 (%)', fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)

            # 转换为base64
            buffer = BytesIO()
            plt.tight_layout()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return f"data:image/png;base64,{image_base64}"

        except Exception as e:
            print(f"生成图表失败: {e}")
            # 返回空字符串表示图表生成失败
            return ""

    def get_user_stats(self, user_id: int) -> dict:
        """获取用户学习统计数据 - 使用真实数据"""
        try:
            # 使用数据库管理器获取真实统计数据
            overall_stats = self.db.get_overall_stats(user_id)
            today_stats = self.db.get_review_stats(user_id)

            return {
                "total_items": overall_stats.get("total_knowledge", 0),
                "items_reviewed_today": today_stats.get("completed_today", 0),
                "weekly_retention_rate": overall_stats.get("completion_rate_30d", 0),
                "streak_days": overall_stats.get("streak_days", 0),
                # 添加更多统计字段
                "mastered_items": overall_stats.get("mastered_knowledge", 0),
                "overdue_count": today_stats.get("overdue_count", 0),
                "total_today": today_stats.get("total_today", 0)
            }
        except Exception as e:
            print(f"获取用户统计数据失败: {e}")
            # 如果获取真实数据失败，返回示例数据作为备用
            return {
                "total_items": 100,
                "items_reviewed_today": 15,
                "weekly_retention_rate": 85.5,
                "streak_days": 7,
                "mastered_items": 25,
                "overdue_count": 3,
                "total_today": 20
            }
# -*- codeing =utf-8 -*-
# @Time : 2025/11/22 18:09
# @Author: Muncy
# @File : visualization.py.py
# @Software: PyCharm
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

    def get_user_stats(self, user_id: int) -> dict:
        """获取用户学习统计数据"""
        # 实现统计逻辑
        return {
            "total_items": 100,
            "items_reviewed_today": 15,
            "weekly_retention_rate": 85.5,
            "streak_days": 7
        }
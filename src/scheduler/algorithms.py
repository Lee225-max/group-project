# -*- codeing =utf-8 -*-
# @Time : 2025/11/18 13:06
# @Author: Muncy
# @File : algorithms.py.py
# @Software: PyCharm
"""
记忆算法 - 成员C实现
"""
'''
from datetime import datetime, timedelta
from typing import List


class EbbinghausScheduler:
    """艾宾浩斯遗忘曲线调度器"""

    # 标准艾宾浩斯复习间隔（小时）
    REVIEW_INTERVALS = [1, 24, 24 * 2, 24 * 4, 24 * 7, 24 * 15, 24 * 30, 24 * 60]

    def calculate_review_schedule(
        self, first_study_time: datetime, recall_score: float = 1.0
    ) -> List[datetime]:
        """计算复习时间表"""
        base_intervals = self.REVIEW_INTERVALS

        # 根据回忆分数调整间隔
        adjusted_intervals = self.adjust_intervals_by_performance(
            base_intervals, recall_score
        )

        return [
            first_study_time + timedelta(hours=interval)
            for interval in adjusted_intervals
        ]

    def adjust_intervals_by_performance(
        self, intervals: List[int], recall_score: float
    ) -> List[int]:
        """根据回忆分数调整间隔"""
        adjustment_factor = self.get_adjustment_factor(recall_score)
        return [int(interval * adjustment_factor) for interval in intervals]

    def get_adjustment_factor(self, recall_score: float) -> float:
        """获取调整系数"""
        if recall_score >= 0.9:  # 记忆很好
            return 1.5
        elif recall_score >= 0.7:  # 记忆良好
            return 1.2
        elif recall_score >= 0.5:  # 记忆一般
            return 1.0
        elif recall_score >= 0.3:  # 记忆较差
            return 0.8
        else:  # 记忆很差
            return 0.6

    def get_next_review_time(
        self, last_review_time: datetime, current_stage: int, recall_score: float
    ) -> datetime:
        """获取下一次复习时间"""
        if current_stage >= len(self.REVIEW_INTERVALS):
            current_stage = len(self.REVIEW_INTERVALS) - 1

        base_interval = self.REVIEW_INTERVALS[current_stage]
        adjusted_interval = int(
            base_interval * self.get_adjustment_factor(recall_score)
        )

        return last_review_time + timedelta(hours=adjusted_interval)
'''

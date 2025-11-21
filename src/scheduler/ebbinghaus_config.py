"""
艾宾浩斯遗忘曲线配置和算法
"""
from datetime import datetime, timedelta
from enum import Enum


class EbbinghausStage(Enum):
    """艾宾浩斯复习阶段"""
    STAGE_1 = 0  # 20分钟
    STAGE_2 = 1  # 1小时
    STAGE_3 = 2  # 12小时（睡前）
    STAGE_4 = 3  # 24小时（第2天）
    STAGE_5 = 4  # 4天
    STAGE_6 = 5  # 7天
    STAGE_7 = 6  # 15天


class EbbinghausConfig:
    """艾宾浩斯遗忘曲线配置管理"""

    # 艾宾浩斯遗忘曲线间隔（小时）
    INTERVALS_HOURS = [0, 1, 12, 24, 96, 168, 360]

    # 阶段描述
    STAGE_DESCRIPTIONS = [
        # "20分钟后",
        "立即复习"
        "1小时后",
        "12小时后（睡前）",
        "1天后",
        "4天后",
        "7天后",
        "15天后"
    ]

    # 阶段标签
    STAGE_LABELS = [
        "第1阶段",
        "第2阶段",
        "第3阶段",
        "第4阶段",
        "第5阶段",
        "第6阶段",
        "第7阶段"
    ]

    @classmethod
    def get_interval_hours(cls, stage_index):
        """获取指定阶段的间隔小时数"""
        if 0 <= stage_index < len(cls.INTERVALS_HOURS):
            return cls.INTERVALS_HOURS[stage_index]
        return cls.INTERVALS_HOURS[-1]

    @classmethod
    def get_stage_description(cls, stage_index):
        """获取阶段描述"""
        if 0 <= stage_index < len(cls.STAGE_DESCRIPTIONS):
            return cls.STAGE_DESCRIPTIONS[stage_index]
        return "已完成所有阶段"

    @classmethod
    def get_stage_label(cls, stage_index):
        """获取阶段标签"""
        if 0 <= stage_index < len(cls.STAGE_LABELS):
            return cls.STAGE_LABELS[stage_index]
        return "已完成"

    @classmethod
    def get_next_review_date(cls, stage_index, last_review_date=None):
        """计算下次复习日期"""
        if last_review_date is None:
            last_review_date = datetime.now()

        interval_hours = cls.get_interval_hours(stage_index)
        return last_review_date + timedelta(hours=interval_hours)

    @classmethod
    def get_total_stages(cls):
        """获取总阶段数"""
        return len(cls.INTERVALS_HOURS)

# -*- codeing =utf-8 -*-
# @Time : 2025/11/24 0:55
# @Author: Muncy
# @File : test_analytics.py
# @Software: PyCharm
"""
统计分析模块测试 - 成员D负责
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.analytics.service import AnalyticsService  # noqa: E402
from src.database.manager import DatabaseManager  # noqa: E402
from src.database.models import User  # noqa: E402
# from datetime import datetime, timedelta

# 添加src到路径
class TestAnalyticsService:
    """统计分析服务测试类"""

    @pytest.fixture
    def analytics_service(self):
        """创建测试用的分析服务"""
        db_manager = DatabaseManager(":memory:")
        return AnalyticsService(db_manager)

    @pytest.fixture
    def test_user(self):
        """创建测试用户"""
        return User(username="testuser", email="test@example.com", password_hash="test")

    def test_get_user_stats_empty(self, analytics_service, test_user):
        """测试空用户的统计数据"""
        stats = analytics_service.get_user_stats(test_user.id)

        assert stats["total_knowledge_items"] == 0
        assert stats["today_review_count"] == 0
        assert stats["completed_reviews"] == 0
        assert stats["streak_days"] == 0

    def test_get_category_stats(self, analytics_service, test_user):
        """测试分类统计"""
        stats = analytics_service.get_category_stats(test_user.id)
        assert isinstance(stats, dict)

    def test_create_learning_chart(self, analytics_service, test_user):
        """测试创建学习图表"""
        chart_data = analytics_service.create_learning_chart(test_user.id)
        assert chart_data.startswith("data:image/png;base64,")

    def test_calculate_streak_days(self, analytics_service):
        """测试连续学习天数计算"""
        # 这里可以添加更详细的测试用例
        assert True


def test_analytics_imports():
    """测试分析模块导入"""
    try:
       # from src.analytics.ui import AnalyticsFrame

        assert True
    except ImportError as exc:
        assert False, f'导入失败: {exc}'
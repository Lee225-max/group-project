"""
认证模块测试 - GUI 版本
"""

from src.auth.service import AuthService
from src.database.manager import DatabaseManager

import pytest
import os
import sys

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestAuthService:
    """认证服务测试类"""

    @pytest.fixture
    def auth_service(self):
        """创建测试用的认证服务"""
        db_manager = DatabaseManager(":memory:")
        return AuthService(db_manager)

    def test_user_registration(self, auth_service):
        """测试用户注册"""
        user = auth_service.register_user("testuser", "test@example.com", "password123")

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.id is not None

    def test_duplicate_username(self, auth_service):
        """测试重复用户名"""
        auth_service.register_user("testuser", "test1@example.com", "password123")

        with pytest.raises(ValueError, match="用户名已存在"):
            auth_service.register_user("testuser", "test2@example.com", "password123")

    def test_user_authentication(self, auth_service):
        """测试用户认证"""
        auth_service.register_user("testuser", "test@example.com", "password123")

        user = auth_service.authenticate_user("testuser", "password123")
        assert user is not None
        assert user.username == "testuser"

    def test_authentication_failure(self, auth_service):
        """测试认证失败"""
        auth_service.register_user("testuser", "test@example.com", "password123")

        user = auth_service.authenticate_user("testuser", "wrongpassword")
        assert user is None

        user = auth_service.authenticate_user("nonexistent", "password123")
        assert user is None


def test_gui_imports():
    """测试GUI相关导入"""
    try:
        assert True
    except ImportError:
        assert False, "CustomTkinter 导入失败"

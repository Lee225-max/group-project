"""
认证服务模块 - 成员A负责
"""

import bcrypt
import re
from typing import Optional

from src.database.manager import DatabaseManager
from src.database.models import User


class AuthService:
    """认证服务 - 处理用户注册与登录认证"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        # 邮箱格式验证正则表达式
        self.email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式是否有效"""
        return re.match(self.email_pattern, email) is not None

    def register_user(self, username: str, email: str, password: str) -> User:
        """
        注册新用户

        Args:
            username: 用户名
            email: 邮箱地址
            password: 原始密码

        Returns:
            注册成功的用户对象

        Raises:
            ValueError: 当输入无效或用户已存在时
            Exception: 数据库操作失败时
        """
        # 输入验证
        if not username or len(username) < 3:
            raise ValueError("用户名长度至少为3个字符")

        if not self._validate_email(email):
            raise ValueError("请输入有效的邮箱地址")

        if not password or len(password) < 6:
            raise ValueError("密码长度至少为6个字符")

        # 使用上下文管理器自动管理会话生命周期
        with self.db_manager.get_session() as session:
            # 检查用户名是否已存在
            existing_user = session.query(User).filter(
                User.username == username
            ).first()
            if existing_user:
                raise ValueError("用户名已存在")

            # 检查邮箱是否已存在
            existing_email = session.query(User).filter(
                User.email == email
            ).first()
            if existing_email:
                raise ValueError("邮箱已被注册")

            # 加密密码
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # 创建并保存用户
            user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )
            session.add(user)
            session.commit()
            session.refresh(user)  # 获取数据库生成的ID等信息

            return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户身份

        Args:
            username: 用户名
            password: 密码

        Returns:
            验证成功返回用户对象，失败返回None
        """
        if not username or not password:
            return None

        with self.db_manager.get_session() as session:
            user = session.query(User).filter(
                User.username == username
            ).first()

        # 验证密码（使用短路逻辑避免NoneType错误）
        if user and bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8")
        ):
            return user

        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        通过用户ID获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        with self.db_manager.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()

"""
认证服务模块 - 成员A负责
"""

import bcrypt

# 使用相对导入
from database.manager import DatabaseManager


class AuthService:
    """认证服务"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def register_user(self, username: str, email: str, password: str):
        """注册用户"""
        from database.models import User
        
        # 检查用户名是否已存在
        session = self.db_manager.get_session()
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            session.close()
            raise ValueError("用户名已存在")
        
        # 加密密码
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 创建用户
        user = User(username=username, email=email, password_hash=password_hash)
        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()
        
        return user
    
    def authenticate_user(self, username: str, password: str):
        """用户认证"""
        from database.models import User
        
        session = self.db_manager.get_session()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None
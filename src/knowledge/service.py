"""
知识管理服务实现 - 成员B负责
"""

from datetime import datetime
from src.database.manager import DatabaseManager
from src.database.models import KnowledgeItem


class KnowledgeService:
    """知识管理服务"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add_knowledge_item(
        self, user_id: int, title: str, content: str, category: str = None
    ):
        """添加知识点"""
        session = self.db_manager.get_session()
        try:
            item = KnowledgeItem(
                user_id=user_id,
                title=title,
                content=content,
                category=category,
                created_at=datetime.now(),
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_knowledge_items(self, user_id: int):
        """获取用户的所有知识点"""
        session = self.db_manager.get_session()
        try:
            items = (
                session.query(KnowledgeItem)
                .filter(
                    KnowledgeItem.user_id == user_id, KnowledgeItem.is_active is True
                )
                .order_by(KnowledgeItem.created_at.desc())
                .all()
            )
            return items
        finally:
            session.close()

    def update_knowledge_item(
        self, item_id: int, title: str = None, content: str = None, category: str = None
    ):
        """更新知识点"""
        session = self.db_manager.get_session()
        try:
            item = (
                session.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
            )
            if item:
                if title is not None:
                    item.title = title
                if content is not None:
                    item.content = content
                if category is not None:
                    item.category = category
                session.commit()
                return item
            return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_knowledge_item(self, item_id: int):
        """删除知识点（软删除）"""
        session = self.db_manager.get_session()
        try:
            item = (
                session.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
            )
            if item:
                item.is_active = False
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def search_knowledge_items(self, user_id: int, search_term: str):
        """搜索知识点"""
        session = self.db_manager.get_session()
        try:
            items = (
                session.query(KnowledgeItem)
                .filter(
                    KnowledgeItem.user_id == user_id,
                    KnowledgeItem.is_active is True,
                    KnowledgeItem.title.ilike(f"%{search_term}%"),
                )
                .order_by(KnowledgeItem.created_at.desc())
                .all()
            )
            return items
        finally:
            session.close()

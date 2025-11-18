from src.database.models import KnowledgeItem


class KnowledgeService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def search_knowledge_items(self, user_id, search_term):
        """搜索知识点"""
        session = self.db_manager.get_session()
        try:
            print(f"🔍 在数据库中搜索: '{search_term}' - service.py:12")
            
            # 构建查询：修复 E712 错误（将 is True 改为直接判断）
            query = session.query(KnowledgeItem).filter(
                KnowledgeItem.user_id == user_id,
                KnowledgeItem.is_active  # 原错误：KnowledgeItem.is_active is True
            )
            
            # 添加搜索条件
            if search_term:
                search_filter = (
                    KnowledgeItem.title.ilike(f"%{search_term}%") | 
                    KnowledgeItem.content.ilike(f"%{search_term}%") |
                    KnowledgeItem.category.ilike(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            items = query.order_by(KnowledgeItem.created_at.desc()).all()
            print(f"📊 搜索到 {len(items)} 个结果 - service.py:30")
            return items
        except Exception as e:
            print(f"❌ 搜索出错: {e} - service.py:33")
            return []
        finally:
            session.close()

    def get_user_knowledge_items(self, user_id):
        """获取用户的知识点列表"""
        session = self.db_manager.get_session()
        try:
            # 修复 E712 错误（将 is True 改为直接判断）
            items = session.query(KnowledgeItem).filter(
                KnowledgeItem.user_id == user_id,
                KnowledgeItem.is_active  # 原错误：KnowledgeItem.is_active is True
            ).order_by(KnowledgeItem.created_at.desc()).all()
            print(f"📝 获取到 {len(items)} 个知识点 - service.py:47")
            return items
        except Exception as e:
            print(f"❌ 获取知识点列表出错: {e} - service.py:50")
            return []
        finally:
            session.close()

    def add_knowledge_item(self, user_id, title, content, category=None):
        """添加知识点"""
        session = self.db_manager.get_session()
        try:
            knowledge_item = KnowledgeItem(
                user_id=user_id,
                title=title,
                content=content,
                category=category,
                is_active=True
            )
            session.add(knowledge_item)
            session.commit()
            session.refresh(knowledge_item)
            print(f"✅ 添加知识点成功: {title} - service.py:69")
            return knowledge_item
        except Exception as e:
            session.rollback()
            print(f"❌ 添加知识点失败: {e} - service.py:73")
            raise e
        finally:
            session.close()

    def update_knowledge_item(self, item_id, title=None, content=None, category=None):
        """更新知识点"""
        session = self.db_manager.get_session()
        try:
            item = session.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
            if not item:
                raise ValueError("知识点不存在")
            
            if title is not None:
                item.title = title
            if content is not None:
                item.content = content
            if category is not None:
                item.category = category
                
            session.commit()
            print(f"✅ 更新知识点成功: {item.title} - service.py:94")
            return item
        except Exception as e:
            session.rollback()
            print(f"❌ 更新知识点失败: {e} - service.py:98")
            raise e
        finally:
            session.close()

    def delete_knowledge_item(self, item_id):
        """删除知识点"""
        session = self.db_manager.get_session()
        try:
            item = session.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
            if item:
                # 软删除
                item.is_active = False
                session.commit()
                print(f"✅ 删除知识点成功: {item.title} - service.py:112")
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ 删除知识点失败: {e} - service.py:117")
            raise e
        finally:
            session.close()

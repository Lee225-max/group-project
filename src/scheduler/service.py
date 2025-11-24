"""
调度器服务 - 完整实现版
"""

from datetime import datetime, timedelta
from src.database.models import ReviewSchedule  # 添加这行导入


class SchedulerService:
    """调度器服务 - 完整实现版"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def start_reminder(self):
        """启动提醒服务"""
        return {"success": True, "msg": "提醒服务已启动（占位符）"}

    def stop_reminder(self):
        """停止提醒服务"""
        return {"success": True, "msg": "提醒服务已停止（占位符）"}

    def get_today_reviews(self, user_id):
        """获取今日复习计划"""
        try:
            # 使用数据库管理器的方法获取今日复习计划
            reviews = self.db_manager.get_today_reviews(user_id)
            print(f"📅 调度器服务: 数据库管理器返回 {len(reviews)} 个今日复习计划 - service.py:28")
            # 详细打印每个复习计划的信息
            for i, review in enumerate(reviews):
                print(f"📋 复习计划 {i + 1}: - service.py:31")
                print(f"类型: {type(review)} - service.py:32")
                if isinstance(review, dict):
                    print(f"所有键: {list(review.keys())} - service.py:34")
                    for key, value in review.items():
                        print(f"{key}: {value} - service.py:36")
                else:
                    print(f"对象属性: {dir(review)} - service.py:38")
                    print(f"ID: {getattr(review, 'id', 'N/A')} - service.py:39")
                    print(f"知识点ID: {getattr(review , 'knowledge_item_id' , 'N/A')} - service.py:40")
                    print(f"标题: {getattr(review, 'title', 'N/A')} - service.py:41")

            return reviews
        except Exception as e:
            print(f"❌ 获取今日复习计划失败: {e} - service.py:45")
            import traceback
            traceback.print_exc()
            return []

    def complete_review(
            self,
            schedule_id,
            user_id,
            effectiveness,
            recall_score,
            notes=None):
        """完成复习"""
        try:
            # 使用数据库管理器的方法完成复习
            result = self.db_manager.complete_review(
                schedule_id, user_id, effectiveness, recall_score, notes
            )
            if result["success"]:
                print("✅ 复习完成成功 - service.py:64")
            else:
                print(f"❌ 复习完成失败: {result.get('msg', '未知错误')} - service.py:66")
            return result
        except Exception as e:
            print(f"❌ 完成复习失败: {e} - service.py:69")
            return {"success": False, "msg": f"完成复习失败: {str(e)}"}

    def get_review_stats(self, user_id):
        """获取复习统计"""
        try:
            # 使用数据库管理器的方法获取复习统计
            stats = self.db_manager.get_review_stats(user_id)
            print("📊 获取复习统计成功 - service.py:77")
            return stats
        except Exception:
            print("❌ 获取复习统计失败 - service.py:80")
            return {
                "total_today": 0,
                "completed_today": 0,
                "overdue_count": 0,
                "completion_rate": 0
            }

    def get_today_review_count(self, user_id):
        """获取今日复习数量"""
        try:
            count = self.db_manager.get_today_review_count(user_id)
            print(f"📅 今日复习数量: {count} - service.py:92")
            return count
        except Exception:
            print("❌ 获取今日复习数量失败 - service.py:95")
            return 0

    def get_overdue_reviews_count(self, user_id):
        """获取逾期复习数量"""
        try:
            count = self.db_manager.get_overdue_reviews_count(user_id)
            print(f"⏰ 逾期复习数量: {count} - service.py:102")
            return count
        except Exception:
            print("❌ 获取逾期复习数量失败 - service.py:105")
            return 0

    def get_ebbinghaus_distribution(self, user_id):
        """获取艾宾浩斯阶段分布"""
        try:
            distribution = self.db_manager.get_ebbinghaus_distribution(user_id)
            print("📈 获取艾宾浩斯分布成功 - service.py:112")
            return distribution
        except Exception:
            print("❌ 获取艾宾浩斯分布失败 - service.py:115")
            return {}

    def get_pending_reminders(self):
        """获取待发送提醒"""
        try:
            reminders = self.db_manager.get_pending_reminders()
            print(f"🔔 获取到 {len(reminders)} 个待发送提醒 - service.py:122")
            return reminders
        except Exception:
            print("❌ 获取待发送提醒失败 - service.py:125")
            return []

    def add_to_today_review(self, knowledge_id, user_id):
        """手动将知识点加入今日复习"""
        try:
            result = self.db_manager.add_to_today_review(knowledge_id, user_id)
            if result["success"]:
                print("✅ 成功将知识点加入今日复习 - service.py:133")
            else:
                print(f"❌ 加入今日复习失败: {result.get('msg', '未知错误')} - service.py:135")
            return result
        except Exception as e:
            print(f"❌ 加入今日复习失败: {e} - service.py:138")
            return {"success": False, "msg": f"加入今日复习失败: {str(e)}"}

    def get_overall_stats(self, user_id):
        """获取整体统计"""
        try:
            stats = self.db_manager.get_overall_stats(user_id)
            print("📊 获取整体统计成功 - service.py:145")
            return stats
        except Exception:
            print("❌ 获取整体统计失败 - service.py:148")
            return {
                "total_knowledge": 0,
                "mastered_knowledge": 0,
                "completion_rate_30d": 0,
                "streak_days": 0,
                "last_review_date": "暂无"
            }

    def get_daily_review_stats(self, user_id, days=7):
        """获取每日复习统计"""
        try:
            stats = self.db_manager.get_daily_review_stats(user_id, days)
            print(f"📅 获取 {days} 天复习统计成功 - service.py:161")
            return stats
        except Exception:
            print("❌ 获取每日复习统计失败 - service.py:164")
            return []

    def delay_review(self, schedule_id: int, delay_minutes: int = 20) -> bool:
        """延迟复习计划"""
        try:
            # 获取当前复习计划
            session = self.db_manager.get_session()
            current_schedule = session.query(ReviewSchedule).filter(
                ReviewSchedule.id == schedule_id
            ).first()
        
            if not current_schedule:
                print(f"❌ [DELAY DEBUG] 未找到复习计划: {schedule_id} - service.py:177")
                session.close()
                return False
        
            # 计算新的提醒时间（当前时间 + 延迟分钟）
            new_reminder_time = datetime.now() + timedelta(minutes=delay_minutes)
        
            # 更新复习计划的安排时间
            success = self.db_manager.update_review_schedule_time(schedule_id, new_reminder_time)
            
            session.close()  # 关闭会话
        
            if success:
                print(f"✅ [DELAY DEBUG] 已延迟复习计划 {schedule_id}，新的提醒时间: {new_reminder_time} - service.py:190")
                return True
            else:
                print(f"❌ [DELAY DEBUG] 延迟复习计划失败: {schedule_id} - service.py:193")
                return False
            
        except Exception as e:
            print(f"❌ [DELAY DEBUG] 延迟复习时出错: {e} - service.py:197")
            return False
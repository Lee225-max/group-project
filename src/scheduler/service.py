"""
调度器服务 - 完整实现版
"""


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
            print(f"📅 调度器服务: 数据库管理器返回 {len(reviews)} 个今日复习计划 - service.py:25")
            # 详细打印每个复习计划的信息
            for i, review in enumerate(reviews):
                print(f"📋 复习计划 {i + 1}: - service.py:28")
                print(f"类型: {type(review)} - service.py:29")
                if isinstance(review, dict):
                    print(f"所有键: {list(review.keys())} - service.py:31")
                    for key, value in review.items():
                        print(f"{key}: {value} - service.py:33")
                else:
                    print(f"对象属性: {dir(review)} - service.py:35")
                    print(f"ID: {getattr(review, 'id', 'N/A')} - service.py:36")
                    print(
                        f"知识点ID: {
                            getattr(
                                review,
                                'knowledge_item_id',
                                'N/A')} - service.py:37")
                    print(f"标题: {getattr(review, 'title', 'N/A')} - service.py:38")

            return reviews
        except Exception as e:
            print(f"❌ 获取今日复习计划失败: {e} - service.py:42")
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
                print("✅ 复习完成成功 - service.py:56")
            else:
                print(f"❌ 复习完成失败: {result.get('msg', '未知错误')} - service.py:58")
            return result
        except Exception as e:
            print(f"❌ 完成复习失败: {e} - service.py:61")
            return {"success": False, "msg": f"完成复习失败: {str(e)}"}

    def get_review_stats(self, user_id):
        """获取复习统计"""
        try:
            # 使用数据库管理器的方法获取复习统计
            stats = self.db_manager.get_review_stats(user_id)
            print("📊 获取复习统计成功 - service.py:69")
            return stats
        except Exception:
            print("❌ 获取复习统计失败 - service.py:72")
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
            print(f"📅 今日复习数量: {count} - service.py:84")
            return count
        except Exception:
            print("❌ 获取今日复习数量失败 - service.py:87")
            return 0

    def get_overdue_reviews_count(self, user_id):
        """获取逾期复习数量"""
        try:
            count = self.db_manager.get_overdue_reviews_count(user_id)
            print(f"⏰ 逾期复习数量: {count} - service.py:94")
            return count
        except Exception:
            print("❌ 获取逾期复习数量失败 - service.py:97")
            return 0

    def get_ebbinghaus_distribution(self, user_id):
        """获取艾宾浩斯阶段分布"""
        try:
            distribution = self.db_manager.get_ebbinghaus_distribution(user_id)
            print("📈 获取艾宾浩斯分布成功 - service.py:104")
            return distribution
        except Exception:
            print("❌ 获取艾宾浩斯分布失败 - service.py:107")
            return {}

    def get_pending_reminders(self):
        """获取待发送提醒"""
        try:
            reminders = self.db_manager.get_pending_reminders()
            print(f"🔔 获取到 {len(reminders)} 个待发送提醒 - service.py:114")
            return reminders
        except Exception:
            print("❌ 获取待发送提醒失败 - service.py:117")
            return []

    def add_to_today_review(self, knowledge_id, user_id):
        """手动将知识点加入今日复习"""
        try:
            result = self.db_manager.add_to_today_review(knowledge_id, user_id)
            if result["success"]:
                print("✅ 成功将知识点加入今日复习 - service.py:125")
            else:
                print(f"❌ 加入今日复习失败: {result.get('msg', '未知错误')} - service.py:127")
            return result
        except Exception as e:
            print(f"❌ 加入今日复习失败: {e} - service.py:130")
            return {"success": False, "msg": f"加入今日复习失败: {str(e)}"}

    def get_overall_stats(self, user_id):
        """获取整体统计"""
        try:
            stats = self.db_manager.get_overall_stats(user_id)
            print("📊 获取整体统计成功 - service.py:137")
            return stats
        except Exception:
            print("❌ 获取整体统计失败 - service.py:140")
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
            print(f"📅 获取 {days} 天复习统计成功 - service.py:153")
            return stats
        except Exception:
            print("❌ 获取每日复习统计失败 - service.py:156")
            return []

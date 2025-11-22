"""数据库管理器：增强业务逻辑+艾宾浩斯核心算法"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .models import (
    Base,
    User,
    KnowledgeItem,
    ReviewSchedule,
    ReviewRecord,
    IntervalUnit,
)
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_path="src/database/review_alarm.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)  # 自动创建表

    def get_session(self):
        """获取数据库会话"""
        return self.Session()

    # ------------------------------
    # 知识管理相关（供knowledge模块调用）
    # ------------------------------
    def add_knowledge(self, user_id, title, content, category=None):
        """新增知识点+自动生成首次复习计划"""
        session = self.get_session()
        try:
            print(f"🔍 [ADD DEBUG] 开始添加知识点: {title}, 用户: {user_id} - manager.py:34")

            # 检查重复知识点
            existing = (
                session.query(KnowledgeItem)
                .filter(
                    KnowledgeItem.user_id == user_id,
                    KnowledgeItem.title == title.strip(),
                )
                .first()
            )
            if existing:
                print(f"❌ [ADD DEBUG] 知识点已存在: {title} - manager.py:46")
                return {"success": False, "msg": "知识点标题已存在"}

            # 创建知识点
            item = KnowledgeItem(
                user_id=user_id,
                title=title.strip(),
                content=content.strip(),
                category=category,
            )
            session.add(item)
            session.flush()  # 获取item.id
            print(f"✅ [ADD DEBUG] 知识点创建成功, ID: {item.id} - manager.py:58")

            # 使用艾宾浩斯间隔生成首次复习计划
            from src.scheduler.ebbinghaus_config import EbbinghausConfig

            first_interval_hours = EbbinghausConfig.get_interval_hours(0)  # 第1阶段

            print(f"📅 [ADD DEBUG] 复习间隔: {first_interval_hours} 小时 - manager.py:65")

            scheduled_date = datetime.now() + timedelta(hours=first_interval_hours)

            first_schedule = ReviewSchedule(
                knowledge_item_id=item.id,
                user_id=user_id,
                scheduled_date=scheduled_date,
                interval_index=0,
                current_interval=first_interval_hours,
                current_interval_unit=IntervalUnit.HOUR,
            )
            session.add(first_schedule)
            print(
                f"[ADD DEBUG] 复习计划创建: 知识点ID={item.id}, 时间={scheduled_date}"
            )
            session.commit()
            print("✅ [ADD DEBUG] 数据库提交成功 - manager.py:82")
            return {
                "success": True,
                "data": {
                    "knowledge_id": item.id,
                    "first_schedule_id": first_schedule.id,
                },
            }
        except Exception as e:
            print(f"❌ [ADD DEBUG] 添加失败: {str(e)} - manager.py:91")
            session.rollback()
            return {"success": False, "msg": f"新增失败：{str(e)}"}
        finally:
            session.close()

    def get_knowledge_with_review_status(self, user_id):
        """获取用户所有知识点（含复习状态）"""
        session = self.get_session()
        try:
            print(f"🔍 [DEBUG] 开始查询用户 {user_id} 的知识点 - manager.py:101")

            knowledges = (
                session.query(KnowledgeItem)
                .filter(KnowledgeItem.user_id == user_id, KnowledgeItem.is_active)
                .order_by(KnowledgeItem.created_at.desc())
                .all()
            )

            print(f"🔍 [DEBUG] 数据库查询结果: {len(knowledges)} 个知识点 - manager.py:110")

            result = []
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)

            print(f"🔍 [DEBUG] 今日时间范围: {today_start} 到 {today_end} - manager.py:118")
            from src.scheduler.ebbinghaus_config import EbbinghausConfig

            for item in knowledges:
                print(f"🔍 [DEBUG] 处理知识点: {item.title} (ID: {item.id}) - manager.py:122")

                # 检查复习计划
                schedules = (
                    session.query(ReviewSchedule)
                    .filter(ReviewSchedule.knowledge_item_id == item.id)
                    .all()
                )
                print(f"关联的复习计划数量: {len(schedules)} - manager.py:130")

                for s in schedules:
                    print(f"计划 {s.id}: 时间={s.scheduled_date}, 完成={s.completed} - manager.py:133")

                # 检查是否今日复习
                today_schedule = (
                    session.query(ReviewSchedule)
                    .filter(
                        ReviewSchedule.knowledge_item_id == item.id,
                        ~ReviewSchedule.completed,  # 修复：使用 == 而不是 is
                        ReviewSchedule.scheduled_date >= today_start,
                        ReviewSchedule.scheduled_date < today_end,
                    )
                    .first()
                )

                print(f"今日复习计划: {today_schedule} - manager.py:147")

                # 检查是否完成所有阶段
                last_schedule = (
                    session.query(ReviewSchedule)
                    .filter(ReviewSchedule.knowledge_item_id == item.id)
                    .order_by(ReviewSchedule.interval_index.desc())
                    .first()
                )

                is_completed_all = (
                    last_schedule.interval_index == 6 and last_schedule.completed
                    if last_schedule
                    else False
                )

                # 构建状态描述
                if is_completed_all:
                    status = "✅ 已掌握"
                elif today_schedule:
                    stage_desc = EbbinghausConfig.get_stage_description(
                        today_schedule.interval_index
                    )
                    status = f"📅 今日复习（{stage_desc}）"
                else:
                    next_schedule = (
                        session.query(ReviewSchedule)
                        .filter(
                            ReviewSchedule.knowledge_item_id == item.id,
                            ~ReviewSchedule.completed,
                        )
                        .order_by(ReviewSchedule.scheduled_date)
                        .first()
                    )
                    if next_schedule:
                        days_diff = (next_schedule.scheduled_date - datetime.now()).days
                        stage_desc = EbbinghausConfig.get_stage_description(
                            next_schedule.interval_index
                        )
                        status = f"⏳ 待复习（{days_diff}天后，{stage_desc}）"
                    else:
                        status = "❌ 无复习计划"

                result.append(
                    {
                        "id": item.id,
                        "title": item.title,
                        "category": item.category,
                        "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "last_reviewed": (
                            item.review_records[-1].review_date.strftime("%Y-%m-%d")
                            if item.review_records
                            else "暂无"
                        ),
                        "review_status": status,
                        "is_today_review": True if today_schedule else False,
                    }
                )

            print(f"🔍 [DEBUG] 最终返回 {len(result)} 个知识点 - manager.py:206")
            return result
        except Exception as e:
            print(f"❌ [DEBUG] 查询出错: {e} - manager.py:209")
            raise
        finally:
            session.close()

    # ------------------------------
    # 今日复习相关（供scheduler/knowledge模块调用）
    # ------------------------------
    def get_today_reviews(self, user_id):
        """获取用户今日待复习计划"""
        session = self.get_session()
        try:
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)

            print(f"🔍 [TODAY DEBUG] 查询用户 {user_id} 的今日复习计划 - manager.py:226")

            schedules = (
                session.query(ReviewSchedule, KnowledgeItem)
                .join(
                    KnowledgeItem, ReviewSchedule.knowledge_item_id == KnowledgeItem.id
                )
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ~ReviewSchedule.completed,
                    ReviewSchedule.scheduled_date >= today_start,
                    ReviewSchedule.scheduled_date < today_end,
                )
                .order_by(ReviewSchedule.scheduled_date)
                .all()
            )

            print(f"🔍 [TODAY DEBUG] 找到 {len(schedules)} 个今日复习计划 - manager.py:243")

            result = []
            from src.scheduler.ebbinghaus_config import EbbinghausConfig

            for schedule, item in schedules:
                stage_label = EbbinghausConfig.get_stage_label(schedule.interval_index)
                stage_desc = EbbinghausConfig.get_stage_description(
                    schedule.interval_index
                )

                result.append(
                    {
                        "schedule_id": schedule.id,
                        "knowledge_id": item.id,
                        "title": item.title,
                        "content": item.content,
                        "scheduled_time": schedule.scheduled_date.strftime("%H:%M"),
                        "stage_label": stage_label,
                        "stage_desc": stage_desc,
                        "interval_index": schedule.interval_index,
                        "scheduled_date": schedule.scheduled_date,
                    }
                )
            return result
        except Exception as e:
            print(f"❌ [TODAY DEBUG] 查询出错: {e} - manager.py:269")
            raise
        finally:
            session.close()

    def get_today_review_count(self, user_id):
        """获取今日待复习数量"""
        session = self.get_session()
        try:
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)

            count = (
                session.query(ReviewSchedule)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ~ReviewSchedule.completed,
                    ReviewSchedule.scheduled_date >= today_start,
                    ReviewSchedule.scheduled_date < today_end,
                )
                .count()
            )

            print(f"🔍 [COUNT DEBUG] 用户 {user_id} 今日复习数量: {count} - manager.py:294")
            return count
        finally:
            session.close()

    def get_overdue_reviews_count(self, user_id):
        """获取逾期复习数量"""
        session = self.get_session()
        try:
            count = (
                session.query(ReviewSchedule)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ~ReviewSchedule.completed,
                    ReviewSchedule.scheduled_date < datetime.now(),
                )
                .count()
            )
            return count
        finally:
            session.close()

    def get_review_stats(self, user_id):
        """获取今日复习统计"""
        session = self.get_session()
        try:
            from datetime import datetime, timedelta

            # 今日统计
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)

            total_today = (
                session.query(ReviewSchedule)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.scheduled_date >= today_start,
                    ReviewSchedule.scheduled_date < today_end,
                )
                .count()
            )

            completed_today = (
                session.query(ReviewSchedule)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.completed,  # 修复：使用 == 而不是 is
                    ReviewSchedule.scheduled_date >= today_start,
                    ReviewSchedule.scheduled_date < today_end,
                )
                .count()
            )

            overdue_count = self.get_overdue_reviews_count(user_id)

            return {
                "total_today": total_today,
                "completed_today": completed_today,
                "overdue_count": overdue_count,
                "completion_rate": round(
                    (completed_today / total_today * 100) if total_today > 0 else 0, 1
                ),
            }
        finally:
            session.close()

 # 整个改了
    class DatabaseManager:
        # 原有方法：__init__（数据库连接初始化）
        def __init__(self, db_path="review_app.db"):
            self.db_path = db_path
            self._init_db()  # 假设原有初始化数据库方法

        # 原有方法：complete_review（你已有的复习完成逻辑）
        def complete_review(self, schedule_id, user_id, effectiveness, recall_score, notes=None):
            # 你的原有代码（验证计划、创建记录、生成下次复习）
            ...  # 这是你已有的逻辑，保持不变
            # （complete_review方法结束，下面就是要新增的方法）

        # ========== 从这里开始粘贴新增的统计查询方法 ==========
        def get_total_review_schedules(self, user_id):
            """查询用户总复习计划数"""
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM review_schedules WHERE user_id = ?
                """, (user_id,))
                return cursor.fetchone()[0]

        def get_completed_review_schedules(self, user_id):
            """查询用户已完成的复习计划数"""
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM review_schedules WHERE user_id = ? AND is_completed = 1
                """, (user_id,))
                return cursor.fetchone()[0]

        def get_reviews_in_date_range(self, user_id, start_date, end_date):
            """查询指定日期范围内的复习次数"""
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM review_records 
                    WHERE user_id = ? AND review_date BETWEEN ? AND ?
                """, (user_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
                return cursor.fetchone()[0]

        def get_avg_review_effectiveness(self, user_id):
            """查询用户平均复习效果分"""
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT AVG(effectiveness) FROM review_records WHERE user_id = ?
                """, (user_id,))
                result = cursor.fetchone()[0]
                return result if result is not None else 0.0

        def get_knowledge_review_stats(self, user_id):
            """查询各知识点的复习统计（次数+平均效果）"""
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT k.id, k.title, COUNT(r.id) as review_count, AVG(r.effectiveness) as avg_effect
                    FROM knowledge_items k
                    LEFT JOIN review_schedules s ON k.id = s.knowledge_item_id
                    LEFT JOIN review_records r ON s.id = r.schedule_id
                    WHERE k.user_id = ?
                    GROUP BY k.id, k.title
                """, (user_id,))
                return [
                    {
                        "knowledge_id": row[0],
                        "title": row[1],
                        "review_count": row[2],
                        "avg_effect": round(row[3], 1) if row[3] is not None else 0.0
                    }
                    for row in cursor.fetchall()
                ]
        # ========== 新增方法结束 ==========

    # （DatabaseManager类结束）

    # ------------------------------
    # 统计相关（供analytics模块调用）
    # ------------------------------
    def get_ebbinghaus_stats(self, user_id):
        """获取各艾宾浩斯阶段知识点数量"""
        session = self.get_session()
        try:
            stats = (
                session.query(
                    ReviewSchedule.interval_index, func.count(ReviewSchedule.id)
                )
                .filter(ReviewSchedule.user_id == user_id, ~ReviewSchedule.completed)
                .group_by(ReviewSchedule.interval_index)
                .all()
            )
            return dict(stats)
        finally:
            session.close()

    def get_ebbinghaus_distribution(self, user_id):
        """获取艾宾浩斯阶段分布（详细版）"""
        session = self.get_session()
        try:
            from src.scheduler.ebbinghaus_config import EbbinghausConfig

            # 获取未完成的复习计划按阶段分组
            stage_stats = (
                session.query(
                    ReviewSchedule.interval_index, func.count(ReviewSchedule.id)
                )
                .filter(ReviewSchedule.user_id == user_id, ~ReviewSchedule.completed)
                .group_by(ReviewSchedule.interval_index)
                .all()
            )

            distribution = {}
            total_stages = EbbinghausConfig.get_total_stages()

            # 初始化所有阶段
            for stage in range(total_stages):
                distribution[stage] = {
                    "count": 0,
                    "label": EbbinghausConfig.get_stage_label(stage),
                    "description": EbbinghausConfig.get_stage_description(stage),
                }

            # 填充实际数据
            for stage, count in stage_stats:
                if stage in distribution:
                    distribution[stage]["count"] = count

            return distribution
        finally:
            session.close()

    def get_daily_review_stats(self, user_id, days=7):
        """获取近N天复习效果统计"""
        session = self.get_session()
        try:
            start_date = datetime.now() - timedelta(days=days)
            stats = (
                session.query(
                    func.date(ReviewRecord.review_date),
                    func.avg(ReviewRecord.recall_score),
                    func.count(ReviewRecord.id),
                )
                .join(KnowledgeItem, ReviewRecord.knowledge_item_id == KnowledgeItem.id)
                .filter(
                    KnowledgeItem.user_id == user_id,
                    ReviewRecord.review_date >= start_date,
                )
                .group_by(func.date(ReviewRecord.review_date))
                .all()
            )

            # 格式化数据：日期、平均分数、复习次数
            result = []
            for date_str, avg_score, count in stats:
                result.append(
                    {
                        "date": date_str,
                        "avg_recall_score": round(avg_score, 1) if avg_score else 0,
                        "review_count": count,
                    }
                )
            return result
        finally:
            session.close()

    def get_overall_stats(self, user_id):
        """获取整体统计概览"""
        session = self.get_session()
        try:
            # 知识点统计
            total_knowledge = (
                session.query(KnowledgeItem)
                .filter(KnowledgeItem.user_id == user_id, KnowledgeItem.is_active)
                .count()
            )

            # 已掌握知识点（完成所有7阶段）
            mastered_ids = (
                session.query(ReviewSchedule.knowledge_item_id)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.interval_index == 6,
                    ReviewSchedule.completed,
                )
                .distinct()
                .all()
            )
            mastered_count = len(mastered_ids)

            # 30天复习完成率
            thirty_days_ago = datetime.now() - timedelta(days=30)
            total_scheduled = (
                session.query(ReviewSchedule)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.scheduled_date >= thirty_days_ago,
                )
                .count()
            )
            completed_scheduled = (
                session.query(ReviewSchedule)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.scheduled_date >= thirty_days_ago,
                    ReviewSchedule.completed,
                )
                .count()
            )
            completion_rate = (
                (completed_scheduled / total_scheduled) * 100
                if total_scheduled > 0
                else 0
            )

            # 连续复习天数
            completed_dates = (
                session.query(func.date(ReviewRecord.review_date))
                .filter(ReviewRecord.knowledge_item.has(user_id=user_id))
                .distinct()
                .order_by(func.date(ReviewRecord.review_date).desc())
                .all()
            )
            streak_days = 0
            if completed_dates:
                current_date = datetime.now().date()
                for idx, (date_str,) in enumerate(completed_dates):
                    record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if (current_date - record_date).days == idx:
                        streak_days += 1
                    else:
                        break

            # 今日复习统计
            today_stats = self.get_review_stats(user_id)

            return {
                "total_knowledge": total_knowledge,
                "mastered_knowledge": mastered_count,
                "completion_rate_30d": round(completion_rate, 1),
                "streak_days": streak_days,
                "last_review_date": (
                    completed_dates[0][0] if completed_dates else "暂无"
                ),
                "today_stats": today_stats,
                "ebbinghaus_distribution": self.get_ebbinghaus_distribution(user_id),
            }
        finally:
            session.close()

    # ------------------------------
    # 提醒相关（供scheduler模块调用）
    # ------------------------------
    def get_pending_reminders(self):
        """获取1小时内需要提醒的计划"""
        session = self.get_session()
        try:
            soon = datetime.now() + timedelta(hours=1)
            plans = (
                session.query(ReviewSchedule, KnowledgeItem, User)
                .join(
                    KnowledgeItem, ReviewSchedule.knowledge_item_id == KnowledgeItem.id
                )
                .join(User, ReviewSchedule.user_id == User.id)
                .filter(
                    ~ReviewSchedule.completed,
                    ReviewSchedule.scheduled_date <= soon,
                    User.enable_reminder,
                )
                .all()
            )

            result = []
            for schedule, item, user in plans:
                result.append(
                    {
                        "schedule_id": schedule.id,
                        "user_id": user.id,
                        "user_email": user.email,
                        "knowledge_title": item.title,
                        "scheduled_date": schedule.scheduled_date.strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "reminder_channel": user.reminder_channel,
                        "interval_index": schedule.interval_index,
                    }
                )
            return result
        finally:
            session.close()

    def add_to_today_review(self, knowledge_id, user_id):
        """手动将知识点加入今日复习"""
        session = self.get_session()
        try:
            # 检查知识点是否存在
            knowledge = (
                session.query(KnowledgeItem)
                .filter(
                    KnowledgeItem.id == knowledge_id, KnowledgeItem.user_id == user_id
                )
                .first()
            )

            if not knowledge:
                return {"success": False, "msg": "知识点不存在"}

            # 创建今日的复习计划
            # today_end = datetime.now().replace(hour=23, minute=59, second=59)

            today_schedule = ReviewSchedule(
                knowledge_item_id=knowledge_id,
                user_id=user_id,
                scheduled_date=datetime.now() + timedelta(hours=1),  # 1小时后复习
                interval_index=0,  # 从第一阶段开始
                current_interval=1,
                current_interval_unit=IntervalUnit.HOUR,
            )

            session.add(today_schedule)
            session.commit()

            return {
                "success": True,
                "msg": "已成功加入今日复习计划",
                "data": {"schedule_id": today_schedule.id},
            }

        except Exception as e:
            session.rollback()
            return {"success": False, "msg": f"加入今日复习失败：{str(e)}"}
        finally:
            session.close()
